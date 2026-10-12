"""Observation-only adaptive reciprocal policy. No dataset or hidden-world access.
The original policy.py remains the reference baseline. See REPORT.md for limitations.
"""
import argparse
import itertools
import json
import math
import signal
import sys
import time
from kit import HARD, OPTIONS, eligibility

FEATURES = ('relationship_goal', 'relationship_pace', 'lifestyle', 'conversations')
DEFAULT = dict(engine='blossom', asks='degree', threshold='adaptive', fusion='harmonic',
               learning=True, dfm=True, epoch=1, hard_days=0)

def sigmoid(z):
    return 1 / (1 + math.exp(-max(-30, min(30, z))))

def blocked(m):
    return any(m['field_status'].get(k) == 'declined' for k in HARD)

def verified(m):
    return all(m['fields'].get(k) is not None for k in HARD)

def features(a, b, day=0):
    x = [1.0]
    for k in FEATURES:
        v, w = a['fields'].get(k), b['fields'].get(k)
        x.append((1 if v == w else -.5) if v is not None and w is not None
                 else 1.5 / len(OPTIONS[k]) - .5)
    x.append(float(day >= 35))
    return x

def update(state, memory, cfg):
    """Diagonal Laplace logistic approximation; terminal feedback only, no fake negatives.
    Snapshot features when assigning, so later clarifications cannot leak into examples.
    """
    memory = memory if isinstance(memory, dict) and memory.get('version') == 1 else {}
    weights = list(memory.get('weights', [-.25, .55, .5, .0, .3, -.15]))
    precision = list(memory.get('precision', [8., 8., 8., 8., 8., 8.]))
    seen = set(memory.get('seen', [])); users = memory.get('users', {})
    exposures = memory.get('exposures', {})
    intros = {i['introduction_id']: i for i in state['introductions']}
    by_id = {m['member_id']: m for m in state['members']}
    for e in state['feedback']:
        key = e['introduction_id'] + ':' + str(e.get('member_id')) + ':' + e['event']
        if key in seen or e['event'] != 'introduction_response':
            continue
        seen.add(key)
        intro = intros.get(e['introduction_id'])
        if intro is None: continue
        ident = e['member_id']; u = users.setdefault(ident, [3., 1., 0., 0.])
        u[0] += e['value'] is not None; u[1] += e['value'] is None
        if e['value'] is None: continue
        u[2] += e['value'] == 'yes'; u[3] += e['value'] == 'no'
        pairkey = '|'.join(sorted([intro['user_a'], intro['user_b']])) + ':' + str(intro['assigned_day'])
        x = exposures.get(pairkey)
        if x is None: continue  # external history has no assignment-time snapshot
        if cfg['learning']:
            p = sigmoid(sum(w * v for w, v in zip(weights, x)))
            for j, v in enumerate(x):
                precision[j] += p * (1-p) * v*v
                weights[j] += (float(e['value'] == 'yes') - p) * v / precision[j]
    # All historical exposures are bounded by 200 choose 2; prune resolved pairs.
    done = {i for i in intros if sum(e['event'] == 'introduction_response' and
            e['introduction_id'] == i for e in state['feedback']) == 2}
    for i in done:
        intro = intros[i]
        key = '|'.join(sorted([intro['user_a'], intro['user_b']])) + ':' + str(intro['assigned_day'])
        exposures.pop(key, None)
    return dict(version=1, weights=weights, precision=precision, seen=sorted(seen),
                users=users, exposures=exposures)

def response_probability(m, state, memory, dfm):
    u = memory['users'].get(m['member_id'], [3., 1., 0., 0.])
    p = u[0] / (u[0] + u[1])
    if not dfm: return p
    # EM for response/no-response mixture with the simulator's discrete response CDF.
    # Pending is NOT a failure. Posterior eventual response p(1-F)/(1-pF).
    observed = {(e['introduction_id'], e.get('member_id')) for e in state['feedback']
                if e['event'] == 'introduction_response'}
    pending = [min(1., max(0., (state['day']-i['assigned_day']) / 7))
               for i in state['introductions'] if m['member_id'] in (i['user_a'], i['user_b'])
               and (i['introduction_id'], m['member_id']) not in observed]
    for _ in range(4):
        expected = sum(p*(1-f)/max(1e-9, 1-p*f) for f in pending)
        p = (u[0]+expected)/(u[0]+u[1]+len(pending))
    return p

