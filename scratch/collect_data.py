import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kit import Simulator, generate
from research.terminal_model import predict_funnel, update_memory, FEATURES
from research.extended_policy_development import decide, fallback
import json

def collect_from_seed(seed):
    world = generate(seed, 200, 'evaluation', 'development')
    sim = Simulator(world)
    memory = {}
    cfg = {'model': 'integrated', 'engine': 'greedy'}
    
    logs = []
    
    for _ in range(60):
        state = sim.observe()
        memory = update_memory(state, memory, cfg)
        
        import policy
        action_asks = policy.decide({'phase': 'ask', 'state': state})['asks']
        sim.resolve_asks(action_asks)
        
        state = sim.observe()
        action_pairs = policy.decide({'phase': 'match', 'state': state})['pairs']
        
        for a_id, b_id in action_pairs:
            m_a = next(m for m in state['members'] if m['member_id'] == a_id)
            m_b = next(m for m in state['members'] if m['member_id'] == b_id)
            pred = predict_funnel(m_a, m_b, state, memory, cfg)
            
            from research.terminal_model import equality_probabilities
            eq = equality_probabilities(m_a, m_b)
            
            logs.append({
                'seed': seed,
                'day': state['day'],
                'user_a': a_id,
                'user_b': b_id,
                'eq': eq,
                'pred_integrated': pred
            })
            
        sim.advance(action_pairs)
        
    for _ in range(40):
         sim.advance([])
         
    state = sim.observe()
    feedback = state.get('feedback', [])
    
    outcomes = []
    for log in logs:
        intro = next((i for i in sim.introductions if (i['user_a'] == log['user_a'] and i['user_b'] == log['user_b']) or (i['user_b'] == log['user_a'] and i['user_a'] == log['user_b'])), None)
        if intro:
            events = [e for e in feedback if e['introduction_id'] == intro['introduction_id']]
            responses = [e for e in events if e['event'] == 'introduction_response']
            responded = len(responses) == 2
            mutual_accept = responded and all(e['value'] == 'yes' for e in responses)
            
            dates = [e for e in events if e['event'] == 'date_happened']
            date_hap = len(dates) > 0 and dates[0]['value'] is True
            
            seconds = [e for e in events if e['event'] == 'second_meeting_intention']
            mutual_second = date_hap and len(seconds) == 2 and all(e['value'] == 'yes' for e in seconds)
            
            outcomes.append({
                **log,
                'y_response': responded,
                'y_mutual_accept': mutual_accept,
                'y_date': date_hap,
                'y_terminal': mutual_second
            })
            
    return outcomes

if __name__ == '__main__':
    all_outcomes = []
    for seed in range(101, 111):
        print(f"seed {seed}")
        all_outcomes.extend(collect_from_seed(seed))
    
    with open('scratch/outcomes_with_seed.json', 'w') as f:
        json.dump(all_outcomes, f)
