# R7 statistical design and adversarial safeguards

Owner: r7_critic, gpt-6.1-sol/high. Reviewer: director `/root`. Planning only. Read-only examination of R6 and analytic noncentral-t calculations; no simulator, world generation, fitting or new research seeds. Exclusive deliverable: this file. The counts and resource ceilings below are proposed fixed choices for the director's registration, not execution authority.

## What R6 established, and what it did not

The authoritative E artifact (`results/research6/stage_e_confirmation/confirmation_analysis.json`) reports N3_two minus G: n=571 independent seed clusters, mean +0.003210741 MSMI/100, paired SD .256046575, SE .010715216, 99% CI [-.024482542,+.030904024], two-sided p=.764558570. Superiority was not established. The interval excludes the +.05 planning target for this frozen contrast. It neither establishes zero effect/equivalence, nor proves G optimal, nor excludes other query/planning mechanisms. Bootstrap agreement is a sensitivity check, not proof that finite-sample t coverage is exact.

The R6 REPORT and stage_e_critic overstate three conclusions. (1) Equal-and-opposite cold_start/delayed sample means do not identify the causal mediator of attenuation. Delayed also shifts the date calendar and PRNG consumption; controlled intervention with registered RNG semantics and matched worlds is needed. Stage B's N3 delayed effect was +.0875, while C's was -.05833: the subgroup narrative is not a stable independently demonstrated law. (2) N3_fifo4 had identical reward on the C grid; this is a scoped observation about that implementation and 60 clusters, not a theorem that query capacity has zero value. (3) N3_two's similar C/D point estimates do not prove it captures 100% of a benefit, equivalence to N3, or a causal decomposition. E establishes no benefit to partition. G is the supported production default, not an empirically proven universal champion. Zero committed invalid episodes does not automatically certify zero failed or interrupted attempts.

No R6 files should be rewritten. Preserve them and give corrected interpretation in R7's evidence ledger. R7 starts with unvalidated hypotheses, not an established latency diagnosis or a promised positive result.

## Fixed endpoint and baseline panel

Use the unchanged six-family benchmark F={development,sparse,cold_start,delayed,shift,drift}, n=200 generated members, 60 decision days plus drain to simulator day100. Let Q_psf be the qualified terminal MSMI count and A_psf the arrived-member denominator at the registered metrics horizon for policy p, seed s, family f. Define

    Y_psf = 100 Q_psf / A_psf
    D_sj = (1/6) sum_f (Y_Csf - Y_Bj,sf)
    Delta_j = E_s[D_sj]
    mean_j = (1/n) sum_s D_sj
    sd_j^2 = (1/(n-1)) sum_s (D_sj - mean_j)^2
    SE_j = sd_j / sqrt(n).

Whole seeds are independent sampling units. Families and policies sharing a seed are correlated. Do not treat 6n episodes, introductions or actors as independent, pool terminal counts into a differently weighted endpoint, normalize by served members, change family weights after results, or substitute model scores/positive pauses/coverage for qualified reward. Report Q and A separately. Check A and initial-world digests across policies; policy-dependent denominators are a correctness concern. Count unique admitted seed IDs, not machine-local seed counts.

Freeze six comparator implementations before development reward grids:

- G: exact shipped greedy default.
- N: the official no-asks baseline, frozen without extra clarifications.
- R: the official random baseline, with its legal action/RNG behavior frozen.
- P: frozen population-control policy used in R6, not a newly retuned model.
- K: frozen maximum-cardinality control, separating scoring/planning from matching volume.
- R6: frozen N3_two, separating a new mechanism from the strongest previously selected acquisition contender.

Use exact policy/config/source hashes, not names alone. These are benchmarks, not six proven optimal policies. Candidate-specific architecture controls remain in C and must isolate the proposed module: equal query budgets/timing, equal allocation scorer/order, and equal public information where appropriate. If a baseline cannot pass correctness/resource checks, resolve before new stage seeds are generated; never silently drop it because it is strong or inconvenient. A different panel is possible only as an explicit pre-execution registration revision.

## Multiplicity, practical gain and noninferiority

Confirm at most one independently selected candidate against all six baselines on one fixed E grid. Allocate R7's reporting family alpha=.01; simultaneous two-sided Bonferroni intervals are

    I_j = mean_j +/- t_(1-.01/(2*6), n-1) SE_j  (99.833333% each).

Bonferroni does not require independent contrasts. Individual positive superiority statements use L_j>0. The headline 'superior to the fixed baseline panel' requires all six L_j>0; failure of one means the panel claim fails, while individually valid comparisons may still be reported. An intersection-union test could test only the joint claim at alpha .01 without Bonferroni, but this proposal chooses simultaneous intervals so individual claims and failed-panel outcomes remain interpretable. Do not select the weakest comparator after E.

