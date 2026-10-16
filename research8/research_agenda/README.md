# Research package: practical paths beyond Greedy

Read [REPORT.md](REPORT.md) first. It integrates repository evidence, primary research, mathematical arguments, an independent critique, and a finite development plan. [theory.md](theory.md) contains the conditional improvement proofs; [model.md](model.md) gives the public-data likelihood/schema and practical policy designs; [final_review.md](final_review.md) records independent checks and limits.

Two important historical corrections emerged:

* The P4 report's displayed MSMI/100 values are twice the stored normalized endpoint; stored G=.343750, P=.376736, Q6=.378472. Proper96-seed-cluster exploratory intervals for P−G and Q6−G include zero.
* G/P/Q6 recorded no soft asks. Frozen R uses random matching and FIFO hard queries, not random soft querying.

The recommended first mechanism test is a hard-first slack-soft acquisition control, alongside explicit missingness/soft-weight scoring and same-score local allocation repair. The more demanding theory route evaluates a small library of complete policies through day59 and retains the selected continuation across days. It includes multi-day holds, because one-step Greedy rollout can miss consecutive-wait opportunities even with a full horizon.

Reproduce the declared rational examples:

```bash
python3 research8/research_agenda/check_theory_examples.py
```

Reproduce the historical commit-metric audit (host-side research tool, requires installed SciPy):

```bash
python3 research8/research_agenda/reconstruct_commit_metrics.py
```

Both commands print JSON without modifying historical sources/results. The latter is a commit-metric reconstruction, not an independent reconstruction of every public feedback event.

No model was fitted and no new simulator episode was run in this package. It does not admit a production policy or establish superiority. Future campaigns require their own frozen code/assets, seed separation, finite budgets and full own-parent controls; user permission is not an extra scientific gate. Existing W2 continues its documented G behavior.
