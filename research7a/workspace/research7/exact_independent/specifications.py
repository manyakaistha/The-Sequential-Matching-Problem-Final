"""Executed constructed cases, not simulator validation or candidate admission.

Every dynamic assertion comes from a Fraction belief-tree enumeration. The full
reachable-node/action/tie/branch traces are retained in each case's ``runs``.
"""
from dataclasses import asdict, is_dataclass, replace
from fractions import Fraction as F
from itertools import combinations, product
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from time import process_time
import gzip
import json

from research7.exact_independent.models import Actor, Edge, Outcome, State, TemporalModel, law
from research7.exact_independent.solver import (BeliefSolver, vertex_recursive_enumeration,
    greedy_matching, enumerate_labelled_4vertex_graphs, verify_matching_legality)


def encode(x):
    if isinstance(x, F):
        return f'{x.numerator}/{x.denominator}'
    if is_dataclass(x):
        return {k: encode(v) for k, v in asdict(x).items()}
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (set, frozenset)):
        return [encode(v) for v in sorted(x, key=repr)]
    if isinstance(x, (list, tuple)):
        return [encode(v) for v in x]
    return x


def solve(model):
    result = BeliefSolver(model).solve()
    descriptor = dict(type=type(model).__name__, attributes=vars(model))
    result['input_model'] = descriptor
    result['input_model_sha256'] = sha256(json.dumps(encode(descriptor), sort_keys=True).encode()).hexdigest()
    return result


def action_values(run, phase='match'):
    node = run['nodes'][0]
    if phase == 'match':
        # Initial query is empty for all no-query transition cases.
        ask = next(a for a in node['actions'] if a['action'] == ('ask', ()))
        assert len(ask['outcomes']) == 1
        node = run['nodes'][ask['outcomes'][0]['child']]
    return {a['action'][1]: a['value'] for a in node['actions']}


def record(case_id, runs, checks, **details):
    return dict(case_id=case_id, status='constructed_enumeration_pass' if all(checks.values()) else 'failed',
                verified=all(checks.values()), checks=checks, runs=runs, **details)


def spec_t02_static_trap():
    vertices = frozenset('ABCD')
    edges = [('A','B',F(9,10)), ('C','D',F(1,20)), ('A','D',F(13,20)), ('B','C',F(13,20))]
    matchings = vertex_recursive_enumeration(vertices, edges)
    greedy, gv = greedy_matching(vertices, edges)
    graphs, cycles = enumerate_labelled_4vertex_graphs(), verify_matching_legality()
    return record('T02', {}, {'greedy': gv == F(19,20), 'optimum': matchings[0][1] == F(13,10),
                  'triangle_and_odd_cycles': all(v['is_exact'] for v in cycles.values()),
                  'all_64_full_action_sets': len(graphs) == 64 and all(g['valid'] for g in graphs)},
                  matchings=matchings, greedy=greedy, greedy_value=gv, graphs=graphs, cycles=cycles)


def delay_model(slow=False, future=True, truncated=False):
    outcomes = (Outcome(F(1,5),F(1),True,label='qualified_pause'),
                Outcome(F(2,5),F(0),False,8,8,'return8'),
                Outcome(F(2,5),F(0),False,16 if slow else 8,8,'slow_A' if slow else 'return8b'))
    edges = [Edge('A','B',(0,),outcomes)]
    if future:
        edges.append(Edge('A','C',(8,),law(F(4,5))))
    return TemporalModel((0,) if truncated else (0,8), [Actor(a) for a in 'ABC'], edges)


def spec_t03_delay_reversal():
    runs = {name: solve(delay_model(**kw)) for name, kw in (
        ('fast',{}), ('slow',{'slow':True}), ('fast_no_future',{'future':False}),
        ('slow_no_future',{'slow':True,'future':False}), ('fast_short',{'truncated':True}),
        ('slow_short',{'slow':True,'truncated':True}))}
    fast, slow = action_values(runs['fast']), action_values(runs['slow'])
    ab = (('A','B'),)
    checks = {'fast_AB':fast[ab] == F(21,25), 'slow_AB':slow[ab] == F(13,25),
              'wait_both':fast[()] == slow[()] == F(4,5),
              'reversal':fast[ab] > fast[()] and slow[ab] < slow[()]}
    for name in ('fast_no_future','slow_no_future','fast_short','slow_short'):
        vals = action_values(runs[name]); checks[name] = vals[ab] == F(1,5) and vals[()] == 0
    return record('T03',runs,checks, expected={'fast_AB':F(21,25),'slow_AB':F(13,25),'wait':F(4,5)})


