# Exact structural cases and the adaptive renewal relaxation

Developer: `/root/exact`, routed Astra/high for the proof and coupled planning
question. Independent reviewer: a separately assigned Sol/high critic. This is
developer evidence, not independent review closure. No simulator worlds,
evaluation seeds, fitting, or reward confirmation are used.

## Scope and executable contract

`python3 -m research6.exact.run` registers source hashes and complete model
specifications **before** compiling or solving, in a fresh timestamped directory
under `results/research6/stage_a_exact/`. It then saves every reachable MDP state,
action, rational transition probability, and Bellman action value. Existing
attempts are never overwritten. `python3 -m unittest research6.exact.test_exact`
runs the focused development checks. All probability/reward/value arithmetic is
`Fraction`; timing and filesystem metadata are not part of that claim.

The matching model's state is decision index, busy-release vector, retired
endpoints, and used dyads. An action is any endpoint-disjoint unused matching,
including empty. Each scheduled edge has expected eventual reward q, joint
retirement probability p with 0≤q≤p≤1, and a failure duration d≥1. Simultaneous
retirement events are independent. Retirement becomes observed by the next toy
decision; other endpoints return at assignment day+d. We book q at assignment
and never book that reward again. Its realized reward could be coupled as a
subset of retirement with conditional probability q/p. This produces the same
expected Bellman values because only the additive expected immediate reward is
needed and no unmodeled latent parameter is learned from that reward.

All listed future edge/calendar information is public **in these toy models**.
This differs from the simulator's partial observations, unknown exits and
delayed feedback. Neither these exact optima nor any schedule here is delivered
to an evaluated simulator policy. Information experiments instead explicitly
enumerate their revelation branches and subsequent available actions.

The 79 fixed additional cases are all 64 labelled four-node graphs, three odd
cycles of lengths 3/5/7, and 12 two-dyad horizon/probability changes including
zero horizon. They are separate constructed validation inputs, not independent
statistical observations or simulator holdout seeds. A second development
implementation enumerates every deterministic Markov policy and recursively
evaluates it, checking every state's action value against backward induction.
The larger named examples may exceed its 100,000-policy cap and record that
omission. A distinct vertex-recursive matching enumerator also checks all 64
graphs. These checks share a developer and cannot satisfy the plan's separate
independent-enumerator ownership requirement by themselves.

## Structural findings

| Required case | Exact reduced-model result | Permitted inference |
|---|---|---|
| Complementary verification | F(∅)=F(A)=F(B)=0, F(AB)=1 | Ordinary diminishing returns fails for this immediate verification objective |
| Collision versus distinct partners | Shared batch 24/25; distinct 7/5; degree sums 8/5 and 7/5 | Degree sum can prefer a worse query batch |
| Four-node path repair | Middle 11/100 versus disjoint outer total 1/5 | Length-three augmentation improves this example |
| Reversed reward magnitudes | One edge 9/10 versus two edges 1/5 | Cardinality is not a universal reward objective |
| Unit triangle | Matching 1; degree LP 3/2; adding odd-set row yields 1 | Node capacity alone does not characterize general-graph matching |
| Known return | AB today 11/100; BD then AC 1/5; deleting future AC makes AB optimal | Reservation depends on alternatives and their timing |
| Soft information and displaced hard query | Prior choice 1/2; free reveal 7/10; reveal minus 1/4 is 9/20 | Gross information value 1/5 can have net loss 1/20 |
| Nonrepeat triangle at days 0/8/16 | 1−(9/10)^3=271/1000; only day 0 gives 1/10 | Reuse across different dyads matters; repeats are forbidden |
| Nonseparable alternatives | Joint current assignments 1; waiting 9/10; each separate continuation loss 9/10 | Adding standalone assignment losses double-counts the same future alternative |
| Last action day | Existing reward 1/5; adding disjoint edge gives 3/10 | Nonnegative disjoint reward helps with full follow-up; does not identify a gap in already maximal G |
| Single introduction, no affected later choice | Expected reward 1/2, with no exploitable later action | Information about that resolved attempt has no decision benefit |

