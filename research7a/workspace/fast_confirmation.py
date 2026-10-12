import sys
import os
import json
import itertools
from kit import Simulator, generate, VERSION, HARD, SOFT, eligibility

import policy
import policy_greedy

def adapt_policy(module, state, phase):
    return module.decide({'phase': phase, 'state': state}).get('asks' if phase == 'ask' else 'pairs', [])

def run_sim(args):
    seed, variant, policy_name = args
    sim = Simulator(generate(seed, 200, variant=variant))
    mod = policy if policy_name == 'smart' else policy_greedy
    
    for _ in range(60):
        obs1 = sim.observe()
        asks = adapt_policy(mod, obs1, 'ask')
        sim.resolve_asks(asks)
        
        obs2 = sim.observe()
        matches = adapt_policy(mod, obs2, 'match')
        sim.advance(matches)
        
    m = sim.metrics()
    return {'msmi': m['mutual_second_meeting_intention'], 'den': m['arrived_members']}

if __name__ == '__main__':
    seeds = range(6001, 6041)
    variants = ['development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift']
    
    tasks_greedy = [(s, v, 'greedy') for s in seeds for v in variants]
    tasks_smart = [(s, v, 'smart') for s in seeds for v in variants]
    
    res_greedy = [run_sim(t) for t in tasks_greedy]
    res_smart = [run_sim(t) for t in tasks_smart]
        
    greedy_msmi = sum(r['msmi'] for r in res_greedy)
    greedy_den = sum(r['den'] for r in res_greedy)
    
    smart_msmi = sum(r['msmi'] for r in res_smart)
    smart_den = sum(r['den'] for r in res_smart)
    
    print('Greedy baseline overall msmi:', greedy_msmi)
    print('Smart overall msmi:', smart_msmi)
    
    import numpy as np
    smart_family = []
    greedy_family = []
    
    for v_idx, v in enumerate(variants):
        sm = sum(res_smart[s_idx * 6 + v_idx]['msmi'] for s_idx in range(40))
        sd = sum(res_smart[s_idx * 6 + v_idx]['den'] for s_idx in range(40))
        gm = sum(res_greedy[s_idx * 6 + v_idx]['msmi'] for s_idx in range(40))
        gd = sum(res_greedy[s_idx * 6 + v_idx]['den'] for s_idx in range(40))
        
        smart_family.append(100 * (sm) / sd)
        greedy_family.append(100 * (gm) / gd)

    final_smart = np.mean(smart_family)
    final_greedy = np.mean(greedy_family)
    
    diff = final_smart - final_greedy
    
    with open('research2/eval_output.txt', 'w') as f:
        f.write("### Evaluation vs Baseline (Confirmation 6001-6040 x 6 Variants)\n")
        f.write("- **Greedy Baseline MSMI/100**: {:.4f}\n".format(final_greedy))
        f.write("- **Proposed Policy MSMI/100**: {:.4f}\n".format(final_smart))
        f.write("- **Absolute Improvement**: {:+.4f}\n".format(diff))
        
        if diff >= 0.10:
            f.write("\n> [!NOTE]\n> **Target MET!** We successfully verified +0.10 expected absolute MSMI density improvement.")
        else:
            f.write("\n> [!WARNING]\n> **Target MISS!** Expected improvement fell short.")