Choose practical margin delta_prac=.025 MSMI/100 before execution. Distinguish (a) statistical superiority L_j>0, (b) observed gain mean_j>=.025, and (c) established practical superiority L_j>.025. For practical superiority to the panel, require (c) for all six. The director's proposed promotion gate is all L_j>0 plus observed mean versus G>=.025; this is statistical panel superiority with an observed practical-size gate, not an established .025 gain. A true gain of .05 is the power target for rejecting zero; a true gain of .075 is the power target for establishing a .025 margin with the same .05 separation. Do not call the design effect an established gain. These numbers are explicit benchmark design choices, not a product-derived business value; the owner may revise them before registration with rationale.

Choose NI margin m_NI=.05 only if an NI statement is wanted. The same simultaneous panel intervals support NI if all L_j>-.05, without additional searches. NI is not superiority and does not itself justify replacing G; 'no significant harm' is not NI. Equivalence needs both endpoints inside a predeclared [-m,+m] and is a different claim.

Family effects are secondary by default: publish all six means and intervals, including negative slices, without a latency causal claim. A policy can win the balanced endpoint and harm one family. If deployment requires every family to be NI to G, register a second gate in advance with six simultaneous lower bounds using critical t_(1-.01/(2*6),n-1), all >-.05, and size for that gate separately. Serial gatekeeping opens this NI family only after all primary panel nulls are rejected, giving strong familywise control at .01 across the primary-then-safety hierarchy; unadjusted diagnostic slices cannot substitute. Its high cost is visible below. Do not add family NI as a confirmatory story after seeing E. The recommended initial plan uses descriptive family diagnostics, not a promised universal family safety claim.

Alpha=.01 is a round-specific family guarantee, conditional on valid tests and leak-free execution. R6's original fixed alpha=.01 and earlier reports remain unchanged. It is not a .01 or .05 lifetime guarantee for arbitrary future rounds. A program-wide guarantee requires a separately frozen alpha-spending ledger including existing rounds; serially assigning each round .01 forever is invalid.

## Fixed staged funnel and finite budgets

Proposed maximum grid, chosen for distinct mechanisms rather than a hyperparameter sweep:

| Stage | Fresh seed clusters | Maximum policies | Maximum episodes | Frozen question/gate |
|---|---:|---:|---:|---|
| A legality/headroom | Existing examined examples only | Six proposed mechanisms and controls | No fresh reward grid | Legal public-only actions, exact constructed examples, mechanism can change decisions |
| B screen | 48 | 12 = six panel controls + six new mechanisms | 3,456 | Eligible/correct/resource-safe; effect vs G >=.025; predicted mechanism metric changes; keep at most two mechanisms |
| C own-parent replication | 64 | 12 total including panel and ablations | 4,608 | Reward direction replicates, module contribution nonnegative in registered contrast; strongest alternative explanation addressed |
| D frozen selection | 96 | 8 = panel + at most two contenders | 4,608 | Candidate has mean vs G >=.025 and one-sided90% lower vs G >0; other panel means >=0; choose highest minimum one-sided90% lower across panel, tie within .005 favors simpler/faster |
| E fixed confirmation | variance-sized n <=1,800 | 7 = panel + one candidate | <=75,600 | One fixed sample and simultaneous primary intervals; retain result regardless of outcome |

B/C/D are exploratory credibility gates, not significance or proof of superiority. All candidate and own-parent effects are reported; Holm adjustment can summarize the complete prespecified exploratory comparison graph without promoting it to confirmation. No D candidate means stop without E. Do not loosen gates, add variants, recycle rejected thresholds or extend D until somebody qualifies. A candidate needing more than the available own-parent controls must displace another before C registration or be deferred.

Illustrative full-grid cap is 88,272 episodes and 208+1,800 fresh seed clusters; the director may divide these into bounded 7a/7b phases before registration. If learning is needed, authorize at most 240 additional training/validation clusters, at most six collectors, 8,640 episodes, with disjoint whole-seed folds; this adds a separate stage before B, not an option activated after disappointing D/E. Conditional learning total cap is 96,912 episodes. A concrete main CPU ceiling must accommodate the pilot forecast: at 5 CPU seconds/episode the no-learning maximum is 122.6 CPU hours and the learning maximum 134.6 CPU hours before operational overhead. Proposed aggregate ceilings are 160 CPU hours main simulation, 20 CPU hours operational verification/archive/replay and 10 CPU hours fitting (total 190); the director may choose a smaller staged grid/budget rather than authorize this maximal grid. These are ceilings, not usage estimates. Costlier inference may make the grid inadmissible. Forecast from already examined seeds with the actual recorder/policy, including failed attempts and full logs; no assumed parallel speedup makes total CPU cheaper.