For nonseparability, future AC gives V({A,C})=9/10 and V({A})=V({C})=V(∅)=0.
The nonzero mixed difference refutes an exact sum of independent node values.
In the two-current-assignment example, AB and CD each earn 1/2 and certainly
retire endpoints. Individually subtracting a 9/10 loss rejects both, earning
9/10 tomorrow; taking both earns 1. This refutes the specific additive loss
reduction, not the usefulness of every approximate price in every market.

**A1 requires a qualification.** “No-return model” alone does not imply zero
learning value. The added `no_return_can_still_have_learning` case has a fair
shared regime. An earlier disjoint introduction never returns and earns no
reward, but its public outcome reveals which of two later conflicting choices
earns one. Expected future reward rises from 1/2 to 1. The zero-value statement
is sound when there is no later decision whose feasible action or expected
utility changes with the observation, or when the remaining affected action
set is empty. Occupancy is still a real cost when it blocks later alternatives;
the waiting counterexample charges that cost explicitly. This distinction
matters especially for a shared-regime learner.

Inherited evidence is retained: round-three waiting (9/10 versus immediate
1/10), retry (21/25 versus waiting 4/5), throughput on the last day (q/d chooses
1/5 although 3/10 is optimal), the earlier static greedy trap (6/5), known
arrivals (8/5), early exit (4/5), and stochastic returning market (709/1000).
An isolated-assignment construction reproduces future opportunity losses
0,0,1/2,0 over four days with duration two and a fair day-three arrival. The
last-day zero refers to **future** opportunity loss; it does not say that
same-day competing alternatives have zero cost.

Terminal qualification and retirement differ. In the added penalty example,
two current edges each earn q=1/10, but one pauses with probability 1 and the
other with probability 1/10. With a unit future alternative and failure release
after one day, their forced values are 1/10 and 1. Using q as the pause
probability erases this difference. Waiting also earns 1, so the example proves
the penalty mismatch without claiming a unique initial optimum. Full follow-up
also means a long busy duration cannot reduce the eventual reward of a final
assignment when there is no later assignment opportunity.

## Renewal occupancy theorem under adaptive public histories

**Proposition (ideal independent-stream model).** Fix Z containing all member
profiles, actor parameters, regime and actual arrival/exit schedules. Suppose,
conditional on Z, each potential unused dyad/day assignment (e,t) has a fresh
outcome stream W(e,t) independent of policy randomization and all information
available before that assignment is selected. A policy may adapt arbitrarily
to its permitted public history, but never observes an unassigned stream. It
chooses legal matchings and never repeats a dyad. Suppose an assignment blocks
each endpoint continuously from assignment until its release, and if it
permanently pauses the endpoint, the pause occurs no later than release. All
eventual counted rewards are nonnegative, bounded, and retained after exits.
There are finitely many assignment days and members.

Let X(e,t) be the assignment indicator. Define a potential reward R(e,t) and
potential assignment-caused occupancy U_i(e,t;s) for each endpoint i∈e and
decision day s≥t, as functions only of Z and W(e,t). Occupancy counts whether
that assignment prevents use of i at s, including its assignment day; thus
U_i(e,t;t)=1. For a permanent pause use occupancy through the horizon, including
the preceding busy interval. If an endpoint exits, one may continue this
potential interval after exit: there can be no later legal assignment of it.
Define x(e,t)=E[X(e,t)|Z], q(e,t)=E[R(e,t)|Z], and
u_i(e,t;s)=E[U_i(e,t;s)|Z]. All expectations here condition on fixed Z, **not**
on an assignment-selected posterior averaged with unconditional coefficients.

Then every legal adapted policy maps to a feasible point of

    maximize  Σ_(e,t) q(e,t) x(e,t)
    subject to x(e,t) ≥ 0,
               Σ_t x(e,t) ≤ 1                         for each dyad e,
               Σ_(e∋i,t≤s) u_i(e,t;s) x(e,t) ≤ 1      for each i,s.

Variables outside legal arrival/exit/action-day and full-hard-truth windows
are absent. Removing query costs and disclosure requirements is an optimistic
relaxation. Any omitted dyad must truly be impossible under every feasible
policy considered; ignoring permanent hard declines is safe but looser.

