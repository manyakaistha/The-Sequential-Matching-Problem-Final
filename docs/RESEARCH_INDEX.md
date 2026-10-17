# Research index

The [final report](../final_report/REPORT.md) is the current synthesis. Earlier reports remain available with their original results and reviews; they are not all statements of the final conclusion.

## Core material

| Topic | Entry point |
|---|---|
| Original task | [Problem statement](../PROBLEM_STATEMENT.md) |
| Data and missingness | [Data contract](DATA_CONTRACT.md) |
| Policy inputs and outputs | [Policy interface](POLICY_INTERFACE.md) |
| Retained implementation | [policy.py](../policy.py) |
| Reference semantics | [kit.py](../kit.py), [evaluate.py](../evaluate.py) |
| Final results and plots | [Report](../final_report/REPORT.md), [assets](../final_report/assets/) |
| Rebuild report figures | [Report README](../final_report/README.md) |

## Research history

| Work | Entry points |
|---|---|
| Initial research and Round 1 | [Research directory](../research/), [submitted Round 1 PDF](../final_report/sources/round1_submission.pdf), [historical root report](../REPORT.md) |
| Research 2 | [Report](../research2/FINAL_REPORT.md) |
| Research 3 | [Report](../research3/FINAL_REPORT.md), [decisions](../research3/DECISIONS.md) |
| Research 4 | [Report](../research4/FINAL_REPORT.md), [provenance reconciliation](../research4/PROVENANCE_RECONCILIATION.md) |
| Research 5 | [Report](../research5/FINAL_REPORT.md), [reproduction](../research5/REPRODUCTION.md) |
| Research 6 | [Report](../research6/REPORT.md), [experiment registry](../research6/EXPERIMENT_REGISTRY.md) |
| Research 7 | [Overview](../research7/README.md), [execution guide](../research7/execution_guide/README.md), [7a](../research7a/README.md), [7b](../research7b/README.md) |
| Research 8 | [Overview](../research8/README.md), [soft-query follow-up](../research8/continuation_probe/PREVIOUS_RESULTS.md), [continuation decision](../research8/continuation_probe/DECISION.md) |
| Learned-policy campaign | [Plan](../research9/final_campaign/CAMPAIGN_PLAN.md), [selection record](../research9/final_campaign/selection.json), [closure](../research9/final_campaign/campaign_closed.json) |
| Supplemental feedback studies | [Source and results](../research9/round2/); use [the corrected final analysis](../final_report/REPORT.md) when interpreting these studies |

## Reading historical results

Keep development screens, toy calculations, replay checks and untouched confirmation separate. A plan or implementation is not evidence that its proposed experiment completed. Policy names can also refer to different components: FIFO is a questioning order; Greedy is an allocation rule; P is a population-based reference, not the random baseline.

The supplemental Round 2 report has known statistical and interpretive errors. It remains as a historical record; the final report and its source tables contain the corrected seed-cluster analysis. No replacement policy established confirmatory superiority over Greedy.

Prompt-only testing handoffs and redundant report-preparation notes were removed on the cleanup branch. Operational and scientific records, including registrations and review provenance, remain. See [cleanup scope](REPOSITORY_CLEANUP.md).