Disk budget: director's proposed new-evidence ceiling is 100GiB with roughly 173GiB currently free. Old R6 logs reportedly use about 80GB for 6,852 episodes (~11.7MB/episode), so the maximal E alone would approach 885GB under the old layout. Full lossless compressed content-addressed deduplication and a measured pilot are prerequisites; do not assume the storage reduction exists. Estimate compressed full evidence bytes per episode on existing examined seeds, require complete-stage forecast*1.25 plus >=20GiB reserve on every executing host and the merge host. A stage unable to fit is deferred before fresh worlds. Resource guard stops are operational incomplete results, never lower-n significance analyses. No old evidence deletion is authorized. Per-invocation deployability still requires the unchanged timeout/payload/memory/container rules; a large offline pool does not relax them. Proposed stage budgets should be reconciled explicitly with the director's resource choices before executable registration.

## Variance-only sample-size rule and honest power

Freeze selection code/config, margins, alpha, power, n cap and formula before inspecting E. Use selected candidate's D paired differences against every baseline, never E outcomes:

    sigma_j = max(.30, 1.10*sd_D,j).
    n_j = smallest integer n>=2 with
          nct.sf(t.ppf(1-.01/(2*6),n-1), n-1,
                 .05*sqrt(n)/sigma_j) >= 1-.10/6.
    n_E = ceil(1.10*max_j n_j).

Here each contrast has >=98.333333% assumed power, so the union bound gives >= 90% probability all six reject when every true margin separation is at least .05. This is an exact noncentral-t calculation under an IID normal seed-difference model, not guaranteed simulator power. The sigma floor and 10% factors are heuristics, not upper confidence bounds. Candidate action divergence can increase variance. For a .025 practical certificate, .05 in the noncentrality means truth .075 versus null .025. If the desired true gain is only .05 but the claim threshold is .025, substitute .025 as separation before registration and accept the much larger cost.

| Assumed paired seed SD | 90% per-comparison n with 10% inflation | >= 90% joint-power n with 10% inflation |
|---:|---:|---:|
| .26 |589|833|
| .30 |783|1,107|
| .35 |1,062|1,504|

First column uses each comparison at90%; it does not guarantee90% joint success. Calculated locally using existing scipy; no RNG/simulator called. n_E>1,800 means do not execute this confirmatory power promise. Stop, or publish an explicitly lower-powered fixed study only after a pre-E amendment that keeps its tested hypotheses honest. Never reduce the SD after E, alter target based on E, unlock unused reserve seeds, extend to significance, or continue confirmation across new machines until the lower bound crosses zero.

Six-family NI can dominate budget. At margin .05, truth zero and simultaneous six-family intervals, SD=.50 needs 2,161 clusters for 90% power per family (not 90% all families); SD=.65 needs 3,647. Those already exceed the proposed E cap. Estimate D family SDs and size the conjunction before promising this safety gate. Do not assert six-family NI just because primary-panel sizing was adequate.

## Freshness, information restrictions and pairing

Do not allocate numeric R7 seeds in this planning document. Build a new read-only inventory over every round's raw results, plans/reserves, registries, compressed metadata, replays, smoke examples, training logs and external-machine declarations. Include all R6 used/reserved partitions, especially 140001–142000 even though E used only 140001–140571. Prior reserved-but-unrun seeds remain blocked until explicitly released by reviewed amendment. Unknown prior external seed usage is an acknowledged limitation; 'not in final rows' does not mean fresh. Do not run inventory tools that mutate sealed historical directories.

Separate examined development/training, B, C, D and E partitions; whole-seed splits. Reserve does not authorize generating every reserved world. A world is consumed as soon as it is generated, inspected or used in fitting/diagnostics, even without a completed episode. Never try E seeds on a second host as a 'smoke test' before confirmation. Verification replays use prespecified already evaluated seeds and remain verification, not added observations.

Pair each policy on the same seed/family initial world, n, pool identifier and horizon. Canonical initial-world digest must match across policies. Source and environment hashes include kit/evaluate, generator/simulator code, imported policy/model modules, configuration, model artifact/preprocessor, exact dependencies and container digest. Hashes prove consistency of supplied bytes, not time of freeze or absence of leakage; independently closed registration and access separation supply the latter evidence.

RNG caveats matter: `generate` consumes one seeded stream with variant-dependent branches; same numerical seed across families does not imply the same latent actors. `Simulator.advance` uses `rand_for(seed,a,b,day)` per introduction; different policies change dyad/date keys. In delayed, an extra draw also shifts subsequent per-introduction draws. Common seeds reduce some noise but do not hold every realized funnel outcome fixed across policies. Paired statistical estimands remain valid under the registered coupling; mediation or 'same dyad counterfactual' claims need an explicitly designed intervention. Do not retrofit a new counter-based generator only for one policy or compare to old-generator baselines. A simulator/RNG revision is a new benchmark requiring all panel policies and clear provenance.

