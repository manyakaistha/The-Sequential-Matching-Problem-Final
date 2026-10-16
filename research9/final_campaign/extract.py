"""Frozen four-worker streaming extraction, with immutable per-cell receipts."""
import concurrent.futures,hashlib,json,os,time
from pathlib import Path
from research8.soft_query_followup.v2.registration import ROOT,write_once,file_sha256
from .dataset import extract_cell

BASE=ROOT/'research9/final_campaign'

def frozen_sources():
    return {str(p.relative_to(ROOT)):file_sha256(p) for p in [BASE/'features.py',BASE/'models.py',BASE/'dataset.py',BASE/'extract.py',BASE/'split.json',BASE/'CAMPAIGN_PLAN.md']}

def work(args):
    commit,dest,sources=args
    for name,value in sources.items():
        if file_sha256(ROOT/name)!=value:raise ValueError('data extraction source changed: '+name)
    return extract_cell(ROOT/'results/research8/soft_query_followup/v2_replication',commit,dest)

def main():
    dest=ROOT/'results/research9/final_campaign/dataset';dest.mkdir(parents=True,exist_ok=True)
    freeze_path=BASE/'data_freeze.json';sources=frozen_sources()
    if freeze_path.exists():
        frozen=json.loads(freeze_path.read_text());assert frozen['sources']==sources
    else:
        frozen={'schema':'r9-data-freeze-v1','sources':sources,'split_sha256':file_sha256(BASE/'split.json'),'workers':4,'scope':'old audited2880cells only; actualpublicassignmentfeatures; nofreshoutcomes'}
        write_once(freeze_path,frozen)
    commits=sorted((ROOT/'results/research8/soft_query_followup/v2_replication/commits').glob('*.json'));assert len(commits)==2880
    receipts=dest/'receipts';receipts.mkdir(exist_ok=True)
    queue=[];done=0;started=time.monotonic()
    for path in commits:
        receipt=receipts/(path.stem+'.json')
        if receipt.exists():
            row=json.loads(receipt.read_text());assert file_sha256(row['path'])==row['output_identity']['sha256'];done+=1
        elif (dest/(path.stem+'.npz')).exists():raise ValueError('unreceipted extraction preserved; explicit recovery required')
        else:queue.append((path,dest,sources))
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        for result in pool.map(work,queue,chunksize=1):
            result['extractor_sources']=sources
            write_once(receipts/(result['cell']['cell_key']+'.json'),result)
            done+=1
            if done%50==0:print(json.dumps({'event':'extraction_progress','cells':done,'total':2880,'elapsed_seconds':time.monotonic()-started}),flush=True)
    assert frozen_sources()==sources
    write_once(BASE/'dataset_ready.json',{'status':'complete','cells':done,'sources':sources,'dataset':str(dest),'elapsed_seconds':time.monotonic()-started})
    print('All2880cells exported with exact assignment-time public features.',flush=True)
if __name__=='__main__':main()
