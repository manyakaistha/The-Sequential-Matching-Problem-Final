"""Fixed two-family, seed-grouped public model fit and honest prediction gates."""
import hashlib,json
from pathlib import Path
import numpy as np
from .features import feature_names
from .models import fit_logistic,predict
from research8.soft_query_followup.v2.registration import ROOT,write_once,file_sha256
BASE=ROOT/'research9/final_campaign'

def balanced_weights(cells):
    _,inverse,counts=np.unique(cells,return_inverse=True,return_counts=True)
    return 1./counts[inverse]

def losses(y,p):
    p=np.clip(p,1e-6,1-1e-6)
    return -(y*np.log(p)+(1-y)*np.log1p(-p))

def metrics(y,p,w,groups,control_p=None):
    p=np.clip(p,1e-6,1-1e-6);w=w/w.sum()
    result=dict(rows=len(y),positives=int(y.sum()),log_loss=float(w@losses(y,p)),brier=float(w@((y-p)**2)),calibration_mean_error=float(abs(w@(p-y))))
    boundaries=[0,.005,.01,.02,.05,1.000001]
    result['reliability']=[]
    for lo,hi in zip(boundaries,boundaries[1:]):
        mask=(p>=lo)&(p<hi);ww=w[mask]
        result['reliability'].append(dict(lower=lo,upper=hi,n=int(mask.sum()),positives=int(y[mask].sum()),mean_prediction=float(np.average(p[mask],weights=ww)) if ww.sum() else None,observed_rate=float(np.average(y[mask],weights=ww)) if ww.sum() else None))
    if control_p is not None:
        delta=losses(y,p)-losses(y,control_p)
        per_seed=np.array([np.average(delta[groups==s],weights=w[groups==s]) for s in np.unique(groups)])
        rng=np.random.default_rng(9139)
        draws=per_seed[rng.integers(0,len(per_seed),size=(2000,len(per_seed)))].mean(axis=1)
        result['constant_loss_difference']=float(per_seed.mean());result['bootstrap95_upper_difference']=float(np.quantile(draws,.975))
    return result

def asset_predict(asset,X):
    p=np.ones(len(X))
    for model in asset['models']:p*=predict(model,X)
    return np.clip(p,1e-6,1-1e-6)