**Proof.** On each legal trajectory, assignment-caused occupancy intervals of
an endpoint cannot overlap. A new assignment is legal only after every prior
one has released and before any permanent pause. By the no-gap assumption a
future pause cannot start after a subsequent assignment became legal. Hence
Σ_(e∋i,t≤s) X(e,t)U_i(e,t;s)≤1 pathwise. Nonrepeat gives Σ_t X(e,t)≤1.

For a fixed candidate (e,t), X(e,t) is measurable with respect to the
preselection history and policy randomness. Conditional on Z, W(e,t) is fresh
and independent of that history, including histories that have selected
particular actor types or inferred their parameters. Thus

    E[X(e,t) U_i(e,t;s) | Z] = x(e,t) u_i(e,t;s),
    E[X(e,t) R(e,t) | Z]     = x(e,t) q(e,t).

Taking expectations in the pathwise constraints proves feasibility. Finite
linearity of expectation gives the objective as the policy's expected eventual
reward. Maximization over the larger feasible LP set bounds that expectation.
Adaptive public histories have not been restricted beyond nonanticipation.
If Z is random, integrating gives E[reward]≤E[LP*(Z)]. This is neither a
pathwise realized-reward ceiling nor generally LP evaluated at averaged
coefficients. ∎

The source timing needed for the no-gap condition is explicit in `kit.py`:
nonmutual assignments use busy=t+8; mutual assignments use busy=date+6;
second feedback arrives by date+5; a positive pause starts after both observed
seconds. The earliest mutual date is t+2, so even that release is at least
t+8. Pause therefore precedes release. An exit does not cancel scheduled
outcomes. These source deductions establish the interval structure; they do
not establish mathematically independent streams for the finite seeded PRNG.

Conditioning on Z is essential. Suppose a public signal reveals a fair latent
short/long duration type. Assign the first dyad only for short type, when it
releases before tomorrow; assign a second incident dyad tomorrow in both
histories. This legal policy has x_first=1/2 and x_second=1. Averaging the first
potential occupancy over the prior gives u=1/2, so using prior coefficients
incorrectly reports tomorrow's capacity as 1/4+1=5/4; its true occupancy sum is
1. Similarly, assign only a publicly revealed reward-one type and skip the
reward-zero type. Actual reward is 1/2, while prior q times assignment
probability is 1/4. Both tables are evaluated with rational arithmetic in the
runner. Conditional on either fixed type the theorem holds. A public-belief
LP would instead need history-indexed variables and correct conditional
coefficients, or a proved valid envelope; the proposed fixed coefficient
factorization cannot silently use population priors.

## Numerical certification and current status

Three small LPs have explicit rational primal and dual witnesses. The triangle
degree relaxation has x=(1/2,1/2,1/2), node dual=(1/2,1/2,1/2), value 3/2.
Adding the odd-set row gives value 1 with unit multiplier on that row. For
the two-day renewal toy, q=(1/2,1/2), constraints are x0≤1 and
(1/2)x0+x1≤1. Primal (1,1/2) and dual (1/4,1/2) both give 3/4, agreeing with
the exact dynamic model. The omitted endpoint/dyad rows are redundant here;
they can be added with zero dual multipliers. The certificate checker verifies
all inequalities with exact rational arithmetic. This certifies those LPs
only, not a full-simulator numerical bound.

For a certified numerical relaxation of the theorem, objective coefficients
must enclose q from above, and occupancy coefficients must enclose u from
below. This increases objective rewards and relaxes constraints. A feasible
nonnegative dual with A_minus^T y≥q_plus then certifies upper value b^T y;
all numerical residuals need outward control or exact rational checking.
Using upper occupancy coefficients instead can exclude a legal expected
schedule and invalidate the bound. Gaussian quadrature convergence alone is
not an enclosure, and a solver's floating objective is not a dual certificate.

**Status:** the symbolic conditional theorem is proved here subject to its
stated assumptions and pending separate critique; tiny rational LPs and
simplified dynamic models are exact. Full-simulator occupancy integration,
outward bounds on continuous-latent integrals, and numerical LP certificates
remain unimplemented/unvalidated. No simulator headroom value or empirical
candidate improvement is inferred from these constructions.
