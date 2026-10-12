"""Analyze only the completed registered fresh grid; never pool prior confirmation."""
import json,math,statistics
from pathlib import Path
import numpy as np
from scipy.stats import t
from research3.analyze import analyze
from research5.run_test import ROOT,check

def main():
    design=check();target=ROOT/'analysis.json'
    if target.exists():raise ValueError('Refuse analysis overwrite')
    data=json.loads((ROOT/'confirmation.json').read_text())
    assert data['complete'] and data['planned_seeds']==design['seeds'] and data['planned_policies']==design['policies']
    assert set(data['planned_variants'])==set(design['families']) and len(data['episodes'])==design['planned_episodes']
    assert data['code_hashes']==design['frozen_inherited_hashes']
    assert data['recorder_sha256']==design['setup_source_hashes']['research5/benchmark.py']
    assert data['logging_schema']==design['logging']['schema']
    assert data['decision_days']==60 and data['follow_up_days']==40
    stats=analyze(ROOT/'confirmation.json')
    pairs={}
    for row in data['episodes']:
        permitted_recorders={design['setup_source_hashes']['research5/benchmark.py']}
        if design.get('recovery'):permitted_recorders.update(design['recovery']['prior_recorder_sha256s'])
        assert row['recorder_source_sha256'] in permitted_recorders
        assert row['invocation_count']==120 and row['arrived_members']==200
        assert abs(row['msmi_per_100_arrived_members']-100*row['mutual_second_meeting_intention']/row['arrived_members'])<1e-12
        pairs[row['policy'],row['seed'],row['variant']]=row['msmi_per_100_arrived_members']
    differences=[statistics.mean(pairs['population_control',s,v]-pairs['greedy',s,v] for v in design['families']) for s in design['seeds']]
    n=len(differences);mean=statistics.mean(differences);sd=statistics.stdev(differences)
    radius=float(t.ppf(1-design['alpha']/2,n-1))*sd/math.sqrt(n)
    interval=[mean-radius,mean+radius];p=stats['policies']['population_control']['paired']['p_two_sided']
    success=bool(sd>0 and p is not None and interval[0]>0 and p<design['alpha'])
    rng=np.random.default_rng(90210);draws=rng.integers(0,n,(10000,n))
    bootstrap=np.quantile(np.asarray(differences)[draws].mean(axis=1),[design['alpha']/2,1-design['alpha']/2]).tolist()
    result={'design_sha256':__import__('hashlib').sha256((ROOT/'design.json').read_bytes()).hexdigest(),'fresh_data_only':True,'statistics':stats,'adjusted_ci98_75':interval,'adjusted_bootstrap98_75_sensitivity':bootstrap,'program_family_alpha':design['alpha'],'superiority':success,'practical_effect_lower_above_05':bool(success and interval[0]>.05),'paired_seed_differences':dict(zip(map(str,design['seeds']),differences)),'inference_scope':'Four finite primary comparisons, each family claim uses commonalpha .0125; old summaries preserved. Normal-cluster t assumptions/large-sample approximation; no universal optimality, equivalence, or future-round guarantee. Bootstrap secondary, never switches primary gate.'}
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('adjusted_ci98_75','superiority','practical_effect_lower_above_05')},indent=2))
if __name__=='__main__':main()
