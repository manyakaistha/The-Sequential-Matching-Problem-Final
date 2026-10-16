# Independent review of the six-worker amendment

14 October 2026. Reviewer: `/root/logging_critic`; implementer/reviewer integration:
`/root`. Bounded read-only production review, 30 CPU seconds/3 minutes. This
amendment follows the user's explicit authorization for six simulation workers,
as supplied by the director. It supersedes the earlier three-simulation-worker
preference; the four-agent routing/slot contract is unaffected. The prior review,
implementation manifest and historical evidence remain preserved.

No blocking defect found in the reviewed amendment. Registration now requires a
six-worker ceiling and an explicit combined worker RSS guard, rejecting ceilings
above six workers or 8 GiB. The launcher defaults to six and permits only integer
counts 1 through 6, with booleans and fractional values rejected. Its dispatch
loop bounds the pending worker count by that chosen limit. The existing global
coordinator flock and inherited worker lease remain in place.

Every monitoring pass sums the live RSS measurements for each worker and its
descendants. Crossing the registered combined ceiling raises a failure; the
existing `finally` cleanup kills remaining workers and their separate-session
descendants. The existing 4 GiB per-worker-tree, CPU, wall, disk and invocation
guards remain in place. The combined 8 GiB ceiling is a monitored RSS limit,
with process polling and scheduling granularity; it is not an instantaneous
kernel-wide memory reservation. It covers participating worker trees, not the
coordinator, other applications or unrelated launchers.

Independent verification:

```sh
python3 -m pytest research8/soft_query_followup/v2/tests/test_enforcement.py research8/soft_query_followup/v2/tests/test_analysis.py -q
```

Result: **23 passed in 0.43 seconds**. The added guard cases cover allowing six,
rejecting seven/invalid counts, rejecting a rehashed registration that expands
the aggregate memory ceiling, and the inclusive 8 GiB boundary versus one byte
above it. Source inspection verified that the tested count/memory helpers are
called in the live coordinator and that memory failure reaches process cleanup.
These are pure guard/data checks; no simulation or policy invocation occurred.
The coordinator's six-worker process dispatch and memory monitoring have not
been exercised by this review under an actual six-worker load.

README and testing-prompt commands now request `--workers 6` and disclose the
8 GiB combined guard. Prior versions are under
`../history/before_six_workers/`, outside the v2 Python source-manifest scan.
Future registrations must be frozen against the amended source identities.
This review does not certify throughput, full-size memory usage or host stability.
The fixed 120-cell smoke must supply those measurements before any replication
forecast; no smoke or replication was launched by this amendment review.
