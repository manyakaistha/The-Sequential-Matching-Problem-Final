import json
import itertools
import math
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kit import Simulator, generate, eligibility, HARD, SOFT
from evaluate import docker_command, invoke, strict_json, VERSION
from extended_policy import decide as decide_extended
from policy import decide as decide_greedy

def get_true_eligibility(world):
    members = world['members']
    edges = []
    for a, b in itertools.combinations(members, 2):
        # build deep copy but with truth for fields
        a_true = dict(a, fields=a['truth'])
        b_true = dict(b, fields=b['truth'])
        if eligibility(a_true, b_true)['status'] == 'feasible':
            edges.append((a['member_id'], b['member_id']))
    return set(tuple(sorted(x)) for x in edges)

def run_funnel(policy_name, seed):
    world = generate(seed, 200, 'dev', 'development')
    sim = Simulator(world)
    
    true_feasible_edges = get_true_eligibility(world)
    num_hard_feasible = len(true_feasible_edges)
    
    memory = None
    if policy_name == 'greedy':
        cfg = None
    else:
        cfg = {"model": "simple"}

    daily_stats = []

    for day in range(60):
        obs = sim.observe()
        
        # ASK PHASE
        req_ask = {'schema_version': VERSION, 'phase': 'ask', 'state': obs, 'memory': memory}
        if policy_name == 'greedy':
            res_ask = decide_greedy(req_ask, 'greedy')
        else:
            res_ask = decide_extended(req_ask, cfg)
        
        memory = res_ask['memory']
        sim.resolve_asks(res_ask['asks'])
        
        # MATCH PHASE
        obs = sim.observe()
        req_match = {'schema_version': VERSION, 'phase': 'match', 'state': obs, 'memory': memory}
        if policy_name == 'greedy':
            res_match = decide_greedy(req_match, 'greedy')
        else:
            res_match = decide_extended(req_match, cfg)
            
        memory = res_match['memory']
        sim.advance(res_match['pairs'])

    # advance to resolve all events
    for _ in range(40):
        sim.advance([])

    # Verify feasible pairs at the end
    obs = sim.observe()
    obs_members = {m['member_id']: m for m in obs['members']}
    revealed_feasible = 0
    for a_id, b_id in true_feasible_edges:
        if a_id in obs_members and b_id in obs_members:
            if eligibility(obs_members[a_id], obs_members[b_id])['status'] == 'feasible':
                revealed_feasible += 1

    # Assignment analysis
    introductions = sim.introductions
    events = sim.events

    funnel = {
        'assignments': 0,
        'nonresponse_stage1': 0,
        'rejection_stage1': 0,
        'mutual_acceptance': 0,
        'date_cancelled': 0,
        'date_happened': 0,
        'nonresponse_stage2': 0,
        'rejection_stage2': 0,
        'mutual_second_intention': 0,
        'deadline_disqualified': 0,
        'valid_msmi': 0
    }

    for intro in introductions:
        funnel['assignments'] += 1
        intro_id = intro['introduction_id']
        es = [e for e in events if e['introduction_id'] == intro_id]
        
        # Responses
        rs = [e for e in es if e['event'] == 'introduction_response']
        responded = sum(1 for r in rs if r['missing_reason'] != 'no_response')
        
        if responded < 2:
            funnel['nonresponse_stage1'] += 1
            continue
            
        accepted = sum(1 for r in rs if r['value'] == 'yes')
        if accepted < 2:
            funnel['rejection_stage1'] += 1
            continue
            
        funnel['mutual_acceptance'] += 1
        
        # Date
        ds = [e for e in es if e['event'] == 'date_happened']
        if not ds or not ds[0]['value']:
            funnel['date_cancelled'] += 1
            continue
            
        funnel['date_happened'] += 1
        
        # Second intentions
        ss = [e for e in es if e['event'] == 'second_meeting_intention']
        s_responded = sum(1 for s in ss if s['missing_reason'] != 'no_response')
        
        if s_responded < 2:
            funnel['nonresponse_stage2'] += 1
            continue
            
        s_accepted = sum(1 for s in ss if s['value'] == 'yes')
        if s_accepted < 2:
            funnel['rejection_stage2'] += 1
            continue
            
        funnel['mutual_second_intention'] += 1
        
        # Deadlines
        date_occ = ds[0]['occurred_day']
        assigned_day = intro['assigned_day']
        late_date = date_occ - assigned_day > 30
        
        late_feedback = False
        for s in ss:
            if s['value'] == 'yes' and s['occurred_day'] - date_occ > 3:
                late_feedback = True
                
        if late_date or late_feedback:
            funnel['deadline_disqualified'] += 1
        else:
            funnel['valid_msmi'] += 1

    metrics = sim.metrics()
    
    return {
        'num_hard_feasible': num_hard_feasible,
        'revealed_feasible': revealed_feasible,
        'funnel': funnel,
        'msmi_per_100': metrics['msmi_per_100_arrived_members']
    }

