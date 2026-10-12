"""Modular observation-only JSON matching policy. No latent world access."""
import argparse
import copy
import itertools
import json
import math
import random
import signal
import sys
import time
from kit import HARD, SOFT, OPTIONS, eligibility
from research.terminal_model import predict_funnel, equality_probabilities, update_memory

DEFAULT=dict(model='integrated',regime=True,learning=True,asks='fifo',engine='greedy',
             opportunity='none',batching=False,uncertainty=0.,query_samples=4,
             query_candidates=10,solver_seconds=.2,query_seconds=.65,soft=False)
LIMIT=1024*1024


def blocked(m): return any(m['field_status'].get(k)=='declined' for k in HARD)
def verified(m): return all(m['fields'].get(k) is not None for k in HARD)


def hard_distributions(m):
    """Exact public-generator semantic-field priors conditioned on age/zone.
    Field priors are independent except age bounds depend on public age, and zones
    on public home zone. Scenario sparse inferred only from observable zone syntax.
    """
    from collections import Counter
    age=m['age']; zone=m['zone']
    zones=('zone_a','zone_b','zone_c','zone_d'); zone_weights=(.60,.23,.12,.05)
    def grouped(values):
        count=Counter(values); return [(v,n/len(values)) for v,n in count.items()]
    def subsets(items,counts):
        return [(tuple(s),mass/math.comb(len(items),k)) for k,mass in counts
                for s in itertools.combinations(items,k)]
    d=dict(age_min=grouped([max(18,age-i) for i in range(3,11)]),
           age_max=grouped([min(65,age+i) for i in range(3,11)]),
           who_to_meet=subsets(('woman','man','non_binary'),((1,.7),(2,.2),(3,.1))),
           relationship_structure=[('monogamous',.9),('non_monogamous',.1)],
           smoking=[('no',.75),('occasionally',.2),('yes',.05)],
           partner_smoking=[('no_smoking',.5),('any',.5)],
           has_children=[(False,.85),(True,.15)],
           partner_children=[('any',.5),('no_children',.5)],
           wants_children=[('yes',1/3),('no',1/3),('unsure',1/3)],
           schedule=subsets(('weekday_evening','weekend_day','weekend_evening'),((1,1/3),(2,1/3),(3,1/3))))
    # Generator extra-zone draw is uniform, not zone-population weighted.
    d['acceptable_zones']=[((zone,),1.)] if zone not in zones else [((zone,),.775)]+[((zone,z),.075) for z in zones if z!=zone]
    for k in HARD:
        if m['fields'].get(k) is not None:
            value=m['fields'][k]; d[k]=[(tuple(value) if isinstance(value,list) else value,1.)]
    return d


def entropy(m):
    return sum(-sum(p*math.log2(p) for _,p in values) for k,values in hard_distributions(m).items()
               if m['fields'].get(k) is None)


def sample_hard(m,rng):
    out=dict(m);out['fields']=dict(m['fields'])
    for k,values in hard_distributions(m).items():
        out['fields'][k]=rng.choices([v for v,_ in values],[p for _,p in values])[0]
    return out


class SolverTimeout(Exception): pass


def solve(edges,seconds=.2):
    """Interruptible general-graph weighted matching with a legal greedy fallback."""
    greedy=greedy_edges(edges)
    if not edges: return greedy
    try:
        import networkx as nx
        if not hasattr(signal,'setitimer'): return greedy
        previous=signal.getsignal(signal.SIGALRM)
        old_timer=signal.getitimer(signal.ITIMER_REAL)
        def timeout(*_): raise SolverTimeout()
        started=time.monotonic()
        try:
            signal.signal(signal.SIGALRM,timeout)
            signal.setitimer(signal.ITIMER_REAL,max(.001,seconds))
            graph=nx.Graph();graph.add_weighted_edges_from((p[0],p[1],w) for w,p in edges)
            return sorted([sorted(p) for p in nx.max_weight_matching(graph,weight='weight')])
        finally:
            signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
            if old_timer[0]: signal.setitimer(signal.ITIMER_REAL,max(.001,old_timer[0]-(time.monotonic()-started)),old_timer[1])
    except Exception: return greedy


