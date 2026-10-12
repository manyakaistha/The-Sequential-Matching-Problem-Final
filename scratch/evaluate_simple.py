import json
import numpy as np

def update_predicted(data):
    # Calculate simple predictions manually using the memory from the logs
    for d in data:
        memory = d['memory']
        counts = memory.get('simple_funnel', [[11.7,8.3],[3.6,16.4],[2.8,17.2],[.65,19.35],[.234,19.766]])
        probabilities = [a/(a+b) for a,b in counts]
        d['simple_terminal'] = probabilities[4]

with open('scratch/outcomes.json', 'r') as f:
    data = json.load(f)

update_predicted(data)

y_terminal_true = np.array([1 if d['y_terminal'] else 0 for d in data])
y_terminal_prob = np.array([d['simple_terminal'] for d in data])

print(f"Total samples: {len(y_terminal_true)}")
print(f"Event rate (terminal): {y_terminal_true.mean():.4f}")
print(f"Mean predicted (terminal) (simple): {y_terminal_prob.mean():.4f}")

