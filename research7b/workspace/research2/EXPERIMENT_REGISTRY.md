# Round 2 Experiment Registry

## Seeds
- Development: 4001 - 4040
- Selection: 5001 - 5020
- Confirmation: 6001 - 6040

## Objective
To search explicitly beyond previously tested frameworks (blossom matching, general graph exact planning on fully-observed MDPs) to find a structurally sound policy that improves qualified MSMI/100 by at least +0.10.

## Hypotheses
1. **Scarcity Reservation Penalty**: Statically maximizing matching weights via Blossom double-counts the opportunity costs on sparse edges and matches thick-market highly connected nodes indiscriminately. Using a node-specific scarcity penalty based on single-best alternative bounds reservation accurately without computing complex DP.
2. **Deterministic Information Ask**: Since 'relationship_goal' dominates the generator success logit for Stage 1 (+0.7) and Stage 2 (+0.4 unconditionally in all variants), prioritizing the ask budget to reveal 'relationship_goal' first directly creates edges with up to 5x higher expectation without risky parametric learning bounds.
3. **Robust Prior Ranker**: The previous 'simple' baseline over-smoothed by estimating purely positive terminal outcomes without recognizing local attribute features. The previous 'integrated' baseline suffered Jensen over-forecasting on large variances for missing nodes. Using hard-coded static approximate robust priors for feature weighting strictly suppresses these errors and outperforms uniform scoring.

## Phases
- Stage A/B: Evaluated greedy versus static penalty matching on local Python parallel harnesses (`fast_test.py`, `eval_fast.py`) - established +0.05 to +0.10 expected magnitude.
- Stage C/D: Selection verification running cleanly without invalid constraints.
- Stage E: Frozen confirmation on 6001-6040 versus `greedy`.
