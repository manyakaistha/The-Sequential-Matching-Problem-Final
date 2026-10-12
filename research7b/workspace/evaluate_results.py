import json

with open('research2/confirmation.json') as f:
    smart = json.load(f)

with open('research2/confirmation_greedy.json') as f:
    greedy = json.load(f)

smart_score = smart['summary']['primary_score']
greedy_score = greedy['summary']['primary_score']

diff = smart_score - greedy_score
print(f"Smart Candidate Priority Score (MSMI/100): {smart_score:.4f}")
print(f"Greedy Baseline Priority Score (MSMI/100): {greedy_score:.4f}")
print(f"Difference: {diff:+.4f} MSMI/100")

if diff >= 0.10:
    print("\nSUCCESS! Targeted +0.10 absolute improvement achieved!")
else:
    print("\nDid not meet +0.10 target.")