def probabilities(a, b, state, memory, cfg):
    base = sum(w*v for w, v in zip(memory['weights'], features(a,b,state['day'])))
    ps = []
    for m in (a,b):
        u = memory['users'].get(m['member_id'], [3.,1.,0.,0.])
        # Shrink heterogeneous actor acceptance estimates towards population fit.
        actor = .35 * math.log((u[2]+2)/(u[3]+2))
        ps.append(sigmoid(base+actor)*response_probability(m,state,memory,cfg['dfm']))
    return ps

def ask_actions(state, memory, cfg):
    budget = max(0, min(12, int(state.get('ask_budget_remaining', 0))))
    if cfg['asks'] == 'none' or budget == 0: return []
    active = [m for m in state['members'] if m['available'] and not blocked(m)]
    unknown = [m for m in active if not verified(m)]
    selected = []; chosen = set()
    if cfg['asks'] != 'soft':
        potential = {m['member_id']: [] for m in unknown}
        for m in unknown:
            for n in active:
                if m['member_id'] == n['member_id']: continue
                if eligibility(m,n)['status'] != 'infeasible':
                    potential[m['member_id']].append(n)
        while budget >= 3 and len(chosen) < len(unknown):
            def value(m):
                ns = potential[m['member_id']]
                if cfg['asks'] == 'fifo': return -active.index(m)
                # Immediate expansion plus complementarity for another selected bundle.
                gain = sum(1 if verified(n) or n['member_id'] in chosen else .18 for n in ns)
                exploration = .12*math.sqrt(math.log(2+state['day'])/(1+len(ns))) if ns else 0
                return gain + exploration
            remaining = [m for m in unknown if m['member_id'] not in chosen]
            m = max(remaining, key=lambda m:(value(m), m['member_id']))
            if cfg['asks'] == 'degree' and not potential[m['member_id']]: break
            chosen.add(m['member_id']); selected.append(dict(member_id=m['member_id'],field='constraints'))
            budget -= 3
    if state['day'] < cfg['hard_days']: return selected
    # Soft queries only on already verified members, with feasible available neighbors.
    candidates = []
    for m in active:
        if not verified(m): continue
        neighbors = [n for n in active if eligibility(m,n)['status']=='feasible']
        for j,k in enumerate(FEATURES):
            if m['fields'].get(k) is not None or m['field_status'].get(k)=='declined': continue
            gain = sum(n['fields'].get(k) is not None for n in neighbors)
            candidates.append((gain*(abs(memory['weights'][j+1])+.1),m['member_id'],k))
    for score,ident,k in sorted(candidates,reverse=True):
        if budget <= 0: break
        if score <= 0: continue
        selected.append(dict(member_id=ident,field=k));budget-=1
    return selected

class SolverTimeout(Exception): pass

def bounded_solver(graph):
    import networkx as nx
    if not hasattr(signal, 'setitimer'):
        raise SolverTimeout('No interruptible timer; use greedy')
    previous = signal.getsignal(signal.SIGALRM)
    def timeout(*_): raise SolverTimeout('500 ms solver deadline')
    try:
        signal.signal(signal.SIGALRM, timeout)
        signal.setitimer(signal.ITIMER_REAL, .5)
        return nx.max_weight_matching(graph, weight='weight')
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)

