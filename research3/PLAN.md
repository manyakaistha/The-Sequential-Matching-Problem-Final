# Round 3: research plan and ownership

Started 9 October 2026. All inherited studies remain in place. This round writes
only `research3/` and `results/research3/`. Initial inherited hashes are recorded
before experimentation. Current policy sources differ from the previous freeze;
this discrepancy is evidence to preserve, not permission to rewrite history.

Director owns registry, policy wrapper, runner, analysis, decisions and final
package. Three concurrent agents occupy the remaining three actual slots:

| Agent | Roles | Exclusive files | Allowance | Reviewer |
|---|---|---|---|---|
| forensics | simulator audit, information acquisition | FORENSICS.md, forensic_audit.py, forensics.json | 10 CPU min, one worker | critic |
| theory_models | theory, prediction, dynamic allocation | THEORY_MODELS.md, tiny_models.py, model_candidates.py, tiny_models.json | 10 CPU min, one worker | critic |
| critic | adversarial review, statistics | CRITIC.md, STATISTICAL_PLAN.md, seed_inventory.py, seed_inventory.json | 10 CPU min, one worker | director |

Assignments and falsifiable questions are recorded in the thread and each agent's
deliverable. Later waves rotate independent replication, implementation review and
production/provenance roles. No nested agents increase the four-slot global limit.
Simulation pools use at most two processes; avoid concurrent expensive analysis.

Sequence: inherited read/audit; register seeds and hypotheses; correctness and
tiny falsification; diverse full-horizon screening; focused paired development and
ablations; independent selection; freeze; fixed confirmation; independent replay;
production verification; compressed artifacts and final manifest. No candidate or
sample is retuned in response to confirmation.

The practical target is +0.10 scenario-balanced qualified MSMI/100. Evidence may
instead support a negative finding or simpler comparable behavior. Predictive
accuracy, toy optimality and oracle diagnostics do not establish policy gain.

Outstanding research is tracked in DECISIONS.md; observations, deductions,
approximations and hypotheses must remain distinguishable in all reports.
