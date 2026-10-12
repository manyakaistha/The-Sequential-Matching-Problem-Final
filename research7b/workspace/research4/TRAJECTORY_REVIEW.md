# Descriptive trajectory review

The director inspects completed public trajectories, with separate privileged
conditional-quality sums supplied by the previously labeled mechanism audit.
These inspections occur after the relevant stage and do not alter any policy,
selection rule or confirmation test. They are exploratory, not causal mediation.

## Focused verification priority versus population scoring

Largest seed-balanced gain: 81030, effect +1.166667 MSMI/100. Across its six
families priority yields 18 qualified pairs against four, whereas the privileged
conditional-quality difference is only +0.007626 MSMI/100. Both ask and match
choices diverge at day zero in all six families. Only 14–26 dyad/day introductions
are shared per family; these shared introductions have identical complete events.

Largest loss: 81018, effect -0.750000, with one versus ten qualified pairs.
Conditional-quality difference is -0.001071. Ask choices diverge at day zero;
matching diverges day zero except sparse day one. Shared dyad/day counts range
9–36. The overall focused parent effect is +0.031250. Removing one seed at a time
ranges from -0.005376 to +0.056452. Removing the largest-gain seed reverses the
point effect. This is influential-seed evidence, not proof that chance is the
exclusive explanation.

## Frozen population scoring versus shipped greedy

Confirmation mean effect is +0.056548; leave-one-seed-out means range +0.043939
to +0.066667. Thus no single seed reverses its positive point estimate, although
the full registered confidence interval crosses zero. Representative largest
seed gain is 83003; largest loss is 83040. In both representative clusters the
entire hard-query schedules are identical across all six families. Matching
choices differ. Common dyad/day introductions have byte-identical event rows;
common dyads assigned on different days do not share outcome draws.

Across all 56 clusters the privileged current-edge conditional-quality sum effect
is +0.000328, exploratory CI [-0.005549,+0.006205]. The deadline-integrated
positive-pause effect is +0.019286, CI [-0.011865,+0.050436], compared with the
realized +0.056548. Better matched edges are not established by this audit.
Favorable date/response/acceptance/second and qualification draws remain plausible
alternatives; adapted future occupancy makes simple descriptive mediation invalid.

## Random-variable sharing

Shipped kit.py initializes each introduction's generator from world seed,
canonical endpoints and assignment day. It reuses a Gaussian shared effect across
acceptance/second stages and the actor's response parameter across submissions.
For identical dyad/day introductions in the same family, complete outcomes are
identical independent of matching-list ordering. Different dyads or assignment
days select other streams. Families share a seed and generator structure and
are treated as one seed cluster, not independent worlds for inference.

The inspection verifies common complete events without reverse engineering or
feeding outcome streams into policies. Introduction identifiers and completed
public labels are read only offline. It gives no deployable prediction of future
draws. Actor/soft truths enter only the separate labeled quality audit.

Raw summaries, exact first divergent actions and trace references:
results/research4/trajectory_review_focus.json and
results/research4/trajectory_review_confirmation.json. Reproduce using
`python3 -m research4.trajectory_review` and its explicit input/candidate/control
arguments recorded in the command ledger, writing a fresh output path.