def greedy_edges(edges):
    out=[];used=set()
    for weight,pair in sorted(edges,key=lambda row:(-row[0],row[1])):
        if weight<=0 or used.intersection(pair): continue
        used.update(pair);out.append(list(pair))
    return sorted(out)


def matching_value(edges,cfg,deadline):
    remaining=deadline-time.monotonic()
    pairs=solve(edges,min(.018,max(.001,remaining))) if remaining>0 else greedy_edges(edges)
    weights={tuple(sorted(p)):w for w,p in edges}
    return sum(weights[tuple(sorted(p))] for p in pairs)


def ask_actions(state,memory,cfg):
    budget=max(0,min(12,int(state.get('ask_budget_remaining',0))))
    if budget<1 or cfg['asks']=='none': return []
    active=[m for m in state['members'] if m.get('available') and not blocked(m)]
    unknown=[m for m in active if not verified(m)]
    past={tuple(sorted((i['user_a'],i['user_b']))) for i in state['introductions']}
    potential={m['member_id']:[] for m in unknown}
    for m in unknown:
        for n in active:
            pair=tuple(sorted((m['member_id'],n['member_id'])))
            if m==n or pair in past: continue
            if eligibility(m,n)['status']!='infeasible': potential[m['member_id']].append(n)
    chosen=[]
    mode=cfg['asks']
    if mode=='fifo': chosen=unknown[:budget//3]
    elif mode=='entropy': chosen=sorted(unknown,key=lambda m:(-entropy(m),m['member_id']))[:budget//3]
    elif mode=='random':
        rng=random.Random('ask:'+str(state['day'])+':'+','.join(m['member_id'] for m in unknown))
        rng.shuffle(unknown);chosen=unknown[:budget//3]
    elif mode in ('value','two_query') and unknown and budget>=3:
        # Correlated bundle outcomes sampled per member, not independently per edge.
        # Restrict candidates by observed potential degree before expensive lookahead.
        candidates=sorted(unknown,key=lambda m:(-len(potential[m['member_id']]),m['member_id']))[:cfg['query_candidates']]
        candidate_ids={m['member_id'] for m in candidates}
        complete=[m for m in active if verified(m)]
        relevant=complete+candidates
        weights={}
        for a,b in itertools.combinations(relevant,2):
            pair=tuple(sorted((a['member_id'],b['member_id'])))
            if pair not in past and eligibility(a,b)['status']!='infeasible':
                weights[pair]=predict_funnel(a,b,state,memory,cfg)['terminal']
        samples=[]
        for sample in range(cfg['query_samples']):
            rng=random.Random('voi:'+str(state['day'])+':'+str(sample)+':'+','.join(sorted(candidate_ids)))
            sampled=[sample_hard(m,rng) if m['member_id'] in candidate_ids else m for m in relevant]
            edges=[]
            for a,b in itertools.combinations(sampled,2):
                pair=tuple(sorted((a['member_id'],b['member_id'])))
                if pair in weights and eligibility(a,b)['status']=='feasible': edges.append((weights[pair],pair))
            samples.append(edges)
        deadline=time.monotonic()+cfg['query_seconds'];cache={}
        def value(ids):
            key=tuple(sorted(ids))
            if key not in cache:
                cache[key]=sum(matching_value([(w,p) for w,p in es if all(i not in candidate_ids or i in ids for i in p)],cfg,deadline) for es in samples)/len(samples)
            return cache[key]
        selected=set();slots=budget//3
        while slots and len(selected)<len(candidates):
            base=value(selected); available=[m['member_id'] for m in candidates if m['member_id'] not in selected]
            options=[(value(selected|{i})-base,(i,)) for i in available]
            if mode=='two_query' and slots>=2 and time.monotonic()<deadline:
                options += [((value(selected|{a,b})-base)/2,(a,b)) for a,b in itertools.combinations(available,2)]
            gain,ids=max(options,key=lambda x:(x[0],x[1]))
            # Exploration fallback on zero myopic gain, essential at complementary cold start.
            if gain<=1e-12: ids=(max(available,key=lambda i:(len(potential[i]),i)),)
            selected.update(ids);slots-=len(ids)
            if time.monotonic()>=deadline:
                for i in sorted(available,key=lambda i:(-len(potential[i]),i)):
                    if slots<=0: break
                    if i not in selected: selected.add(i);slots-=1
                break
        chosen=[m for m in candidates if m['member_id'] in selected]
    else:
        selected=set()
        for _ in range(min(budget//3,len(unknown))):
            remaining=[m for m in unknown if m['member_id'] not in selected]
            m=max(remaining,key=lambda m:(sum(1. if verified(n) or n['member_id'] in selected else .18 for n in potential[m['member_id']]),m['member_id']))
            selected.add(m['member_id']);chosen.append(m)
    asks=[dict(member_id=m['member_id'],field='constraints') for m in chosen];budget-=3*len(chosen)
    if cfg.get('soft') and budget:
        # One-query exact outcome enumeration for decision-changing soft information.
        verified_members=[m for m in active if verified(m)]
        edges=[];query_candidates=[]
        for a,b in itertools.combinations(verified_members,2):
            pair=tuple(sorted((a['member_id'],b['member_id'])))
            if pair not in past and eligibility(a,b)['status']=='feasible': edges.append((predict_funnel(a,b,state,memory,cfg)['terminal'],pair))
        deadline=time.monotonic()+min(.2,cfg['query_seconds']);base=matching_value(edges,cfg,deadline)
        by_id={m['member_id']:m for m in verified_members}
        for m in verified_members:
            for field in ('relationship_goal','relationship_pace','lifestyle','conversations'):
                if m['fields'].get(field) is not None or m['field_status'].get(field)=='declined': continue
                if time.monotonic()>deadline: break
                expected=0.
                for val in OPTIONS[field]:
                    hypothetical=dict(m);hypothetical['fields']=dict(m['fields']);hypothetical['fields'][field]=val
                    changed=[]
                    for w,pair in edges:
                        if m['member_id'] in pair:
                            n=by_id[pair[1] if pair[0]==m['member_id'] else pair[0]]
                            w=predict_funnel(hypothetical,n,state,memory,cfg)['terminal']
                        changed.append((w,pair))
                    expected+=matching_value(changed,cfg,deadline)/len(OPTIONS[field])
                query_candidates.append((expected-base,m['member_id'],field))
        for gain,ident,field in sorted(query_candidates,reverse=True):
            if budget<=0: break
            if gain>1e-8: asks.append(dict(member_id=ident,field=field));budget-=1
    return asks


def match_actions(state,memory,cfg):
    active=[m for m in state['members'] if m.get('available') and verified(m) and not blocked(m)]
    past={tuple(sorted((i['user_a'],i['user_b']))) for i in state['introductions']}
    edges=[];predictions={};alternatives={m['member_id']:[] for m in active}
    for a,b in itertools.combinations(active,2):
        pair=tuple(sorted((a['member_id'],b['member_id'])))
        if pair in past or eligibility(a,b)['status']!='feasible': continue
        pred=predict_funnel(a,b,state,memory,cfg);w=pred['terminal']
        if cfg['model']=='ranking_control':
            w=(pred['response_a']*pred['accept_a'])*(pred['response_b']*pred['accept_b'])
        predictions[pair]=pred;edges.append((w,pair))
        for ident in pair: alternatives[ident].append((w,pair))
    adjusted=[];remaining=60-state['day']
    for w,pair in edges:
        pred=predictions[pair]
        if cfg['opportunity']!='none' and remaining>1:
            # Approximate foregone introduction throughput: eight-day minimum busy
            # plus mutual-acceptance duration, retirement, and finite alternatives.
            accept=pred['both_accept_unconditional']
            lag_logits=memory.get('date_logweights',[math.log(5.),0.])
            delayed=1/(1+math.exp(max(-30.,min(30.,lag_logits[0]-lag_logits[1]))))
            busy=8+accept*(10.642857142857+8.5*delayed)
            hazard=(.12/39)/(1-.12*max(0,state['day']-22)/39) if state['day']>=22 else 0.
            cost=0.
            for ident in pair:
                others=[value for value,p in alternatives[ident] if p!=pair]
                if not others: continue
                best=max(others)
                attempts=min(len(others),max(0,(remaining-1)/8))
                node_value=.5*best*attempts
                lost=min(1.,busy/max(1,remaining))*(1-pred['pause'])+pred['pause']
                cost+=node_value*lost*(1-hazard)**busy
            w-=cost
        if cfg.get('uncertainty'):
            known=sum(p in (0.,1.) for p in equality_probabilities(next(m for m in active if m['member_id']==pair[0]),next(m for m in active if m['member_id']==pair[1])))
            w-=cfg['uncertainty']*pred['terminal']*(4-known)/4
        if w>0: adjusted.append((w,pair))
    if cfg['batching'] and state['day']<20:
        # Component-specific two-day wait only when incompleteness touches component.
        adjacency={m['member_id']:set() for m in active}
        for _,p in adjusted: adjacency[p[0]].add(p[1]);adjacency[p[1]].add(p[0])
        waiting=set();visited=set()
        incomplete=[m for m in state['members'] if m.get('available') and not blocked(m) and not verified(m)]
        by_id={m['member_id']:m for m in active}
        for ident in adjacency:
            if ident in visited: continue
            todo=[ident];component=set()
            while todo:
                u=todo.pop()
                if u in component: continue
                component.add(u);todo.extend(adjacency[u]-component)
            visited.update(component)
            grows=any(eligibility(by_id[u],m)['status']!='infeasible' for u in component for m in incomplete)
            if grows and len(component)>=3 and state['day']%2: waiting.update(component)
        adjusted=[(w,p) for w,p in adjusted if not waiting.intersection(p)]
    pairs=solve(adjusted,cfg['solver_seconds']) if cfg['engine']=='blossom' else greedy_edges(adjusted)
    by_id={m['member_id']:m for m in active}
    for a,b in pairs:
        pair=tuple(sorted((a,b)));key='|'.join(pair)+':'+str(state['day'])
        memory['snapshots'][key]=dict(day=state['day'],users=[a,b],equal=list(equality_probabilities(by_id[a],by_id[b])),pred=predictions[pair])
    return pairs


def fallback(request):
    return {'asks' if isinstance(request,dict) and request.get('phase')=='ask' else 'pairs':[],'memory':{}}


def decide(request,config=None):
    try:
        cfg=dict(DEFAULT);cfg.update(config or {})
        if not isinstance(request,dict) or request.get('phase') not in ('ask','match'): return fallback(request)
        state=request['state']
        if not isinstance(state,dict) or not isinstance(state['members'],list): return fallback(request)
        # Safe protocol boundary: corrupt memory cannot cause a hidden-state read.
        json.dumps(request,allow_nan=False)
        memory=update_memory(state,copy.deepcopy(request.get('memory')),cfg)
        key='asks' if request['phase']=='ask' else 'pairs'
        actions=ask_actions(state,memory,cfg) if key=='asks' else match_actions(state,memory,cfg)
        if len(json.dumps(memory,allow_nan=False).encode())>=LIMIT:
            memory['snapshots']={};memory['seen']=[];memory['regime_seen']=[]
        response={key:actions,'memory':memory}
        if len(json.dumps(response,allow_nan=False).encode())>=LIMIT: return fallback(request)
        return response
    except (ValueError,TypeError,KeyError,AttributeError,IndexError,OverflowError): return fallback(request)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',default='greedy');parser.add_argument('--config',default='{}');parser.add_argument('--candidate')
    args=parser.parse_args();request={}
    try:
        raw=sys.stdin.buffer.read(LIMIT+1)
        if len(raw)>LIMIT: raise ValueError('request too large')
        request=json.loads(raw,parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
        config=json.loads(args.config)
        if args.candidate:
            from research.extended_candidates import CANDIDATES
            config=dict(CANDIDATES[args.candidate],**config)
        response=decide(request,config)
    except (ValueError,KeyError,TypeError): response=fallback(request)
    print(json.dumps(response,allow_nan=False))


if __name__=='__main__': main()