def match_actions(state, memory, cfg):
    if state['day'] % cfg['epoch']: return []
    members = [m for m in state['members'] if m['available'] and verified(m) and not blocked(m)]
    past = {tuple(sorted((i['user_a'],i['user_b']))) for i in state['introductions']}
    raw = []; degree = {m['member_id']:0 for m in members}
    for a,b in itertools.combinations(members,2):
        pair = tuple(sorted((a['member_id'],b['member_id'])))
        if pair in past or eligibility(a,b)['status'] != 'feasible': continue
        pa,pb = probabilities(a,b,state,memory,cfg)
        fusion = (2*pa*pb/max(1e-9,pa+pb) if cfg['fusion']=='harmonic'
                  else pa*pb if cfg['fusion']=='product' else pa)
        # Terminal multiplier is a ranking approximation, not a calibrated MSMI probability.
        same_goal = a['fields'].get('relationship_goal') is not None and a['fields'].get('relationship_goal')==b['fields'].get('relationship_goal')
        score = fusion * (.13 if same_goal else .10)
        raw.append((score,pair,a,b)); degree[pair[0]]+=1;degree[pair[1]]+=1
    edges=[]
    for score,pair,a,b in raw:
        t = (.018 if cfg['threshold']=='static' else 0 if cfg['threshold']=='zero'
             else .024 * max(0.,(35-state['day'])/35) * min(1., min(degree[i] for i in pair)/4))
        if cfg['threshold'] == 'hazard':
            # Prior departure hazard, conditional on survival; unavailability also
            # includes busy/paused members, so it cannot identify actual exits.
            d = state['day']
            h = (.12/39)/(1-.12*(d-22)/39) if 22 <= d <= 59 else 0.
            t = .024 * (60-d)/60 * (1-h)**8 * min(1., min(degree[i] for i in pair)/4)
        if score>t: edges.append((score-t,pair))
    def greedy():
        used=set(); out=[]
        for _,pair in sorted(edges,key=lambda e:(-e[0],e[1])):
            if not used.intersection(pair): out.append(list(pair));used.update(pair)
        return out
    pairs=greedy()
    if edges and cfg['engine'] != 'greedy':
        try:
            import networkx as nx
            g=nx.Graph();g.add_weighted_edges_from((p[0],p[1],w) for w,p in edges)
            if cfg['engine']=='hungarian':
                # Honest forced partition: men versus everyone else; infeasible edges absent.
                # scipy is research-only; production blossom does not import it.
                import numpy as np
                from scipy.optimize import linear_sum_assignment
                left=[m['member_id'] for m in members if m['gender']=='man'];right=[m['member_id'] for m in members if m['gender']!='man']
                if left and right:
                    mat=np.zeros((len(left),len(right)+len(left)))
                    for i,u in enumerate(left):
                        for j,v in enumerate(right):
                            mat[i,j]=g[u][v]['weight'] if g.has_edge(u,v) else -1
                    rows,cols=linear_sum_assignment(mat,maximize=True)
                    pairs=[[left[i],right[j]] for i,j in zip(rows,cols) if j<len(right) and mat[i,j]>0]
                else: pairs=[]
            else: pairs=[sorted(p) for p in bounded_solver(g)]
        except Exception:
            # Solver failures must preserve legal actions; control exceptions
            # (KeyboardInterrupt/SystemExit) are not swallowed by Exception.
            pairs=greedy()
    by_id={m['member_id']:m for m in members}
    for u,v in pairs:
        key='|'.join(sorted([u,v]))+':'+str(state['day'])
        memory['exposures'][key]=features(by_id[u],by_id[v],state['day'])
    return sorted(pairs)

def decide(request, config=None):
    cfg=dict(DEFAULT);cfg.update(config or {})
    state=request['state'];memory=update(state,request.get('memory'),cfg)
    key='asks' if request['phase']=='ask' else 'pairs'
    actions=ask_actions(state,memory,cfg) if key=='asks' else match_actions(state,memory,cfg)
    return {key:actions,'memory':memory}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',default='greedy');parser.add_argument('--config',default='{}')
    args=parser.parse_args();request={}
    try:
        raw=sys.stdin.buffer.read(1024*1024+1)
        if len(raw)>1024*1024: raise ValueError('input size')
        request=json.loads(raw,parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
        response=decide(request,json.loads(args.config))
        if len(json.dumps(response,allow_nan=False).encode())>=1024*1024: raise ValueError('output size')
    except (ValueError, KeyError, TypeError, AttributeError, IndexError) as error:
        print('Policy fallback: '+type(error).__name__,file=sys.stderr)
        response={'asks' if isinstance(request,dict) and request.get('phase')=='ask' else 'pairs':[],'memory':{}}
    print(json.dumps(response,allow_nan=False))

if __name__=='__main__': main()
