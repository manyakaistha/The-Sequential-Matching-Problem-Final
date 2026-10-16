# Independent selection/statistics/proof-reuse review

2026-10-15; `/root/continuation_critic`, integrating reviewer `/root`.
Read-only analyze.py and registration.py, fixed protocol and fit result admission
state. Allowance90 CPU seconds/five minutes. No policy reward outcome inspected,
research fitting or simulator episode performed.

## Statistical and selection findings

The fitted funnel failed the prespecified probability gate. Registration
correctly limits screening to model_greedy/model_soft/model_repair plus G/Q6/P;
D is omitted. ABC remain explicitly exploratory rankings, as declared before
outcomes. No refit or predictive-failure rescue was introduced.

The screen chooses the largest positive candidate mean versus G and retains
fixed simpler portfolio order on exact ties. It requires the original144
reference world/action/metric/invocation/fallback replays. Reference means are
compared on the same eight seed groups and six families. Selection uses no
final seeds or final policy reward. A negative Q6/P contrast does not silently
become a strongest-panel claim; the pre-outcome protocol permits that contender
for the user's primary G objective. A no-candidate result remains final.

The final contrast first averages paired differences within each seed's six
families, then uses the96 seed differences for mean, sample SD, SE and Student-t
inference. There is no family/arm pseudoreplication. One-sided p is t.sf(mean/SE,
95), the displayed two-sided95% interval uses t(.975), and the one-sided95%
lower bound uses t(.95). G→Q6→P formal claims stop at the first failed gate.
Nominal later p values remain descriptive. Zero variance conservatively yields
no standard-t claim, including a positive constant difference; this is explicit
rather than fabricated infinite significance. Paired wins/ties/losses and all
seed differences are retained. No sample expansion, final repair or replacement
is authorized by a negative result.

An independent synthetic execution of the actual final_report exercised96
exact high-half128-bit seed keys and six families under three scenarios:
G passes/Q6 fails/P has a nominally positive result but remains descriptive;
G fails and all later claims close; positive constant difference with zero
variance produces no t claim. All checks passed. The report used n96 rather
than576 and preserved full Python integer dictionary keys. Temporary reports
were constructed unit fixtures, not campaign evidence or simulator episodes.

## Pre-freeze binding hardening requested

1. Cached proof reuse must require exactly the unique registered checkpoint
   key set, matching expected/verified counts, complete current registration,
   source and audit-implementation bindings, valid checkpoint payload/status,
   and current commit/catalog/archive identities. The initial implementation
   rehashed only checkpoints listed by a self-digested proof, so an accidentally
   truncated/re-signed proof could claim completeness without covering every
   registered cell. Current source/implementation identity also needs explicit
   comparison at reuse. Reuse exact-input audit proof; do not repeat full
   decompression unnecessarily.
2. rows_for must validate each exact registered cell metadata, registration/
   source binding, valid metric status, error=None and zero fallback, rather
   than only key coverage. These are fixed admission rules, not reward filters.
3. Confirmation registration must verify its bound selection is the declared
   deterministic highest positive-G allowed candidate in the audited screen
   summary, not merely any allowed candidate string with a matching file hash.
   The selection/audit/source hashes must stay frozen. Preserve the original
   screen source identity when binding confirmation; no final-source amendment
   may change actions under the same screen registration.

Current source inspection shows large final seeds remain ordinary Python
integers through registration/cell keys, worker JSON, generate(seed=...), and
analysis dictionary keys/list iteration. No NumPy-int64 or float narrowing was
found in these final paths; NumPy seed arrays are confined to old small-seed
training/bootstrap metadata. The final reservation/independent review file
hashes are part of the registration source closure. The randomization receipt's
historical omissions and conditional collision bound remain in scope.

Disposition before the requested binding hardening: formulas and finite policy
admission accepted; freeze/launch remains conditional on those fixes and their
bounded malformed-input tests. Separate runtime and final independent endpoint/
statistics receipts are still required. No scientific win is established here.
