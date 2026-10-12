# Research 7 agent orchestration contract

## Authority, routing and cheap-director design

Use one global four-slot ledger, counting root and every live child/director across both machines. At most 3 workers under one coordinator; children request delegation rather than spawn. Agent slots and simulation processes are distinct; at most 3 sim processes globally (2 Mac + 1 small by default). No agent owns its own simulator pool.

The live planning review used the explicit routes in AGENTS.md: Luna/medium for evidence, Sol/high for critic work, and Astra/high for coupled planning, all with bounded context and `fork_turns=none`. Research 6 JSON/helper currently encode Google aliases and extra Antigravity fields, conflicting with its Markdown/Codex instructions. Leave these historical files unchanged; use provider-specific new adapter and report requested/resolved provider/model/effort. Root's actual runtime is inherited from the host and cannot be retuned by JSON.

| Role/task | Codex route | Direct Gemini preference | Antigravity route | Approval owner |
|---|---|---|---|---|
| Director scheduling/ledger/gates | Existing root; future Sol medium | Flash medium | flash; exposed settings only | Independent technical reviewers; director integrates |
| File finding, bounded reads, mechanical output | Luna low | Flash-Lite low | flash low if flash_lite is unavailable | Director/Sol/Pro interprets |
| Structured extraction, inventory | Luna medium | Flash-Lite medium | flash medium | Stronger review: completeness/denominators |
| Bounded implementation | Sol medium | Flash medium | flash | Independent implementation reviewer |
| Bounded independent review | Sol medium | Flash medium | flash | Sol/Pro for subtle ambiguity |
| Simulator, algorithm, prediction, stats, production, critic | Sol high | Pro high | pro | Own technical conclusions |
| Difficult proof/coupled DP | Astra high | Pro high specialist | pro | Separate strong critic; do not claim model equivalence |

Only low/medium/high task effort is allowed; one escalation per bounded task. Gemini API thinking controls vary by actual model/API: map to supported documented settings during preflight, record the exact request, and never pretend a model tier is a hard thinking-token limit. Model names/prices/account availability can change. Pin the actually available model at future launch using current official docs and exposed tools, no silent fallback.

Antigravity official subagent docs inspected during planning list `inherit`, `flash`, `pro` tiers and clean context; they do **not** establish `flash_lite` as a valid custom-agent tier. Therefore use flash for Antigravity evidence or explicitly available direct Gemini Flash-Lite; record that conscious provider revision. Do not pass Codex fork/model fields to invoke_subagent or Antigravity subagent_type to collaboration.spawn_agent. The new routing JSON is an inert capability policy; the runtime adapter must validate the actual tool schema before delegation.

The cheap director follows registered state transitions. It never selects models by intuition after failures, certifies proofs from worker confidence, invents candidates, rewrites gates, computes E means early or fits private feedback. Its job is to issue bounded work orders, maintain ownership/slots/leases, collect raw evidence, call the named reviewer and apply the fixed decision predicate. Scientific uncertainty triggers a bounded stronger review, not a bigger unbounded search.

## Work-order schema and output contract

Every task states:

- taskID/provider/model/effort and clean context;
- concrete question and falsifiable hypothesis;
- exact input files/source hashes/phase/examined seed restriction;
- exclusively owned files or read-only scope;
- deliverable format with evidence locations and omissions;
- CPU/wall/storage/cell/fit caps, with all-attempt accounting;
- named independent reviewer and escalation path;
- explicitly authorized actions and prohibited dependent work;
- stop condition and handoff dependencies.

Use evidence classes `observed_artifact`, `source_deduction`, `exact_reduced_model`, `approximation`, `untested_hypothesis`, `unknown`. Work response includes status, changed files, evidence/results, raw artifact paths, tested/not-tested scope, resource totals, contradictions and requested next work. Cheap workers return facts; stronger reviewers own scientific/production conclusions.

No developer independently reviews its own candidate or main analysis. If the critic writes a patch, rotate another qualified independent reviewer onto that patch. Do not silently reuse Astra for mechanical inventory; follow-up preserves model/effort. Escalate once only for a specified ambiguity/failure; log the original profile, counterexample, requested replacement, and reviewer. If unavailable, queue or explicitly amend routing; don't exceed high or invent capacity.

## Global waves and file ownership

| Wave | Coordinator | Worker1 | Worker2 | Worker3/critic |
|---|---|---|---|---|
| W0 evidence/contract | Shared registry and input freeze | 7a evidence extractor | 7b simulator forensics | Statistical/causal critic |
| W1 exact/infrastructure | Interfaces/ownership/seed inventory | 7a independent exact + metric developer | 7b recorder/runner developer | Critic, then separate implementation reviews |
| W2 public model/admission | One collector queue/resources | Predictive researcher/fit jobs 7b | 7a leakage/merge checker | Selective-label/stat critic |
| W3 policy development | Configs/candidate admission | Q1/H1/A1/A2 bounded developer | D1/Q2/D2 planning developer 7b | Critic; completed other-worker reviews |
| W4 screen | Registered queue/health | Mechanism analyst | Production engineer | Independent stat critic |
| W5 replication/ablations | Freeze parent graph/promotions | Acquisition/continuation analyst | Independent replicator 7a | Adversarial critic |
| W6 selection/freeze | Chosen ID/n/resources/seal | Production engineer | Independent statistician | Critic/freshness review |
| W7 sealed E | Scheduling/leases/health only | Provenance/log engineer | Independent verifier prepares code | Compliance critic, no effect peek |
| W8 merge/report | Final index/report | Independent counts/statistics 7a | Replay/container/archive 7b | Claim/limit review |