def query_model(p, real=False, extra_future=False):
    actors = [Actor('A'), Actor('U',departure=1,known=False), Actor('V',known=False), Actor('W',arrival=1,known=False)]
    edges = [Edge('A','U',(0,),law(F(1,5))), Edge('V','W',(1,),law(F(4,5)))]
    if real:
        for prefix, day in (('X',0),('Y',1)):
            for i in range(3):
                unknown, known = prefix+str(i), prefix+str(i)+'P'
                actors += [Actor(unknown,arrival=day,departure=day+1,known=False),Actor(known,arrival=day,departure=day+1)]
                edges.append(Edge(unknown,known,(day,),law(F(1))))
    verified = frozenset(a.name for a in actors if a.known)
    initial = [(prob,State(verified=verified,latent=(('present:W',present),)))
               for prob,present in ((p,True),(1-p,False)) if prob]
    base = 12 if real else 3
    return TemporalModel((0,1),actors,edges,(base,base+(3 if extra_future else 0)),initial)


def spec_t04_query_tree():
    runs, checks = {}, {}
    # Below, at, above threshold, arrival removed, and capacity relaxation.
    for real in (False,True):
        for name,p,extra in (('zero',F(0),False),('below',F(1,5),False),
                             ('tie',F(1,4),False),('above',F(7,20),False),('capacity',F(7,20),True)):
            key = ('budget12_' if real else 'scaled3_') + (('capacity_future15' if real else 'capacity_future6') if extra else name)
            runs[key] = run = solve(query_model(p,real,extra))
            values = action_values(run,'ask')
            competitors = ('X0','X1','X2') if real else ()
            u, v = tuple(sorted(competitors+('U',))), tuple(sorted(competitors+('V',)))
            base = F(6) if real else F(0)
            if extra:
                checks[key] = values[u] == base + F(1,5) + p*F(4,5) and values[u] > values[v]
            else:
                checks[key] = values[u] == base+F(1,5) and values[v] == base+p*F(4,5)
            checks[key+'_optimum'] = run['value'] == max(values[u],values[v])
            checks[key+'_budget'] = all(3*len(a['action'][1]) <= run['input_model']['attributes']['budgets'][node['belief'][0][1].epoch]
                for node in run['nodes'] for a in node['actions'] if a['action'][0] == 'ask')
    return record('T04',runs,checks,threshold=F(1,4),
                  capacity_relaxation='Fixed12 evidence is the zero/below/tie/above cases; real relaxation explicitly raises tomorrow to15. Scaled one-bundle3 toy relaxes tomorrow to6.',
                  real_embedding='Three useful cost-3 X bundles today, three newly arriving useful Y bundles tomorrow; each earns 1. W must also be queried after arrival.',
                  applicability='D2 query-choice proof; D1 FIFO only requires transition correctness')


def spec_t05_reuse_dyad():
    runs = {}
    for name,n,q,p in (('triangle_coupled',3,F(1,10),F(1,10)), ('two_actors',2,F(1,10),F(1,10)),
                        ('triangle_unqualified_pause',3,F(1,20),F(1,10))):
        actors = [Actor(a) for a in 'ABC'[:n]]
        edges = [Edge(a,b,(0,8,16),law(q,p)) for a,b in combinations('ABC'[:n],2)]
        runs[name] = solve(TemporalModel((0,8,16),actors,edges))
    seen_unqualified = any(b['reward'] == 0 and b['next_state'].paused
        for node in runs['triangle_unqualified_pause']['nodes'] for a in node['actions'] for b in a['branches'])
    return record('T05',runs,{'triangle':runs['triangle_coupled']['value'] == F(271,1000),
        'two_actors':runs['two_actors']['value'] == F(1,10),
        'q_less_p':runs['triangle_unqualified_pause']['value'] == F(271,2000),
        'zero_reward_pause_executed':seen_unqualified},
        expected={'triangle':F(271,1000),'two_actors':F(1,10),'q_less_p':F(271,2000)},
        limitation='Outcome feedback is released by next 8-day epoch in this toy; simulator delayed-label timing requires separate fixtures.')


def uncertain_query_model(shared=True, complement=False):
    if complement:
        actors,edges = [Actor('A',known=False),Actor('B',known=False)], [Edge('A','B',(0,),law(F(1)))]
        return TemporalModel((0,),actors,edges,6)
    unknown = ('A','B')
    actors = [Actor(a,known=False) for a in unknown] + [Actor('C')]
    if not shared:
        actors += [Actor('D')]
    edges = [Edge('A','C',(0,),law(F(1))), Edge('B','C' if shared else 'D',(0,),law(F(1)))]
    unlock = F(4,5) if shared else F(7,10)
    initial=[]
    for answers in product((False,True),repeat=2):
        prob=F(1)
        for answer in answers:
            prob *= unlock if answer else 1-unlock
        initial.append((prob,State(verified=frozenset(a.name for a in actors if a.known),
                                  latent=tuple(('answer:'+a,v) for a,v in zip(unknown,answers)))))
    return TemporalModel((0,),actors,edges,6,initial)