Evaluated policies see only the prospective public request plus their legal memory. No scenario label, seed, generator state, hidden truth/response propensities, future calendar or privileged teacher features. Public regime estimation must use feedback already arrived; missing/censored and selected labels do not become IID actor observations. Models train/calibrate on permitted prior partitions and remain frozen during D/E except explicitly registered per-episode public online updates. Cross-E-episode learning, hidden E outcomes and selection-condition updates are prohibited. Proper-score gains and exact-toy solutions are secondary mechanism evidence, not reward promotion by themselves.

## Multi-machine execution and leak-proof merge contract

One director-owned immutable global registration contains the complete stage cell set and no machine creates its own seeds or candidate grid. Use identity

    cell_key=(experiment_id, stage, seed, family, policy/config hash)

and retain attempt UUID separately. Freeze ordered seed list; shard by seed index modulo number_of_hosts, keeping every family/policy for a seed on its assigned host. This avoids cross-host pairing differences. The host count changes scheduling, not n or inference. Pool size across hosts is one predeclared global offline-worker cap (suggest 6 for two hosts, otherwise retain 3); do not infer authorization for an unbounded pool. Root plus three live agents remains a different four-slot limit.

Each host receives identical source/model/container snapshots and its own disjoint cell manifest, writes exclusively to its shard directory, and records platform/dependencies/thread settings, source hashes, world digests and resource use. Before fresh stages, deterministically replay previously examined fixed requests/worlds on each host; compare ordered actions, semantic actions, memory and metrics. Float/tie nondeterminism must be resolved before E. Host-specific policies or float libraries changing decisions are benchmark variants, not interchangeable replicates.

Retain full append/attempt evidence including prospective requests, returned wire bytes, stdout/stderr, errors, fallback status, action digests, timing/resource records and host-private audit worlds. Host-private audit data are never mounted or exposed to policy/model processes. Close and fsync independently decompressible invocation chunks and commit only after durable artifacts/hash/size checks. R6's exclusive file creation and atomic hard-link commit are useful patterns, but its machine-local absolute attempt_path is not a portable merged artifact identity; use root-relative artifact IDs plus a manifest mapping each origin shard without rewriting sealed rows.

A durable first committed cell is authoritative, including committed failure. Retries are allowed only for missing/uncommitted original cells after documented infrastructure recovery; preserve every abandoned attempt. A committed invalid policy episode is never replaced by a later successful run or a new seed. The stage fails eligibility or remains an explicitly incomplete result under its registered failure rule; correctness repairs require a new development phase, not editing E. Never choose among multiple outputs based on reward. A transfer retry is byte-copy retry, not an experiment rerun. If an original missing cell is reassigned, the scheduler first revokes its old lease and verifies no commit exists; source/seed/config remain unchanged. Late duplicate commits are quarantined, not averaged or counted twice.

Merge independently verifies registration/source/config identity, exact expected set, one authoritative row per cell, episode validity, closed artifact hashes/sizes, full invocation count/horizon and matched initial-world digest. Byte-identical transport duplicates deduplicate to one cell with provenance retained. Conflicting duplicate scientific results are a hard stop for investigation, not first-arrival/best-result selection. Reject foreign/unregistered cells. Require complete six-family/seven-policy clusters before E analysis; no failed-cell deletion or per-machine subset p-values. Do not run meta-analysis of host estimates or count machines as replicates: assemble global D_sj then perform the frozen seed-cluster analysis once.

For E the director/health display receives counts, errors, resource/disk state and remaining original cells only. E outcomes and effect summaries stay sealed from candidate developers/selection until the full grid and all operational reviews close. All machines halt optional analysis; there is no weakest-host extension or federated tuning. Independent replicator reconstructs the raw endpoint, pairing, complete denominators and all CIs without importing director analysis helpers; bootstrap resamples entire seeds jointly across all policies/families with a fixed analysis-only RNG. Standard bootstrap sensitivity does not alter the primary rule. Sign flips are not automatically exact because policy assignment labels were not randomized and symmetry is an additional assumption.

Archive restoration rejects traversal, symlink destinations and unexpected members, validates SHA/size and exact complete file set. Source/manifest hashes alone are not a substitute for raw evidence or a tamper-proof timestamp. Reviewer-owned reports must close before final seal; later objections receive a separate amendment preserving original evidence. Final report names null/negative results, missing-grid limitations, every baseline, every searched candidate and all deviations. A failed superiority result is a completed scientific outcome; keep G unless separate explicit production criteria and evidence justify change.
