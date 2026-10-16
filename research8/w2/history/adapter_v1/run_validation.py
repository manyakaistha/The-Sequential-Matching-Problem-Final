"""Registered reduced B1 grid and constructed-wire performance tests.

No simulator episodes, model fitting or reward/panel comparisons.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from time import perf_counter
import hashlib
import json
import platform
import subprocess
import sys

from research8.planner import Actor, ExactPlanner, Model, ScenarioState
from research8.w2.bounded import BoundedPlanner
from research8.w2.public_adapter import decide,evaluate_projection
from research8.w2.tests.fixtures import absorbing,request,waiting_projection


def run():
    base=Path(__file__).parent
    reg=json.loads((base/'registration.json').read_text())
    rows=[]
    g=reg['fixed_grid']
    for today,middle,future in product(g['current_reward'],g['intermediate_reward'],g['future_reward']):
        model=Model(tuple(Actor(a) for a in 'ABCD'),
                    (absorbing(0,('A','B'),F(today)),absorbing(1,('A','C'),F(middle)),absorbing(2,('A','D'),F(future))),end_day=2)
        state=ScenarioState(0,tuple('ABCD'))
        start=perf_counter();candidate=BoundedPlanner(model).solve(state);elapsed=perf_counter()-start
        oracle=ExactPlanner(model).solve(state)
        if candidate.used_fallback:raise AssertionError(candidate.fallback_reason)
        realized_first_value=ExactPlanner(model).evaluate_actions(state,[candidate.action],controller='exact').value
        assert oracle.value==max(map(F,(today,middle,future)))
        assert oracle.value-realized_first_value<=F(1,100)
        rows.append(dict(today=today,middle=middle,future=future,action=candidate.action,
                         expected=str(candidate.value),oracle=str(oracle.value),
                         regret=str(oracle.value-realized_first_value),states=candidate.states,
                         transitions=candidate.transitions,support_entries=candidate.support_entries,
                         solve_seconds=elapsed))
    assert len(rows)==27
    bench=[]
    for phase in reg['benchmarks']['phases']:
        raw=request(200,phase,unknown=20 if phase=='ask' else 0)
        wire=json.dumps(raw,allow_nan=False)
        assert len(wire.encode())<=1048576
        for kind,n in [('direct',10),('subprocess',3)]:
            times=[]
            for _ in range(n):
                start=perf_counter()
                if kind=='direct':out=decide(raw)
                else:
                    proc=subprocess.run([sys.executable,'-m','research8.w2.public_adapter'],input=wire,
                                        text=True,capture_output=True,timeout=10,check=True)
                    if len(proc.stdout.encode())>1048576:raise RuntimeError('Output cap')
                    out=json.loads(proc.stdout)
                times.append(perf_counter()-start)
                assert out['memory']['last_status']['mode']=='G_fallback'
            bench.append(dict(phase=phase,kind=kind,n=n,seconds=times,max_seconds=max(times),
                              below_user_target=all(t<1 for t in times),active_planning=False))
    active=[]
    for _ in range(10):
        start=perf_counter();out=evaluate_projection(request(),waiting_projection);active.append(perf_counter()-start)
        assert out['pairs']==[] and out['memory']['last_status']['mode']=='offline_declared_projection'
    files=['bounded.py','public_adapter.py','public_rules.py','protocol.py','registration.json','run_validation.py']
    return dict(status='passed',model_fidelity_scope='27 declaredfouractor threeepoch cases',
                grid_rows=rows,max_grid_regret=str(max(F(r['regret']) for r in rows)),
                max_bounded_solve_seconds=max(r['solve_seconds'] for r in rows),
                runtime=bench,offline_fouractor_projection_seconds=active,
                tested_runtime_gate_passed=all(b['below_user_target'] for b in bench),
                live_model_asset_admitted=False,live_candidate_switches=False,production_reward_admitted=False,
                host=dict(python=sys.version,platform=platform.platform()),
                source_sha256={f:hashlib.sha256((base/f).read_bytes()).hexdigest() for f in files},
                frozen_old_core_sha256=hashlib.sha256((base.parent/'planner.py').read_bytes()).hexdigest(),
                official_episodes=0,fits=0,
                limits=['Constructed200member Gfallback timing, not active200member B1 timing',
                        'Availability-only finitebelief core, not full publicfeedback/uncertainexit kernel',
                        'Zero tail after12futureepochs not fullhorizon certificate',
                        'No qualifiedreward prediction assets admitted'])


if __name__=='__main__':
    result=run()
    with (Path(__file__).parent/'results'/'validation.json').open('x') as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=result['status'],cases=len(result['grid_rows']),max_grid_regret=result['max_grid_regret'],
                         max_bounded_solve_seconds=result['max_bounded_solve_seconds'],
                         runtime=[{k:b[k] for k in ['phase','kind','max_seconds','below_user_target']} for b in result['runtime']],
                         tested_runtime_gate_passed=result['tested_runtime_gate_passed'],live_model_asset_admitted=False),indent=2))