def spec_t06_query_complement():
    runs={name:solve(model) for name,model in (('complement',uncertain_query_model(complement=True)),
          ('shared',uncertain_query_model()),('distinct',uncertain_query_model(shared=False)))}
    vals=action_values(runs['complement'],'ask')
    shared,distinct=action_values(runs['shared'],'ask'),action_values(runs['distinct'],'ask')
    degree_shared=shared[('A',)]+shared[('B',)]
    degree_distinct=distinct[('A',)]+distinct[('B',)]
    return record('T06',runs,{'complement': vals[()] == vals[('A',)] == vals[('B',)] == 0 and vals[('A','B')] == 1,
        'collision':shared[('A','B')] == F(24,25), 'distinct':distinct[('A','B')] == F(7,5),
        'degree_wrong':degree_shared == F(8,5) > degree_distinct == F(7,5)},
        degree_shared=degree_shared,degree_distinct=degree_distinct)


def spec_t07_continuation_nonadditive():
    edges=[Edge('A','B',(0,),law(F(1,2),F(1))),Edge('C','D',(0,),law(F(1,2),F(1))),
           Edge('A','C',(8,),law(F(9,10)))]
    run=solve(TemporalModel((0,8),[Actor(a) for a in 'ABCD'],edges))
    vals=action_values(run)
    # Derive separate continuation losses from enumerated conditional values.
    wait=vals[()]
    loss_ab=wait-(vals[(('A','B'),)]-F(1,2))
    loss_cd=wait-(vals[(('C','D'),)]-F(1,2))
    return record('T07',{'joint':run},{'joint':vals[(('A','B'),('C','D'))] == 1 > wait == F(9,10),
        'separate_loss_double_counts':loss_ab == loss_cd == F(9,10),
        'additive_rejects':F(1,2)-loss_ab < 0 and F(1,2)-loss_cd < 0},
        separate_losses=[loss_ab,loss_cd],scope='Counterexample to exact additive losses, not a rejection of approximate duals.')


def spec_t08_static_prices():
    edges=[(a,b,F(1)) for a,b in combinations('ABCD',2)]
    matching=vertex_recursive_enumeration(frozenset('ABCD'),edges)
    incidence=[]
    for pairs,value in matching:
        if len(pairs)==2:
            counts=tuple(sum(a in edge for edge in pairs) for a in 'ABCD')
            incidence.append(dict(matching=pairs,price_coefficients=counts,bonus_coefficient=len(pairs)))
    return record('T08',{}, {'symbolic_coefficients':len(incidence)==3 and all(
        x['price_coefficients']==(1,1,1,1) and x['bonus_coefficient']==2 for x in incidence)},
        full_action_set=matching, symbolic_evidence=incidence,
        proof='Disjoint matching covers each member of S exactly once; its linear penalty coefficients are the indicator vector of S, for arbitrary rational prices.')


class PosteriorModel:
    def __init__(self):
        self.initial=[(F(1,2),(0,'H','pending')),(F(1,2),(0,'L','pending'))]
    def observe(self,s): return s[0],s[2]
    def terminal(self,s): return s[0]==2
    def actions(self,s): return ('wait',) if s[0]==0 else ('next_response',)
    def transition(self,s,a):
        rate=F(3,4) if s[1]=='H' else F(1,4)
        if s[0]==0:
            return [(rate,(1,s[1],'mature_yes'),F(0)),(1-rate,(1,s[1],'mature_no'),F(0))]
        return [(rate,(2,s[1],'next_yes'),F(1)),(1-rate,(2,s[1],'next_no'),F(0))]


def spec_t09_public_posterior():
    run=solve(PosteriorModel())
    pending=run['nodes'][0]
    no=next(n for n in run['nodes'] if n['history'][-1][1]==(1,'mature_no'))
    post_high=sum(p for p,s in no['belief'] if s[1]=='H')
    # Distinct Beta surrogate, integer sufficient-statistic update (not a fit).
    mature=(0,); successes=sum(mature); trials=len(mature)
    beta=F(1+successes,2+trials)
    return record('T09',{'two_type':run},{'pending_prior':sum(p for p,s in pending['belief'] if s[1]=='H') == F(1,2),
        'mature_posterior':post_high == F(1,4),'next_response':no['value'] == F(3,8),
        'beta_separate':beta == F(1,3)},post_high=post_high,beta_surrogate=beta)


