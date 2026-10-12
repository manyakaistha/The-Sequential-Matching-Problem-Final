"""Create a pre-evaluation test design using historical variance/cost metadata only."""
from datetime import datetime,timezone
import hashlib,json,math,platform,sys
from pathlib import Path
import numpy,scipy
from scipy.stats import nct,t
from research4.benchmark import hashes

ROOT=Path('results/research5')
SOURCES=('research5/__init__.py','research5/prepare.py','research5/run_test.py','research5/analyze.py','research5/benchmark.py')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def power(n,delta,sd,alpha):return float(nct.sf(t.ppf(1-alpha/2,n-1),n-1,delta*math.sqrt(n)/sd))
def main():
    ROOT.mkdir(exist_ok=True)
    if (ROOT/'design.json').exists():raise ValueError('Existing registration is immutable; refuse overwrite')
    prior=json.loads(Path('results/research4/freeze.json').read_text())
    assert prior['policy']=='population_control' and prior['code_hashes']==hashes()
    alpha=.05/4;sd=.26;delta=.05;target=.90
    minimum=next(n for n in range(3,10001) if power(n,delta,sd,alpha)>=target)
    n=math.ceil(1.10*minimum)
    assert minimum==390 and n==430
    first,last=90001,90000+n
    inventory=json.loads(Path('results/research4/seed_inventory.json').read_text())
    blocked=set(range(1,10001))|set(inventory['examined_or_reserved_inherited_seed_keys'])
    for lo,hi in inventory['new_reserved_ranges']:blocked.update(range(lo,hi+1))
    for stage in ('screen','focus','selection','confirmation'):
        rows=json.loads((Path('results/research4')/(stage+'.json')).read_text())
        blocked.update(rows['planned_seeds'])
    proposed=set(range(first,last+1));assert not blocked&proposed
    archive=json.loads(Path('results/research4/archive_index.json').read_text())
    trace=next(r for r in archive['archives'] if Path(r['path']).name=='confirmation_traces.tar.gz')
    prior_costs=[json.loads(line) for line in Path('results/research4/commands.jsonl').read_text().splitlines() if line.strip()]
    cost=next(r for r in prior_costs if r.get('status')=='finished' and isinstance(r.get('command'),list) and 'research4.benchmark' in r['command'] and 'results/research4/confirmation.json' in r['command'])
    episodes=12*n;ratio=episodes/672
    estimate={'episodes':episodes,'workers':2,'wall_seconds':cost['wall_seconds']*ratio,'os_child_cpu_seconds':cost['child_cpu_seconds']*ratio,'raw_trace_bytes':sum(m['bytes'] for m in trace['members'])*ratio,'compressed_trace_bytes':trace['bytes']*ratio,'scope':'Linear extrapolation from round4 E; not guaranteed, excludes new full logging, replication/analysis/archive overhead. No external spend.'}
    design={'registered_utc':datetime.now(timezone.utc).isoformat(),'status':'prepared_not_executed','candidate':prior['policy'],'configuration':prior['configuration'],'baseline':'shipped kit baseline_asks/baseline_match','policies':['greedy',prior['policy']],'seeds':list(range(first,last+1)),'families':['development','sparse','cold_start','delayed','shift','drift'],'n_clusters':n,'planned_episodes':episodes,'decision_days':60,'follow_up_days':40,'alpha':alpha,'family_size':4,'adjusted_confidence':1-alpha,'primary_target_effect_for_power':delta,'planning_sd':sd,'minimum_n_model_power90':minimum,'sample_inflation':1.10,'model_power_at_fixed_n':power(n,delta,sd,alpha),'success':'All fixed cells valid, zero failure/fallback, positive lower adjusted paired-t CI and two-sided p<.0125. Practical effect lower>.05 is separate. No guarantee of universal superiority.','frozen_inherited_hashes':hashes(),'initializer_hashes':{p:sha(p) for p in ('research3/__init__.py','research4/__init__.py')},'setup_source_hashes':{p:sha(p) for p in SOURCES},'analysis_helper_hashes':{'research3/analyze.py':sha('research3/analyze.py')},'registry_sha256':sha('research5/EXPERIMENT_REGISTRY.md'),'prior_manifest_sha256':sha('results/research4/manifest.json'),'cost_estimate':estimate,'logging':{'schema':'research5-full-v1','minimum_free_disk_bytes':200_000_000_000,'policy_io':'complete request and validated response JSON including input/output memory, errors and timing; per-episode gzip JSONL level1','privileged':'separate initial generated world and complete final simulator state, never passed to policy','estimate_scope':'Old 57GB raw trace estimate excludes added logs. Added compressed size/runtime unknown; 200GB launch guard is a conservative operational reserve, not a proven bound. Retain all artifacts; no automatic deletion.'},'versions':{'python':sys.version,'platform':platform.platform(),'numpy':numpy.__version__,'scipy':scipy.__version__},'seed_inventory':{'prior_inventory_sha256':sha('results/research4/seed_inventory.json'),'blocked_seeds':sorted(blocked),'proposed_overlap':sorted(blocked&proposed),'scope':'Repository-recorded actual/planned seeds plus guard; no claim about unrecorded external usage. No proposed world generated.'},'power_sensitivity':[{'sd':s,'effect':d,'power_at_n':power(n,d,s,alpha)} for s in (.2275845624,.2526184558,.26,.30,.35) for d in (.025,.05,.075,.10)]}
    (ROOT/'design.json').write_text(json.dumps(design,indent=2)+'\n')
    print(json.dumps({k:design[k] for k in ('n_clusters','planned_episodes','alpha','model_power_at_fixed_n','cost_estimate')},indent=2))
if __name__=='__main__':main()
