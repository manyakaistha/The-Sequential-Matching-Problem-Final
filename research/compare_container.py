"""Compare host and container semantic actions with independent simulator states."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from kit import Simulator,generate,VERSION
from evaluate import invoke,docker_command
world=generate(101,200,'evaluation','development');sims=[Simulator(world),Simulator(world)];mems=[None,None];diffs=[];order=[];peak=[0.,0.]
for day in range(60):
    for phase in ('ask','match'):
        responses=[]
        for j,sim in enumerate(sims):
            request=dict(schema_version=VERSION,state=sim.observe(),phase=phase,memory=mems[j]);cmd=[sys.executable,'research_policy.py'] if j==0 else docker_command('sequential-research:1.0')
            r,t=invoke(cmd,request);peak[j]=max(peak[j],t);mems[j]=r['memory'];responses.append(r)
        key='asks' if phase=='ask' else 'pairs'
        actions=[r[key] for r in responses]
        canonical=lambda xs: sorted(json.dumps(x,sort_keys=True) for x in xs)
        if actions[0]!=actions[1]:
            target=order if canonical(actions[0])==canonical(actions[1]) else diffs
            target.append(dict(day=day,phase=phase,host=actions[0],container=actions[1]))
        for j,sim in enumerate(sims):
            if phase=='ask':sim.resolve_asks(actions[j])
            else:sim.advance(actions[j])
for sim in sims:
    for _ in range(40):sim.advance([])
out=dict(semantic_action_differences=diffs,ordering_only_differences=order,peak_call_seconds=peak,host_metrics=sims[0].metrics(),container_metrics=sims[1].metrics())
Path('results/research/container_comparison.json').write_text(json.dumps(out,indent=2)+'\n');print('semantic differences',len(diffs),'ordering only',len(order))
