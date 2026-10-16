# Prompt for the next testing agent

Paste the complete block below into a coding/research agent opened in this repository. The corrected v2 implementation already exists. This prompt authorizes a fixed development campaign after its gates; it does not authorize changing the policies or repeatedly testing until significance.

```text
MISSION: VERIFY THE REPAIRED EVIDENCE RUNNER, THEN REPLICATE SOFT QUERY FILLING

Repository:
 /Volumes/1700 APFS/PERSONAL_PROGRAMMING_PROJECTS/romio-juliet/The-Sequential-Matching-Problem

All outputs, temporary files, process working directories and test temporary
folders must remain on this external drive. Do not delete unrelated files or
change system settings. A small boot-drive operation guard is already present;
the main storage budget and logs belong to the external drive.

Read before work:
- AGENTS.md and the R6/R7 orchestration contracts.
- research8/soft_query_followup/RECOMMENDATION.md
- research8/soft_query_followup/v2/README.md
- research8/soft_query_followup/v2/review.md
- research8/soft_query_followup/v2/registration.py
- research8/soft_query_followup/v2/runner.py and invoke.py
- research8/soft_query_followup/v2/audit.py and analysis.py
- Original soft_query_trial primary registration and primary_results.json.
- research7/STATISTICS.md for the seed-cluster principle. This new run is
  DEVELOPMENT replication, not the full six-reference R7 confirmation study.

TASK AND AUTHORIZATION
Use the existing v2 implementation. Verify it, freeze fresh registrations,
run the instrumentation smoke, close its evidence gate, and then run the fixed
fresh replication. Finish its independent audit and report. Do not stop after
another plan. Do not modify policy behavior to improve smoke/replication reward.
Follow AGENTS.md model/effort routing and separate developer/reviewer ownership.
Do not spawn nested agent pools. At most six simulation cell workers globally (explicit user amendment);
check other launchers on both machines before launch. The v2 lock coordinates
participating launchers but cannot control unrelated software.

WHAT IS ALREADY FIXED
The new v2 runner:
- Invokes trusted frozen policies in separate cold JSON subprocesses.
- Enforces invocation timeout and bounded input/output; rejects unauthorized
  policy fallback and invalid responses instead of hiding them.
- Keeps world truth in host memory; saves no new private world.json.
- Records public requests, responses, actions, query answers, invocation timings,
  day-level budget/candidate/matching telemetry, released feedback, arrival
  inventory, lifecycle status and final day99 public evidence.
- Hashes all attempt artifacts and binds immutable commits to registration/source.
- Verifies source and registration identities before dispatch/resume.
- Stops on invalid commits/resource failures and retains all failed attempts.
- Uses a repository-wide coordinator lease and at most six cell workers.
- Has a separate independent public-event outcome checker.
- Analyzes six-family averages within seeds and Holm-adjusts every registered
  comparison. It does not turn constant nonzero differences into fake t evidence.

Isolation is process/JSON isolation for trusted code, not an adversarial OS
filesystem/network sandbox. macOS RSS enforcement uses monitored limits and
process termination, not an unsupported claim of kernel RLIMIT_RSS enforcement.
Keep those limitations explicit.

PRESERVE THE ORIGINAL EXPERIMENT
Do not rerun or overwrite the original freeze script, smoke.json, primary.json,
432 commits, reports or policies. The old trial remains preliminary:
- G95, random111, targeted113 qualified dyads across144 episodes/arm.
- Targeted-G=.0625; Holm p=.0842.
- Random-G=.055556; Holm p=.1074.
- Targeted-random=.006944; p=.7956.
These do not establish adjusted5% superiority, targeting equivalence, or a causal
mechanism. Add any interpretation correction as a new review, not an old-file edit.
The old closure checker did not independently reconstruct public event outcomes.
Do not pretend the new logger retroactively fixes that missing evidence.

EXACT UNCHANGED FIVE ARMS
G: original FIFO hard queries and Greedy matching.
G_random_soft: original hard batch plus registered random soft filling.
G_targeted_soft: original hard batch plus registered targeted soft filling.
Q6: unchanged frozen R6 N3_two reference through v2/reference_adapter.py.
P: unchanged frozen population-score reference through v2/reference_adapter.py.

No trained model, VOI algorithm, new salt, altered targeting, solver, waiting,
feature weights or continuation controller may be introduced during these runs.
P/Q6 are frozen reference behaviors, not newly learned model assets. They must
be paired on the same worlds as the candidates; do not compare to archived means.

STEP1: VERIFY IMPLEMENTATION
From repository root:

mkdir -p research8/soft_query_followup/v2/.tmp
PYTHONPATH=. TMPDIR="$PWD/research8/soft_query_followup/v2/.tmp" \
 python3 -m pytest research8/soft_query_followup/v2/tests \
 research8/soft_query_trial/tests/test_policies.py -q \
 --basetemp research8/soft_query_followup/test_temp_v2

The current suite contains82 tests plus2 subtests, verified across the initial
70-test run, later guard/analysis checks, and six-worker guard tests.
One test uses a declared4-member fixture and120 cold calls, not fresh empirical
reward evidence. Do not count tests or repeated portability calls as study cells.
If tests fail, preserve the attempt, identify the failure and obtain independent
review before freezing any changed infrastructure version. Do not edit expected
outcomes just to pass. Keep scientific policy behavior unchanged.

Verify the original primary source_manifest still matches old source files.
Verify the preserved constructed capture independently:

PYTHONPATH=. python3 -m research8.soft_query_followup.v2.audit \
 --registration research8/soft_query_followup/v2/validation/declared_fixture_registration.json \
 --output research8/soft_query_followup/v2/validation/declared_capture

That one-cell fixture registration is intentionally not a campaign registration.
Never pass it to the campaign launcher.

STEP2: INVENTORY AND REVIEW FRESH SEEDS
Choose exactly4 smoke seed groups and96 replication seed groups, disjoint from
each other and every previously examined/reserved group. Do not assume that
larger numbers are fresh. Do not commit proposed seed lists before their first
inventory scan, or the scanner will conservatively see your own reservation.

Use the metadata scanner:

PYTHONPATH=. python3 -m research8.soft_query_followup.v2.registration audit-seeds \
 --seeds "COMMA_SEPARATED_EXPLICIT_SEEDS" \
 --output research8/soft_query_followup/campaign_v2/SMOKE_OR_REPLICATION_seed_audit.json

Audit smoke and replication separately. Inspect collisions, archives_not_decoded,
and unreadable_or_oversized. The scanner excludes private world.json and states
its repository-visible scope. It does not certify universal freshness.
Have an independent evidence reviewer reconcile omitted archives/metadata against
prior inventories, registrations and reservations. If unresolved, select another
namespace or finish the inventory; do not approve an unexplained omission.

Save a review JSON for each audit, for example:
{
 "status":"accepted_repository_visible_freshness",
 "proposed_seeds":[EXACT_ORDERED_SEEDS],
 "audit_sha256":"SHA256_OF_THE_AUDIT_FILE_BYTES",
 "reviewer":"NAMED_INDEPENDENT_REVIEWER",
 "archive_omissions_disposition":"SPECIFIC_RECONCILIATION_AND_SCOPE",
 "unreadable_omissions_disposition":"SPECIFIC_RECONCILIATION_IF_ANY"
}
Do not fabricate the review or claim there were zero omitted archives if present.
All same-seed families/arms stay in the same stage. Every inspected group remains
development permanently.

STEP3: FIX RESOURCE FORECAST AND FREEZE THE SMOKE
The instrumentation smoke now uses all five arms so P/Q6 adapter, resource and
logging compatibility are tested before replication:
-4 fresh seed groups ×6 families ×5 arms =120 episodes.
-This supersedes the proposed72-cell three-arm instrumentation smoke; no old
  completed72-cell experiment is altered.

Check external-drive free space, no other active simulator campaign, source
review, runtime dependencies and environment versions. Existing ceilings are:
-6 cell workers; invocation wall≤10s; request/response wire1MiB.
-attemptCPU90s including child processes; attemptwall180s; monitoredRSS4GiB per worker tree and8GiB combined.
-results-drive free reserve≥10GiB; small boot operation reserve≥.25GiB.
These are guard ceilings, not evidence the forecast fits. Record Python/SciPy
versions and runtime platform in the campaign evidence. Do not increase a cap
after a failure. If a legitimate infrastructure amendment is required, review
and refreeze it before primary replication, preserving the failed smoke version.

Freeze after all executable files, tests and analysis are stable:

PYTHONPATH=. python3 -m research8.soft_query_followup.v2.registration freeze \
 --stage R8V2_instrumentation_smoke \
 --seeds "FOUR_EXPLICIT_SMOKE_SEEDS" \
 --arms G,G_random_soft,G_targeted_soft,Q6,P \
 --freshness-audit research8/soft_query_followup/campaign_v2/smoke_seed_audit.json \
 --freshness-review research8/soft_query_followup/campaign_v2/smoke_seed_review.json \
 --output research8/soft_query_followup/campaign_v2/smoke_registration.json

The tool writes once and checks a complete ordered grid, unchanged policy/config
identities, all source dependencies, freshness receipts, caps and analysis.
Do not edit source after freezing. Do not run the old launcher or old freeze.py.

STEP4: RUN AND AUDIT THE SMOKE
Use a new output directory on this external drive:

PYTHONPATH=. python3 -m research8.soft_query_followup.v2.launcher \
 --registration research8/soft_query_followup/campaign_v2/smoke_registration.json \
 --output results/research8/soft_query_followup/v2_smoke \
 --workers 6

PYTHONPATH=. python3 -m research8.soft_query_followup.v2.audit \
 --registration research8/soft_query_followup/campaign_v2/smoke_registration.json \
 --output results/research8/soft_query_followup/v2_smoke

Require all120 cells, zero policy-invalid commits/unauthorized fallback, exact
public-event metric reconstruction, source/world/denominator identity, complete
120-call per-cell streams, correctly released feedback and recorded query budget.
Report active200-member cold invocation maxima, actual throughput, CPU, output
size and projected replication storage/runtime. Never quote the4-member test
latency as proof of full-population speed.

Check mechanism opportunities: actual daily slack; eligible candidates; soft
answers; changed matching decisions. Pre-answerG versus post-answer action is an
own-history diagnostic and can include hard-query effects, not causal soft-only
attribution. Same aggregate hard asks across different histories is not proof
of identical day-level hard schedules.

Smoke reward means cannot tune rules, choose seeds or decide which unfavorable
arms to omit. The smoke gate concerns implementation, evidence and resources.
If it fails, preserve the evidence and correct infrastructure before a new freeze.

STEP5: FREEZE THE FIXED REPLICATION
After the smoke gate and independent review close, use96 untouched replication
seed groups ×6 families ×5 unchanged arms =2880 primary episodes.
No sequential extension or stopping when a favorable p-value appears.

Seven predeclared exploratory contrasts:
- Randomsoft−G, Randomsoft−Q6, Randomsoft−P.
- Targetedsoft−G, Targetedsoft−Q6, Targetedsoft−P.
- Targetedsoft−Randomsoft.

For each contrast, D_s = mean of its six family differences within seed s.
Use96 independent seed groups, not576 independent seed-family pairs.
Endpoint =100 * qualified_dyads / arrived_members_by_day59, zero if no arrivals.
Each qualifying dyad counts once.60 action +40 follow-up days; cut feedback at99.
Mutual first acceptance, happened date within30days, distinct positive endpoint
second intentions within3days of date, and all required feedback released by99.
Day59 introductions retain eventual follow-up credit.
Report paired means, seed-clusterSD/SE, exploratory95% intervals and Holm-adjusted
seven-comparison summaries. Family results remain descriptive. A significant
contrast is not a full six-reference panel-confirmation verdict.

Freeze using the same command with:
 --stage R8V2_soft_replication
 --seeds "96_EXPLICIT_REPLICATION_SEEDS"
 --arms G,G_random_soft,G_targeted_soft,Q6,P
 --freshness-audit .../replication_seed_audit.json
 --freshness-review .../replication_seed_review.json
 --output .../replication_registration.json

STEP6: EXECUTE FIXED GRID AND RECONSTRUCT BEFORE ANALYSIS

PYTHONPATH=. python3 -m research8.soft_query_followup.v2.launcher \
 --registration research8/soft_query_followup/campaign_v2/replication_registration.json \
 --output results/research8/soft_query_followup/v2_replication \
 --workers 6

PYTHONPATH=. python3 -m research8.soft_query_followup.v2.audit \
 --registration research8/soft_query_followup/campaign_v2/replication_registration.json \
 --output results/research8/soft_query_followup/v2_replication

Do not inspect reward summaries until the entire fixed grid closes. Monitor only
progress, errors, resource use and evidence health. Every failed attempt remains
preserved. Committed policy invalidity blocks that version. Infrastructure-only
interruptions may resume the same registration and cells after independent
recovery review; never replace seeds, discard unfavorable cells or choose retries.
Do not count replays as independent new worlds. If sources changed, original
registration cannot resume; preserve it and explicitly review a new version.

Only after successful complete-grid audit:

PYTHONPATH=. python3 -m research8.soft_query_followup.v2.analysis \
 --registration research8/soft_query_followup/campaign_v2/replication_registration.json \
 --output results/research8/soft_query_followup/v2_replication \
 --report research8/soft_query_followup/campaign_v2/replication_results.json

STEP7: INDEPENDENT STATISTICS AND HONEST REPORT
A different reviewer independently computes qualification and96seed-cluster
contrasts from public evidence and reconciles exact counts/means/SE/CI/Holm values.
Publish all seven comparisons and all five policies; report negative outcomes.
Audit interpretation claims against raw results:
- Positive development gain is not guaranteed population improvement.
- Nonsignificance is not equivalence or proof of no benefit.
- Relative percentages are point estimates, not causal certificates.
- Field revelation, surrogate score gains and funnel averages do not establish
  the mechanism or eventual-reward improvement.
- Compare every candidate to its ownGparent and contemporaneousQ6/P.
- Do not claim all-family safety from nonsignificant family tests.

Recommend one next action:
-Repeatable gains againstG,Q6,P: select one unchangedcandidate for a separately
 registered fresh full-panel confirmation, with variance/resource planning.
-G gains but notQ6/P: study a better public scorer; do not claim panel superiority.
-No replication: preserve the negative result and simplify/reconsider acquisition.
-Targeted/random uncertainty: do not assert equivalence; choose further complexity
 by explicit cost/effect/uncertainty evidence rather than its name.

Deliver implementation verification, freshness reviews, immutableregistrations,
all raw public evidence, attempts/guard reports, independentreconstruction,
fixed statistical report and a short plain-language conclusion.
Do not addVOI,D1,training or an extra policy during this experiment.
Proceed autonomously through the authorized gated work; report exact blockers.
```

## Six-worker amendment

The user explicitly authorized six simulation workers. This supersedes the older three-simulation-worker preference; the four-agent concurrency/routing contract remains unchanged. This host has10physical/logicalcores and16GiBRAM. Six workers are supported, but not presumed faster or empirically safe until the fixed smoke passes active timing, memory and storage gates. The launcher enforces an8GiB combined monitored worker-treeRSS ceiling in addition to4GiB per-tree limits. Use six for the smoke; freeze the actual chosen replication concurrency from its resource forecast before replication. No active campaign or new frozen registration existed when this change was made. Prior source snapshots are preserved under `../history/before_six_workers/`.