def print_audit():
    seeds = list(range(2001, 2011))
    
    for rp in ['greedy', 'simple_fifo']:
        stats = {
            'num_hard_feasible': [],
            'revealed_feasible': [],
            'msmi_per_100': [],
            'f_assignments': [],
            'f_nonresp1': [],
            'f_reject1': [],
            'f_mutual': [],
            'f_date_cancel': [],
            'f_date_yes': [],
            'f_nonresp2': [],
            'f_reject2': [],
            'f_mutual2': [],
            'f_deadlines': [],
            'f_valid': []
        }
        for s in seeds:
            res = run_funnel(rp, s)
            stats['num_hard_feasible'].append(res['num_hard_feasible'])
            stats['revealed_feasible'].append(res['revealed_feasible'])
            stats['msmi_per_100'].append(res['msmi_per_100'])
            f = res['funnel']
            stats['f_assignments'].append(f['assignments'])
            stats['f_nonresp1'].append(f['nonresponse_stage1'])
            stats['f_reject1'].append(f['rejection_stage1'])
            stats['f_mutual'].append(f['mutual_acceptance'])
            stats['f_date_cancel'].append(f['date_cancelled'])
            stats['f_date_yes'].append(f['date_happened'])
            stats['f_nonresp2'].append(f['nonresponse_stage2'])
            stats['f_reject2'].append(f['rejection_stage2'])
            stats['f_mutual2'].append(f['mutual_second_intention'])
            stats['f_deadlines'].append(f['deadline_disqualified'])
            stats['f_valid'].append(f['valid_msmi'])
            
        print(f"--- POLICY: {rp} ---")
        print(f"MSMI/100: {np.mean(stats['msmi_per_100']):.3f}")
        print(f"Num hard-feasible possible pairs: {np.mean(stats['num_hard_feasible']):.1f}")
        print(f"Revealed verified feasible possible pairs: {np.mean(stats['revealed_feasible']):.1f}")
        print(f"Assignments (Starts): {np.mean(stats['f_assignments']):.1f}")
        print(f"|- Nonresponse Stage 1: {np.mean(stats['f_nonresp1']):.1f}")
        print(f"|- Rejection Stage 1: {np.mean(stats['f_reject1']):.1f}")
        print(f"|- Mutual Acceptance: {np.mean(stats['f_mutual']):.1f}")
        print(f"   |- Date Cancelled: {np.mean(stats['f_date_cancel']):.1f}")
        print(f"   |- Date Happened:  {np.mean(stats['f_date_yes']):.1f}")
        print(f"      |- Nonresponse Stage 2: {np.mean(stats['f_nonresp2']):.1f}")
        print(f"      |- Rejection Stage 2: {np.mean(stats['f_reject2']):.1f}")
        print(f"      |- Mutual Second Intention: {np.mean(stats['f_mutual2']):.1f}")
        print(f"         |- Deadline Disqualified: {np.mean(stats['f_deadlines']):.1f}")
        print(f"         |- Valid MSMI (Success): {np.mean(stats['f_valid']):.1f}")
        print()

if __name__ == '__main__':
    print_audit()
