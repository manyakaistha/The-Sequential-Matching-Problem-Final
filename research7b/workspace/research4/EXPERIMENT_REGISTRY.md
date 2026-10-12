# Round 4 experiment registry

Written before fresh evaluations,10 October2026. Preserve round3 confirmation
and all sources. No fitting uses round3 confirmation or future seeds. Round3
observations may suggest hypotheses, but cannot be untouched again. All inherited
seed inventory and every round3 planned/examined seed are excluded. Fresh ranges
below80000 were not used here; reserves80001 onward must match completed inventory
before execution. Privileged state is never an evaluated policy input.

## Frozen candidate set and hypotheses

| Candidate | Mechanism | Falsifiable comparison |
|---|---|---|
| greedy | shipped asks/match | baseline |
| population_control | public joint funnel, FIFO queries | stronger nonlearning control |
| goal_surplus_control | population+remainingbudget goal asks | acquisition parent |
| coordinated_goal | up to3FIFO hard bundles+samebatch goal | versus goal_surplus_control |
| hard_priority | public partial compatibility priority | versus population_control |
| response_beta_control | momentmatched Beta response prior | feedback parent |
| response_uniform | exact uniform response moments | versus response_beta_control |
| acceptance_shrinkage | Gaussian .7prior actor acceptance update | versus response_uniform |

All allocations remain legal greedy descending positive scores, canonical ties.
No new source or configuration changes after B. Learned quantities use resolved
public events only, priors fixed from shipped law. Acceptance posterior ignores
partner/shared posterior and trialregime coupling and uses Gaussian moment
matching; this is an explicit approximation, requiring prospective diagnostics.
No endpoint prices or separable occupancy optimality claim. Detailed assumptions
in MECHANISMS.md. Memory{}; wrapper7second guard, legal emptyfallback, cap1MiB.

## Stages and deterministic advancement

A: previously examined seed101development, all8; protocol/tiny posterior tests,
source correctness review. New source may change only before B. Record hashes.

B:80001–80012, all6families, all8candidates=576episodes. Exploratory screen.
Promote top2 new candidates excluding greedy and population_control, ordered by
primary mean then alphabetical, irrespective significance. C always includes
greedy and population_control and each promoted candidate's own control:
coordinated_goal→goal_surplus_control;hard_priority→population_control;
response_uniform→response_beta_control;acceptance_shrinkage→response_uniform;
goal_surplus_control→population_control;response_beta_control→population_control.
No recursive control expansion. Holm over all7 candidate−greedy contrasts.

C:81001–81032, all6families, above set. Serious32cluster focused comparison.
Prelisted ablations are exactly coordinated_goal−goal_surplus_control,
hard_priority−population_control,response_uniform−response_beta_control, and
acceptance_shrinkage−response_uniform, when both
policies exist, Holm across all present contrasts. Compare proper scores on the
identical greedy prospective cohort, public labels, no fitting/calibration changes.
Promote top2 nonbaseline candidates (population_control eligible), sorted by mean
then alphabetical. D includes those2 plus greedy and population_control.

D:82001–82020, all6families, independentselection. Among eligible new candidates
within .025MSMI/100 of best D mean choose lowest engineering cost, then highest
mean then alphabetical. Costs: population_control0,goal_surplus_control1,
coordinated_goal1,hard_priority2,response_beta_control2,response_uniform2,
acceptance_shrinkage3. Band is engineering choice, not statistical equivalence.
All stages require exact plannedgrid, zero invalid/failure/fallback. If none valid,
stop advancement and preserve failures rather than replacing a candidate silently.

E:83001 onward, exactly selected frozen candidate versus greedy all6families.
Fixed n=min(160,max(40,ceil(1.10*((1.959964+.841621)*max(.21,CpairedSD)/.10)^2))).
Use population_control C variance only if selected absentC. Record n,seedlist,
source/configuration and registry hashes before any E generation. Complete all
fixed cells with60action+40followup. No earlysuccess stop, sampleextension,
retuning, substitute candidate or repeated tests to reach significance.

## Statistics and reporting

Primary scenario-balanced qualified MSMI/100: mean six episode ratios perseed,
then paired mean across independent seedclusters. Practical target+.10. Registered
superiority iff positive lower endpoint of two-sided95%Studentt pairedCI (alpha.05),
complete/valid/zero fallbacks. Estimate exceeding+.10 is distinct from CI excluding
+.10. Nonsignificance is not equivalence.10,000whole-seed percentile bootstrap
RNG90210 sensitivity; scenario means and leave-one-seed-out exploratory. Respect
six correlated families perseed. Report allsearched candidates, unadjustedCI,
Holm screen/ablation corrections, failures, stage counts/probabilities with proper
denominators, coverage, occupancy/repeatopportunities, pause/deadline losses,
querycosts, latency mean/p95/p99/max, request/memorysizes, productionparity.

Two simulationworkers maximum. Offline research resources separate from inference.
Current observed round3~2–3wallseconds/episode perworker; expected B~12–18minutes,
C~13–40minutes dependingcontrols, D~6–10minutes,E~8–20minutes. Record measured wall
and childCPU, not invented estimates. No external paid resource spend. Package
independent selected replay, criticism/rebuttal, production checks, allraw episode
rows/prospective snapshots, calibration/mechanism analyses, losslessarchives,
restoration instructions, final source/config provenance. Negative result remains
useful; this round will not search indefinitely for a significant seedset.

## Repeated-round research-program claim

The valid old extended, round3 and round4 primary confirmations form a family of
three tests. Retain registered round4 nominal95%CI/p, but a program-wide verified
superiority claim additionally requires p<.05/3=.016666667 and positive lower
endpoint of Bonferroni98.333333% pairedtCI. This correction accounts for these
three completed valid comparisons only, not an unbounded future research series.
The invalid research2 no-followup experiment supplies no superiority test. This
round ends after its fixed confirmation regardlessresult; further experiments
would need another directive and new multiplicity plan. Report both nominal and
program-wide gates, even if one passes and the other fails. Greedy prospective
traces record match-time public states (ask_log omitted, not used by models) for
identical-example prediction; records never enter evaluated policy inputs.
