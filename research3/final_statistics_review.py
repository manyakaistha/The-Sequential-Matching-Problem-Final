"""Independent read-only final reward audit; no simulator or director analysis import."""
import collections, hashlib, json, math, statistics
from pathlib import Path
import numpy as np
from scipy.stats import t
from research3.independent_replicator import cluster_audit, FAMILIES
ROOT=Path('results/research3')

def main():
    freeze=json.loads((ROOT/'freeze.json').read_text());out={'method':'independent full registered grids, seed cluster reconstruction, bootstrap and influential-seed sensitivity; same data, no new evidence','stages':{}}
    for stage in ['screen','focus','selection','confirmation']:
        path=ROOT/(stage+'.json');data=json.loads(path.read_text());assert data['complete']
        expected={(p,s,v) for p in data['planned_policies'] for s in data['planned_seeds'] for v in FAMILIES}
        found=[(r['policy'],r['seed'],r['variant']) for r in data['episodes']]
        assert len(found)==len(expected)==data['planned_episodes'] and set(found)==expected
        audit=cluster_audit(str(path));official=json.loads((ROOT/(stage+'_statistics.json')).read_text())
        for p,row in audit['clusters'].items():
            actual=official['policies'][p]
            assert abs(row['mean']-actual['primary']['mean'])<1e-12
            for key,field in [('paired_difference','mean'),('paired_sd','sd'),('p_two_sided','p_two_sided')]:
                a,b=row[key],actual['paired'][field]
                assert (a is None and b is None) or (a is not None and b is not None and abs(a-b)<1e-12)
            assert all(abs(a-b)<1e-12 for a,b in zip(row['ci95'],actual['paired']['ci95']))
        out['stages'][stage]=audit
        out['stages'][stage]['exact_grid_episodes']=len(found)
    data=json.loads((ROOT/'confirmation.json').read_text());assert data['code_hashes']==freeze['code_hashes']
    assert data['planned_seeds']==list(range(freeze['confirmation_seeds'][0],freeze['confirmation_seeds'][1]+1))
    assert set(data['planned_policies'])=={'greedy',freeze['policy']}
    assert len(data['planned_seeds'])==freeze['confirmation_n']
    assert hashlib.sha256(Path('research3/EXPERIMENT_REGISTRY.md').read_bytes()).hexdigest()==freeze['registry_sha256']
    rows={(r['policy'],r['seed'],r['variant']):r for r in data['episodes']};seeds=data['planned_seeds'];name=freeze['policy']
    diffs=np.array([sum(rows[name,s,v]['msmi_per_100_arrived_members']-rows['greedy',s,v]['msmi_per_100_arrived_members'] for v in FAMILIES)/6 for s in seeds])
    draws=np.random.default_rng(90210).integers(0,len(seeds),(10000,len(seeds)))
    bootstrap=np.quantile(diffs[draws].mean(axis=1),[.025,.975]).tolist()
    official=json.loads((ROOT/'confirmation_statistics.json').read_text());assert all(abs(a-b)<1e-12 for a,b in zip(bootstrap,official['policies'][name]['bootstrap95']))
    loo=[float(np.delete(diffs,i).mean()) for i in range(len(seeds))]
    out['confirmation_sensitivity']={'bootstrap95':bootstrap,'leave_one_seed_out_effect_range':[min(loo),max(loo)],'positive_negative_zero_cluster_differences':[int((diffs>0).sum()),int((diffs<0).sum()),int((diffs==0).sum())],'seed_effects':dict(zip(map(str,seeds),diffs.tolist())),'qualifications':{p:sum(r['mutual_second_meeting_intention'] for r in data['episodes'] if r['policy']==p) for p in ['greedy',name]},'resource_counts':{'invalid':sum(not r['valid'] for r in data['episodes']),'failures':sum(r['failure_count'] for r in data['episodes']),'optimized_fallbacks':sum(r.get('optimized_fallback_count',0) for r in data['episodes'])}}
    target=ROOT/'independent_final_statistics.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['stages']['confirmation'],indent=2));print(json.dumps(out['confirmation_sensitivity'],indent=2))
if __name__=='__main__':main()
