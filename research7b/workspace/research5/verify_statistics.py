"""Independent completed-grid statistics, with no director analysis imports."""
import collections,hashlib,json,math,statistics,time,sys
from pathlib import Path
import numpy as np
from scipy.stats import t
ROOT=Path('results/research5')
FAMILIES=('development','sparse','cold_start','delayed','shift','drift')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def paired(values,alpha):
 n=len(values);mean=statistics.mean(values);sd=statistics.stdev(values);se=sd/math.sqrt(n);radius=float(t.ppf(1-alpha/2,n-1))*se
 return {'n':n,'mean':mean,'sd':sd,'ci':[mean-radius,mean+radius],'p_two_sided':float(2*t.sf(abs(mean/se),n-1)) if se else None}
def audit():
 d=json.loads((ROOT/'design.json').read_text());data=json.loads((ROOT/'confirmation.json').read_text());official=json.loads((ROOT/'analysis.json').read_text())
 assert d['seeds']==list(range(90001,90431)) and d['families']==list(FAMILIES) and d['policies']==['greedy','population_control'] and d['alpha']==.0125
 assert data['complete'] and data['planned_episodes']==5160 and data['planned_seeds']==d['seeds'] and data['planned_policies']==d['policies'] and set(data['planned_variants'])==set(FAMILIES)
 assert data['decision_days']==60 and data['follow_up_days']==40 and data['code_hashes']==d['frozen_inherited_hashes']
 for field in ('frozen_inherited_hashes','initializer_hashes','setup_source_hashes','analysis_helper_hashes'):
  for p,h in d[field].items():assert sha(p)==h,p
 assert sha('research5/EXPERIMENT_REGISTRY.md')==d['registry_sha256']
 assert sha(ROOT/'design.json')==official['design_sha256']
 assert data['recorder_sha256']==d['setup_source_hashes']['research5/benchmark.py'] and data['logging_schema']==d['logging']['schema']
 permitted={data['recorder_sha256']}|set(d.get('recovery',{}).get('prior_recorder_sha256s',[]));groups=collections.defaultdict(dict);counts=collections.defaultdict(collections.Counter);attribution=collections.Counter();recoveries=collections.Counter()
 for r in data['episodes']:
  key=r['seed'],r['variant'];assert key not in groups[r['policy']];assert r['policy'] in d['policies'] and r['valid'] and r['failure_count']==0 and r['optimized_fallback_count']==0
  assert r['invocation_count']==120 and r['arrived_members']==200 and r['recorder_source_sha256'] in permitted
  q=r['mutual_second_meeting_intention'];assert isinstance(q,int) and q>=0 and abs(r['msmi_per_100_arrived_members']-q/2)<1e-12
  groups[r['policy']][key]=q/2
  for k in ('assignments','mutual_acceptances','dates','mutual_second_meeting_intention','served_members','arrived_members','ask_cost'):counts[r['policy']][k]+=r[k]
  attribution[r['recorder_source_sha256']]+=1
  if r.get('recovered_from'):recoveries[r['recovered_from']]+=1
 expected={(s,v) for s in d['seeds'] for v in FAMILIES};assert len(data['episodes'])==5160 and set(groups)==set(d['policies']) and all(set(g)==expected for g in groups.values())
 means={p:[sum(g[s,v] for v in FAMILIES)/6 for s in d['seeds']] for p,g in groups.items()};diff=[a-b for a,b in zip(means['population_control'],means['greedy'])];nom=paired(diff,.05);adj=paired(diff,.0125)
 draws=np.random.default_rng(90210).integers(0,430,(10000,430));boot=np.asarray(diff)[draws].mean(axis=1);bs95=np.quantile(boot,[.025,.975]).tolist();bsadj=np.quantile(boot,[.00625,.99375]).tolist()
 errors={}
 def compare(label,a,b):
  err=float(np.max(np.abs(np.asarray(a,dtype=float)-np.asarray(b,dtype=float))));errors[label]=err;assert err<1e-12,(label,a,b)
 compare('adjusted_ci',adj['ci'],official['adjusted_ci98_75']);compare('adjusted_bootstrap',bsadj,official['adjusted_bootstrap98_75_sensitivity']);compare('nominal_ci',nom['ci'],official['statistics']['policies']['population_control']['paired']['ci95']);compare('paired_mean',adj['mean'],official['statistics']['policies']['population_control']['paired']['mean']);compare('paired_sd',adj['sd'],official['statistics']['policies']['population_control']['paired']['sd']);compare('p',adj['p_two_sided'],official['statistics']['policies']['population_control']['paired']['p_two_sided']);compare('nominal_bootstrap',bs95,official['statistics']['policies']['population_control']['bootstrap95']);compare('all_seed_differences',diff,[official['paired_seed_differences'][str(s)] for s in d['seeds']])
 for p,m in means.items():compare(p+'_mean',statistics.mean(m),official['statistics']['policies'][p]['primary']['mean'])
 superiority=bool(adj['ci'][0]>0 and adj['p_two_sided']<.0125);assert superiority==official['superiority'];assert bool(superiority and adj['ci'][0]>.05)==official['practical_effect_lower_above_05']
 # Verify recovered committed rows against every original key and recorded field.
 bykey={(r['policy'],r['seed'],r['variant']):r for r in data['episodes']};sources={}
 for source in recoveries:
  prior=json.loads(Path(source).read_text());preserved=0
  for old in prior['episodes']:
   new=bykey[old['policy'],old['seed'],old['variant']]
   for k,v in old.items():
    if k not in {'trace','full_invocation_log','privileged_audit_log','audit_files','recovered_from','recorder_source_sha256'}:assert new[k]==v,(source,k)
   assert new['recorder_source_sha256']==old.get('recorder_source_sha256',prior['recorder_sha256']);preserved+=1
  sources[source]={'source_sha256':sha(source),'all_original_rows_preserved':preserved}
 # Immediate recovery must contain every saved row, independent of prior provenance path.
 if d.get('recovery'):
  prior=json.loads(Path(d['recovery']['source_result']).read_text());assert sha(d['recovery']['source_result'])==d['recovery']['source_result_sha256'];assert len(prior['episodes'])==d['recovery']['preserved_rows']
  assert all((r['policy'],r['seed'],r['variant']) in bykey for r in prior['episodes'])
 return {'scope':'Independent counts and paired seed statistics; no research3.analyze/research5.analyze dependency; same fixed interrupted sample, no prior-study pooling','qualified_denominator':'100*qualified_dyads/200arrived; family mean within430seeds; means of ratios coincide with pooled count ratio here because every denominator200','means':{p:statistics.mean(v) for p,v in means.items()},'nominal95':nom,'adjusted98_75':adj,'bootstrap95':bs95,'bootstrap98_75':bsadj,'superiority':superiority,'practical_lower_above05':bool(superiority and adj['ci'][0]>.05),'scenario_means':{p:{v:statistics.mean(g[s,v] for s in d['seeds']) for v in FAMILIES} for p,g in groups.items()},'totals':dict(counts),'recorder_attribution':dict(attribution),'recovery_provenance_counts':dict(recoveries),'original_source_preservation':sources,'official_max_abs_errors':errors,'invalid_failures_fallbacks':0,'leave_one_seed_out_range':[min((sum(diff)-x)/429 for x in diff),max((sum(diff)-x)/429 for x in diff)],'seed_differences':dict(zip(map(str,d['seeds']),diff)),'fresh_data_only_interpretation':'New registered round relative to earlier studies; includes118retained same-round committed rows after operational interruptions, not a newly untouched replacement sample. Literal fresh_data_only does not mean interruption-free.'}
def main():
 p=ROOT/'independent_statistics.json';assert not p.exists(),'refuse overwrite';start=time.process_time();wall=time.monotonic();obj=audit();obj.update(cpu_seconds=time.process_time()-start,wall_seconds=time.monotonic()-wall,command=sys.argv,source_hashes={str(q):sha(q) for q in [Path(__file__),ROOT/'design.json',ROOT/'confirmation.json',ROOT/'analysis.json']});p.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps({k:obj[k] for k in ('means','adjusted98_75','superiority','practical_lower_above05','recorder_attribution','cpu_seconds')},indent=2))
if __name__=='__main__':main()