Not all role tasks run concurrently: W1 needs separate implementer/reviewer waves to fit four slots. W3's complex research goes to Sol/high/Astra high by role, bounded implementation subsequently to Sol/medium/Flash. A critic remains engaged in substantive waves; it need not consume an idle background process while waiting but must receive reviews before any gate. Director tracks actual slot availability before every spawn.

Exclusive future paths:

| Owner | Writable paths | Read-only prohibitions |
|---|---|---|
| Coordinator | registry/,decisions.jsonl,delegations.jsonl,planexecutionamendments,launcher,primaryanalysis,finalindex | All old-round results/source unchanged |
| Runner developer 7b | runtime/runner.py,recorder.py,leases.py and focused tests | No statistical gate or registry edits |
| Independent runtime reviewer | reviews/runtime_*.md,independent test fixtures | No implementation patch while independently reviewing |
| Lightweight developer | policies/light.py,history.py,static_allocation.py,specified tests | No heavy planner/shared configs |
| Dynamic developer | policies/continuation.py,models/return.py,plannerfixtures | No independent exact/statistics files |
| Acquisition developer | policies/reward_acquisition.py,answer_model.py,focused tests | No actual eligibility weakening |
| Predictive developer | models/public_*.py,training exports/assets lineage | No E data/private-world imports |
| 7a independentverifier | exact_independent/,metrics_independent.py,merge_independent.py,statistics_independent.py | No mainplanner/analysishelpers |
| Critic | reviews/critic_*.md,statisticsreviews,ownfalsifierfixtures | No developer approval of own patch |

One owned filepath may not be assigned twice. Both machines exchange closed bundles/patches through the coordinator, not concurrent shared-file writes. Merging code requires review/source freezing separately from merging scientific data.

## Concrete work-order examples

**Evidence extraction (cheap).** Question: 'Which R6 stage claims are supported by raw analysis?' Hypothesis: 'REPORT stage counts/means match authoritative JSON.' Read-only REPORT, stage analysis, manifest, and transcript. Return a table with locators, exact numbers, and missing files; no inference or policy recommendation. CPU 30 seconds, response <= 800 words plus artifact. Named reviewer: critic. No episodes/fits/worlds.

**Independent exact test (bounded implementation).** Question: 'Does observable-history DP reproduce T03/T04?' Hypothesis: 'No anticipation and joint-return branching yield the listed rational actions.' Own exact_independent files only; schema provided. CPU 90 minutes for later execution, state cap 100000/case. Reviewer: theory specialist + critic. No official sim worlds. A failed case yields the smallest JSON counterexample; do not change expected values to pass.

**Coupled planning specialist.** Question: 'Does D1 joint-action value avoid double-counting future AC?' Hypothesis: 'Whole-action transition reproduces T07 whereas additive prices fail.' Read legal transition/spec files, own theory note only. CPU 180 seconds analytic planning; later solver compute separately registered. Reviewer Sol/Pro critic. No new reward confirmation.

**Policy implementation.** Question: 'Can Q2 execute one 12-unit non-adaptive package with a real A1 post-answer controller?' Hypothesis: 'The hypothetical controller and deployed controller agree, and all real pairs remain verified.' Own reward_acquisition.py and tests. CPU 120 seconds agent work plus future test work-order budget; independent implementation reviewer. No changing model assets/hyperparameters.

**Independent statistics.** Question: 'Does the full E grid justify all 6 lower bounds > 0?' Hypothesis: 'Raw counts reconstruct the registered cluster endpoint and the same CI.' Inputs: closed public bundle, global registration, frozen STATISTICS. Own independent statistics module/report. CPU 45 minutes, no refits/new samples/policy edits. Reviewer critic. Return all comparisons, failures, and rounding/incomplete-grid checks.

**Mechanical runner monitoring.** Question: 'Are original registered cells progressing durably?' Hypothesis: 'Log-closed chunks and commit set track the planned grid.' Inputs: health ledger only during E. Output counts/errors/disk/CPU/lease conflicts. No MSMI/effect display. Sol/Pro reviewer owns recovery decision. Stop scheduling on resource failure; no budget/sample increase without a pre-E amendment.

## Provider preflight and later start-up prompts

Codex spawn fields: task_name,model,reasoning_effort,fork_turns='none',message. Check live agents before call. Future adapter uses a named logical task kind and the actual schema; it must not reuse the R6 Antigravity helper unchanged.

Antigravity custom agents may use the workspace `.agents/agents/<role>.md` with supported model tier and tools; create them only during later execution setup, verifying current front matter/tool names. Do not install live auto-executing agents as part of this planning task. Direct Gemini calls use an available model ID and supported thinking parameter, recorded in requested/resolved settings. Provider quality match is a preference, not demonstrated equivalence.

Startup 7a: 'Read research7/PLAN_7A.md and common contracts. Execute only the coordinator-issued 7a work orders within limits; use cheap models for facts and independent strong review for claims. Do not run 7b training/screen or inspect E outcomes.'

Startup 7b: 'Read research7/PLAN_7B.md and common contracts. Prepare concrete frozen registration/runner/tests first; respect later user execution authorization, resource caps and 7a handoffs. Do not tune after E or quietly drop the baseline/failed cell.'

These prompts are resumable instructions, not permission to run experiments now.
