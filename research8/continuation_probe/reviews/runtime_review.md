# Independent runtime review

Reviewer: `/root/continuation_forensics`, 2026-10-15. Director and scientific
critic: `/root`, `/root/continuation_critic`. Read-only review of the five new
runtime modules; no runtime implementation edits, episodes, generated worlds,
fits or result inspection. Review remained within the 90 CPU-second allowance.

**Readiness:** the inspected clean-output execution path is suitable for the
fixed 24-cell development mechanism replay, subject to the director's source
freeze and independent scientific/policy review. It does not certify a hostile
submission sandbox or policy improvement. The final source recheck confirmed
abnormal resume now fails closed on uncommitted orphan attempts until explicit
quiescent recovery preserves them. No remaining critical runtime finding.

## Verified behavior

* Registration fixes two deliberately reused seeds840001/840002, all six
  families, two named arms, 24 exact cells, original resource caps, and15GiB
  storage guard. The source closure includes the old frozen source manifest,
  every new probe Python source and fast audit. A mechanical hash check found
  all63 current entries matched; these seeds are not fresh evidence.
* Runner serializes sanitized public observations to a new cold policy process
  for every ask/match call; validates phase keys, memory and real legal actions;
  retains requests, responses, actions, invocations, released feedback and public
  final metrics; makes120calls over days0..59 and releases through99.
* CLI accepts only the probe package entrypoints; JSON rejects duplicate keys
  and nonfinite constants. Transport bounds combined stdout/stderr, wall time,
  process CPU, file size and observed RSS. Child source remains trusted: root
  path access is not a filesystem/network sandbox, accurately disclosed.
* Shared v2 coordinator lock, seven-worker ceiling and8GiB monitored total
  worker-tree RSS guard are retained. Parent samples each worker tree; on limits
  it kills descendants as well as worker. Aggregate RSS is sampled rather than
  a kernel-enforced instantaneous bound. Known coordinator detection includes
  the new probe and existing v3 launcher.
* Per-cell raw512MiB limit and dispatch reserve include raw/archive overlap and
  audit staging. Complete/failed ordinary attempts are durably committed then
  archived through unchanged streaming zstd level3 storage, which verifies
  physical and original logical hashes before raw removal. Interrupted workers
  retain their partial raw attempts.

## Findings and fixes

1. **Valid-commit archive recovery — fixed during review.** Originally the
   coordinator skipped existing commits, bypassing the runner's recovery branch.
   Confirmed revised `launcher.py:173-187` checks original source identity and
   runs archive/hash recovery before counting existing cells complete. A crash
   between commit publication and archival therefore reaches recovery.
2. **Uncommitted interrupted attempts — fixed on final recheck.** A
   partial attempt without a commit was not inspected before that cell was
   requeued. Retaining it avoids loss, but silent redispatch leaves stopped
   partial attempts unarchived and needs an explicit recovery record. Recommend
   rejecting resume when any attempt directory is unreferenced by a valid
   commit; recover it separately before running exact remaining original cells.
   Final launcher source rejects these directories before dispatch, preserving
   their raw evidence for explicit recovery.
3. **Registration metadata — fixed on final recheck.** The writer declares
   stage/horizon correctly, while the inspected verifier did not separately
   enforce top-level stage_id and60/40/99 horizon fields. Runtime itself
   hardcodes the correct horizon. Enforce these values before freezing so a
   self-rehashed metadata edit is rejected. Confirmed the verifier now enforces
   stage,60/40/99 horizon and the complete frozen ANALYSIS purpose/gate object.

Final recheck also confirmed the runner rejects a policy function taking over
one second, while retaining the ten-second cold-transport guard. A quick source
review of `summarize.py` found no additional critical issue: it uses one bounded
archive-aware independent audit pass, checks12parent cells against original
world/action/metric identities, and reports next-day potential-return/witness
use denominators without a significance or superiority claim. This was source
review only, not an executed result audit.

## Bounded verification

All five reviewed modules parsed successfully with Python3.14 AST. Four
constructed empty-public-state cold calls (two arms times ask/match) returned
the expected wire keys and no fallback, using the actual new transport and CLI;
they did not create an episode or inspect a generated world. Source hash closure
check passed. No claim is made that these four calls exercise timeout, memory
exhaustion, kill-race, disk pressure, interruption or archive-corruption cases;
those behaviors are supported here by source inspection and inherited guarded
components, not new end-to-end negative tests.

The director should record the final frozen hashes and recovery recheck after
any changes. Do not describe this small reused-seed replay as independent
confirmation or expand its sample after observing reward.
