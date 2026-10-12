#!/bin/bash
source .venv/bin/activate
SEEDS=$(python -c "print(','.join(map(str, range(6001, 6041))))")
python evaluate.py --seeds $SEEDS --variants all --policy policy.py --baseline greedy --output research2/confirmation.json > research2/confirmation.log 2>&1
python evaluate.py --seeds $SEEDS --variants all --policy policy_greedy.py --baseline greedy --output research2/confirmation_greedy.json > research2/confirmation_greedy.log 2>&1