def spec_t10_terminal_followup():
    edges=[Edge('A','B',(59,),law(F(3,5),F(4,5),20)),Edge('A','C',(59,),law(F(2,5),F(2,5),5))]
    run=solve(TemporalModel((59,),[Actor(a) for a in 'ABC'],edges))
    vals=action_values(run)
    unqualified=[b for n in run['nodes'] for a in n['actions'] for b in a['branches']
                 if b['reward']==0 and b['next_state'].paused and ('A','B') in b['next_state'].used]
    return record('T10',{'last_day':run},{'higher_q_longer':vals[(('A','B'),)] == F(3,5) > vals[(('A','C'),)] == F(2,5),
        'late_pause_zero_reward':bool(unqualified), 'no_terminal_actions':all(not n['actions'] for n in run['nodes'] if n['history'][-1][1][0]==1)},
        limitation='Constructed late-pause branch labels, not a simulator deadline implementation test.')


class PendingModel(TemporalModel):
    def transition(self,s,action):
        for p,child,reward in super().transition(s,action):
            if action[0]=='match':
                matured=('old_outcome',dict(s.latent)['old_qualified'])
                child=replace(child,pending=(),events=child.events+(matured,))
            yield p,child,reward


def spec_t31_pending_continuation():
    runs={}
    for name,new in (('old_only',False),('new_disjoint',True)):
        actors=[Actor(a) for a in 'ABCD']
        initial=[(p,State(verified=frozenset('ABCD'),used=frozenset({('A','B')}),
                          busy=(('A',8),('B',8)),pending=(('old_AB',F(9,20)),),latent=(('old_qualified',yes),)))
                 for p,yes in ((F(9,20),True),(F(11,20),False))]
        edges=[Edge('C','D',(0,),law(F(3,10)))] if new else []
        runs[name]=solve(PendingModel((0,),actors,edges,initial=initial))
    return record('T31',runs,{'old_contributes_zero':runs['old_only']['value']==0,
        'new_only_increment':runs['new_disjoint']['value']==F(3,10),
        'old_feedback_resolves':any(b['next_state'].pending==() for n in runs['old_only']['nodes']
                                  for a in n['actions'] for b in a['branches'])},
        expected={'old_only':F(0),'new_disjoint':F(3,10)},scope='Independent target bookkeeping; deployed D1/D2/L2 must separately agree with this oracle.')


def get_all_test_specifications():
    return {'T02':spec_t02_static_trap,'T03':spec_t03_delay_reversal,'T04':spec_t04_query_tree,
        'T05':spec_t05_reuse_dyad,'T06':spec_t06_query_complement,'T07':spec_t07_continuation_nonadditive,
        'T08':spec_t08_static_prices,'T09':spec_t09_public_posterior,'T10':spec_t10_terminal_followup,
        'T31':spec_t31_pending_continuation}


@lru_cache(maxsize=1)
def run_exact_specification_check():
    started=process_time(); ledger={}
    for name,fn in get_all_test_specifications().items():
        ledger[name]=fn()
        if process_time()-started > 300:
            raise TimeoutError('aggregate 300 CPU second allowance exceeded')
    return dict(status='constructed_belief_enumerations_complete',total_cases=len(ledger),
        all_verified=all(c['verified'] for c in ledger.values()),case_ledger=ledger,cpu_seconds=process_time()-started,
        developer='/root/r7_exact_repair',independent_reviewer='/root/r7_live_critic (review pending)',
        source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))},
        gates={'constructed_oracle':'executed; independent review pending','D1_D2_L2_candidate_agreement':'unclosed',
               'simulator_timing_and_protocol':'separate fixtures required','baseline_smoke':'No D1/D2 proof dependency for baseline-only arm; runtime/registration gates still apply'})


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    report=run_exact_specification_check()
    summary={k:v for k,v in report.items() if k!='case_ledger'};summary['case_ledger']={}
    for name,case in report['case_ledger'].items():
        raw=json.dumps(encode(case),sort_keys=True,separators=(',',':')).encode()
        path=output/(name+'.json.gz');path.write_bytes(gzip.compress(raw,mtime=0))
        summary['case_ledger'][name]={k:v for k,v in case.items() if k not in ('runs','graphs','full_action_set')}
        summary['case_ledger'][name].update(artifact=path.name,artifact_sha256=sha256(path.read_bytes()).hexdigest(),
            runs={n:{k:r[k] for k in ('value','enumerated_states','support_states','enumerated_transitions','cpu_seconds','input_model_sha256')} for n,r in case['runs'].items()})
    (output/'summary.json').write_text(json.dumps(encode(summary),indent=2,sort_keys=True)+'\n')
    print(json.dumps(encode({'all_verified':report['all_verified'],'cpu_seconds':report['cpu_seconds'],
                            'cases':{n:c['verified'] for n,c in report['case_ledger'].items()}})))
