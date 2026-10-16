# Public evidence and enforcement repair

Use this version for new runs; the old `soft_query_trial` sources, registrations and432commits remain unchanged.

## Implemented

- Cold subprocess JSON policies; bounded input/output, real invocation deadlines, explicit failures and detected frozen-reference fallbacks.
- Temporary child working directories/import cache and all outputs on the external project drive. No new private world files; world hash computed only on the host.
- Fsynced public request, response, action, invocation, answer, day-level telemetry and released-feedback streams; explicit arrived-by59 and day99 final public artifacts; attempt lifecycle; write-once hashed commits.
- Source/config/registration checks, complete grid validation, reviewed freshness receipts, fixed resource ceilings and output-to-registration binding.
- One repository-wide coordinator lease, maximum3participating cell workers, inherited worker lease, monitored whole-process-tree RSS/wall limits and cleanup of separate-session child processes.
- Independent endpoint reconstruction without importing the main metrics: mutual first acceptance, distinct endpoints, coherent event chronology, date0..30, second intentions0..3, releases≤99 and exact per100 normalization. Hashes, public capture completeness, action legality, memory/record continuity and metrics reconciled before analysis.
- Seed-group statistics, fixed registered comparisons/Holm, explicit degeneracy and descriptive family/mechanism diagnostics.

Policies have not been changed. `reference_adapter.py` exposes the unchangedQ6/P references and propagates fallback status. This does not train a model or integrateVOI/D1.

## Validation and limits

The initial combinedrun passed70tests+2subtests in14.96s, including23unchangedpolicytests. Two subsequently added analysis cases and guard tests passed in a13-test follow-up, also independently repeated. The current inventory is72tests+2subtests, verified across those runs. The independent review is [review.md](review.md).

A single declared4-actor simulator fixture completed120coldcalls and independently reconstructed its public evidence. Maximum observed coldcall was.182s. It included mutual acceptance, a happened date and a late-positive unqualified pause; positive qualified endpoint cases are covered by pure event fixtures. This is not200-member performance or a new sampled reward study. Preserved rawcapture is `validation/declared_capture/`; summary `validation/capture_summary.json`.

Subprocess/JSON isolation is for trusted frozen code; it is not an adversarial filesystem/network sandbox. RSS limits onmacOS and process-tree checks are polled and may overshoot between checks; CPU limits haveOSrounding. The global lock coordinates participatingv2launchers and detects known oldercoordinators; an operator must exclude unrelated jobs, including jobs on anothermachine. Independent eventaudit does not regenerate every questionnaire answer or availability transition from latent world truth.

The source manifest includes executable modules and tests. Do not edit them afterfreeze. Analysis of an actualv2campaign requires its livefrozenidentity to match; laterrevisions must preserve an isolated compatible sourceversion to reproduceold audits.

No new120-cell instrumentation smoke or2880-cell replication has been launched. Do not reuseold registrations with this runner. The120-cell future smoke deliberately includesQ6/P as well as thethreeoriginalarms, superseding the previously suggested but unrun72-cell instrumentation smoke.

## Commands

From repositoryroot:

```bash
mkdir -p research8/soft_query_followup/v2/.tmp
PYTHONPATH=. TMPDIR="$PWD/research8/soft_query_followup/v2/.tmp" python3 -m pytest research8/soft_query_followup/v2/tests research8/soft_query_trial/tests/test_policies.py -q --basetemp research8/soft_query_followup/test_temp_v2
```

Publicfixtureaudit (not a campaignregistration):

```bash
PYTHONPATH=. python3 -m research8.soft_query_followup.v2.audit --registration research8/soft_query_followup/v2/validation/declared_fixture_registration.json --output research8/soft_query_followup/v2/validation/declared_capture
```

For the exact freshseedreview, freeze,120-cellsmoke,2880-cellreplication andanalysis workflow, copy [TESTING_PROMPT.md](TESTING_PROMPT.md) into the next agent. The registrationCLI writes once and refusesunreviewedseedfreshness, changedpolicies or alteredguards; the launcher stops on invalidity rather than silentlydroppingcells.

Historical records remain preliminary. Thev2repair does not retroactively independentlycertify theold432episodeaggregates.
