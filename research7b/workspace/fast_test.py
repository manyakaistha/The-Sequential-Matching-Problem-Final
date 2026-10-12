import sys
import itertools
import random
import copy
from kit import Simulator, generate, VERSION, HARD, SOFT, eligibility

def smart_decide(state):
    phase = state
    
    # 1. Gather all candidates
    members = {m['member_id']: m for m in state['members'] if m['available']}
    
    budget = state['ask_budget_remaining']
    asks = []
    
    # Priority 1: resolve missing HARD fields for members who are available
    missing_hard = []
    for m in state['members']:
        if m['available']:
            if any(m['fields'].get(k) is None and m['field_status'].get(k) != 'declined' for k in HARD):
                missing_hard.append(m['member_id'])
    
    for m_id in missing_hard:
        if budget >= 3:
            asks.append({'member_id': m_id, 'field': 'constraints'})
            budget -= 3
            
    # Priority 2: Ask for relationship_goal for promising candidates
    if budget > 0:
        feasible_members = set()
        past = {tuple(sorted((i['user_a'], i['user_b']))) for i in state['introductions']}
        mem_list = [m for m in state['members'] if m['available']]
        for a, b in itertools.combinations(mem_list, 2):
            key = tuple(sorted((a['member_id'], b['member_id'])))
            if key in past: continue
            if eligibility(a, b)['status'] == 'feasible':
                feasible_members.add(a['member_id'])
                feasible_members.add(b['member_id'])
        
        # Now, for these members, we want to know their relationship_goal
        for m_id in list(feasible_members):
            if budget >= 1:
                m = members[m_id]
                if m['fields'].get('relationship_goal') is None and m['field_status'].get('relationship_goal') != 'declined':
                    asks.append({'member_id': m_id, 'field': 'relationship_goal'})
                    budget -= 1

    return asks

def smart_match(state):
    past = {tuple(sorted((i['user_a'], i['user_b']))) for i in state['introductions']}
    mem_list = [m for m in state['members'] if m['available']]
    edges = []
    w = {'relationship_goal': 3.0, 'relationship_pace': 1.0, 'conversations': 0.5, 'lifestyle': 0.1}
    
    weights_by_node = {m['member_id']: [] for m in mem_list}
    
    for a, b in itertools.combinations(mem_list, 2):
        key = tuple(sorted((a['member_id'], b['member_id'])))
        if key in past: continue
        if eligibility(a, b)['status'] != 'feasible': continue
        
        score = 0
        for k, weight in w.items():
            va = a['fields'].get(k)
            vb = b['fields'].get(k)
            if va is not None and vb is not None:
                if va == vb:
                    score += weight
                else:
                    score -= weight * 0.5
        
        edges.append((score, a['member_id'], b['member_id']))
        weights_by_node[a['member_id']].append((score, key))
        weights_by_node[b['member_id']].append((score, key))
            
    final_edges = []
    for score, m1, m2 in edges:
        key = tuple(sorted((m1, m2)))
        cost = 0.
        for ident in (m1, m2):
            others = [val for val, p in weights_by_node[ident] if p != key]
            if others:
                cost += max(others) * 0.5
        adjusted = score - cost
        final_edges.append((adjusted, m1, m2))
        
    used = set()
    pairs = []
    for adj, m1, m2 in sorted(final_edges, reverse=True):
        if adj >= 0 and m1 not in used and m2 not in used:
            pairs.append([m1, m2])
            used.add(m1)
            used.add(m2)
            
    return pairs

def run_test(policy_ask, policy_match):
    seeds = range(2001, 2011)
    msmi = 0
    den = 0
    for seed in seeds:
        sim = Simulator(generate(seed, 200, variant='development'))
        for _ in range(60):
            sim.resolve_asks(policy_ask(sim.observe()))
            sim.advance(policy_match(sim.observe()))
        m = sim.metrics()
        msmi += m['mutual_second_meeting_intention']
        den += m['arrived_members']
    print(f"Total MSMI: {msmi}, Denominator: {den}, Score: {100 * msmi / max(1, den):.4f}")

def baseline_asks(state):
    eligible=[m for m in state['members'] if m['available'] and any(m['fields'][k] is None for k in HARD)
              and not any(m['field_status'][k]=='declined' for k in HARD)]
    return [{'member_id':m['member_id'], 'field': 'constraints'} for m in eligible[:state['ask_budget_remaining']//3]]


def greedy_match(state):
    members=[m for m in state['members'] if m['available']]
    past={tuple(sorted((i['user_a'],i['user_b']))) for i in state['introductions']}
    edges=[]
    for a,b in itertools.combinations(members,2):
        key=tuple(sorted((a['member_id'],b['member_id'])))
        if key in past or eligibility(a,b)['status']!='feasible':continue
        score=sum(a['fields'].get(k) is not None and a['fields'].get(k)==b['fields'].get(k) for k in SOFT)
        edges.append((-score,key))
    used=set();out=[]
    for _,pair in sorted(edges):
        if not used.intersection(pair):out.append(list(pair));used.update(pair)
    return out


print("Baseline Greedy:")
run_test(baseline_asks, greedy_match)
print("Smart Asks + Heuristic + Penalty Match:")
run_test(smart_decide, smart_match)