def main():
    ready=json.loads((BASE/'dataset_ready.json').read_text());assert ready['status']=='complete' and ready['cells']==2880
    for rel,value in ready['sources'].items():assert file_sha256(ROOT/rel)==value
    split=json.loads((BASE/'split.json').read_text())
    historical=json.loads((ROOT/'research8/soft_query_followup/storage_recovery/continuation_registration.json').read_text())
    sets=[set(split[k]) for k in ('train','validation','development_test')]
    assert list(map(len,sets))==[64,16,16] and len(set.union(*sets))==96 and set.union(*sets)==set(historical['ordered_seed_list'])
    assert not (sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2])
    paths=sorted(Path(ready['dataset']).glob('*.npz'));assert len(paths)==2880
    expected={c['cell_key']:c for c in historical['cells']}
    assert {p.stem for p in paths}==set(expected)
    collected={key:[] for key in ['X','y_terminal','y_first','y_date_given_first','y_second_given_timelydate','mask_date_given_first','mask_second_given_timelydate','group_seed']};cells=[]
    for index,path in enumerate(paths):
        receipt=json.loads((path.parent/'receipts'/(path.stem+'.json')).read_text())
        assert receipt['extractor_sources']==ready['sources'] and receipt['cell']==expected[path.stem]
        assert receipt['rows']>0, 'Zero-rowcellsrequireexplicitbalancedproper-score amendment beforefit'
        assert file_sha256(path)==receipt['output_identity']['sha256']
        with np.load(path,allow_pickle=False) as data:
            meta=json.loads(str(data['metadata_json']))
            assert meta['cell']==expected[path.stem] and meta['provenance']==receipt['provenance']
            assert all(np.all(data[k]==expected[path.stem][v]) for k,v in [('group_seed','seed'),('family','family'),('arm','policy_id')])
            assert int(data['y_terminal'].sum())==receipt['qualified'] and len(data['X'])==receipt['rows']
            assert data['feature_names'].tolist()==feature_names()
            for key in collected:collected[key].append(data[key])
            cells.append(np.full(len(data['X']),index,dtype=np.int32))
    arrays={k:np.concatenate(v) for k,v in collected.items()};cell_ids=np.concatenate(cells);X=arrays['X'];y=arrays['y_terminal'];group=arrays['group_seed']
    masks={k:np.isin(group,values) for k,values in split.items() if k in ('train','validation','development_test')}
    train=masks['train'];wtrain=balanced_weights(cell_ids[train]);Xtrain=X[train]
    inherited_weights=np.zeros(len(X));inherited_weights[train]=wtrain
    support_gate=bool(y[train].sum()>=50 and y[masks['validation']].sum()>=20 and y[masks['development_test']].sum()>=20)
    agree_indices=[i for i,name in enumerate(feature_names()) if name.endswith('__equal_known')]
    agreement=X[:,agree_indices].sum(axis=1)[:,None]
    constant_probability=float(((wtrain/wtrain.sum()*len(wtrain))@y[train]+.5)/(len(wtrain)+1))
    control=fit_logistic(agreement[train],y[train],wtrain)
    constant_p=np.repeat(constant_probability,len(X));agreement_p=predict(control,agreement)
    fits={}
    direct=fit_logistic(Xtrain,y[train],wtrain,l2=1.0)
    fits['direct']=dict(schema='final-model-asset-v1',kind='direct',feature_names=feature_names(),models=[direct])
    funnel=[]
    stage_specs=[('y_first',np.ones(len(X),dtype=bool)),('y_date_given_first',arrays['mask_date_given_first'].astype(bool)),('y_second_given_timelydate',arrays['mask_second_given_timelydate'].astype(bool))]
    stages=[]
    for label,risk in stage_specs:
        use=train&risk;yy=arrays[label][use];ww=inherited_weights[use];xx=X[use]
        support=int(yy.sum())>=50 and int((1-yy).sum())>=50
        if support:model=fit_logistic(xx,yy,ww,l2=1.)
        else:
            p=(float(np.average(yy,weights=ww))*len(yy)+.5)/(len(yy)+1) if len(yy) else .5
            model=dict(schema='public-logistic/v1',mean=[0.]*X.shape[1],scale=[1.]*X.shape[1],intercept=float(np.log(p)-np.log1p(-p)),coefficients=[0.]*X.shape[1],l2=1.,constant=True,converged=True,training_rows=len(yy))
        funnel.append(model);stages.append(dict(label=label,rows=int(use.sum()),positives=int(yy.sum()),personalized=support))
    fits['funnel']=dict(schema='final-model-asset-v1',kind='funnel',feature_names=feature_names(),models=funnel)
    report=dict(schema='r9-prediction-report-v1',split=split,stage_support=stages,models={},controls={},source_identity={name:file_sha256(BASE/name) for name in ('features.py','models.py','dataset.py','train.py','TRAINING_PROTOCOL.md')})
    predictions={kind:asset_predict(asset,X) for kind,asset in fits.items()}
    for kind,p in predictions.items():
        report['models'][kind]={}
        for name in ('validation',):
            use=masks[name];weights=balanced_weights(cell_ids[use]);report['models'][kind][name]=metrics(y[use],p[use],weights,group[use],constant_p[use])
    chosen=min(('direct','funnel'),key=lambda kind:(report['models'][kind]['validation']['log_loss'],0 if kind=='direct' else 1))
    # Only the selected family is opened on development-test; no replacement.
    for name in ('validation','development_test'):
        use=masks[name];weights=balanced_weights(cell_ids[use])
        report['controls'][name]={'constant':metrics(y[use],constant_p[use],weights,group[use]),'agreement':metrics(y[use],agreement_p[use],weights,group[use])}
        if name=='development_test':report['models'][chosen][name]=metrics(y[use],predictions[chosen][use],weights,group[use],constant_p[use])
    gates=[]
    for name in ('validation','development_test'):
        m=report['models'][chosen][name];c=report['controls'][name]
        gates.append(m['log_loss']<min(c['constant']['log_loss'],c['agreement']['log_loss']) and m['bootstrap95_upper_difference']<0 and m['calibration_mean_error']<=.01)
    admitted=bool(support_gate and all(gates));asset=fits[chosen];asset.update(probability_admitted=admitted,scope='training64groups only; validation selected two fixed model families; terminal probability admission '+str(admitted),training_split_sha256=file_sha256(BASE/'split.json'))
    report.update(selected_family=chosen,probability_admitted=admitted,support_gate=support_gate,constant_probability=constant_probability,bootstrap_interval_scope='upperendpointoftwo-sided95percentileinterval',fit_scope='previously examined development worlds; no counterfactual policy-value claim',total_rows=len(X),train_rows=int(train.sum()),train_positives=int(y[train].sum()))
    write_once(BASE/'selected_model.json',asset);write_once(BASE/'prediction_report.json',report)
    print(json.dumps({'selected':chosen,'probability_admitted':admitted,'rows':len(X),'validation':report['models'][chosen]['validation'],'development_test':report['models'][chosen]['development_test']},indent=2),flush=True)
if __name__=='__main__':main()
