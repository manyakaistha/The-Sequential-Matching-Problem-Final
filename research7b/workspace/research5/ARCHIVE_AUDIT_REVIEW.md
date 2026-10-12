# Independent full-log and archive audit review

11 October2026. Production/provenance reviewer; reviewers: critic and director.
Owned only this review. Director verify_logs.py and archive_results.py were read
without edits or full audit reruns. Question: do saved records enforce complete
public histories, and does restoration preserve bytes safely? Hypothesis:
120paired calls and exact public transitions are required; archive corruption,
unsafe members and differing existing bytes are refused. Allowance60CPU seconds.
Independent fixtures below use temporary synthetic files only, no worlds or
policy inference. Current large audit/build executions remain director-owned.

## Full committed-log reconstruction

The verifier binds every row-listed audit file's byte length and SHA, reads exactly
two privileged records (initial world and final simulator state), and confines
privileged truth to offline reconstruction. It runs Simulator on the saved world
and preceding saved actions, never calls a policy or generates a new world. Each
of120request/response pairs must have matching sequence and the expected phase/day.
Each incoming observation equals reconstructed sim.observe exactly; incoming
memory equals the previous outgoing memory. Request/response shape,10second
configured deadline, actual elapsed time, request size and memory size are checked.
Simulator methods independently reject illegal actions and update public state.
Extra/error log records are refused. Forty subsequent empty advances produce
day100; the whole serialized final simulator state must equal the saved private
record. This checks scheduled outcomes after exits rather than dropping them.

Actions, prospective member snapshots, greedy match-time public states, introductions,
completed feedback, latency arrays, peak sizes and both ordered/semantic digests
must match the committed row and public trace. Public events are then regrouped
without calling metrics(), with explicit response/rejection/date/second-intention
denominators and both qualification deadlines. Qualified counts, reward ratios,
assignments, ask cost and served/arrived counts must equal the official row.

These are strong complete-record consistency checks, not policy re-execution or
proof that every orphan request completed. Main requires complete=true and5160rows,
but does not itself assert an exact unique registered policy/seed/family cell set.
The final package must separately require that set, error-free audit status,
5160successful row records and619200checked invocations, with audit/source/input
hashes matched. Duplicate rows must not substitute for missing original cells.
Interrupted/uncommitted attempts remain the separate recovery review's scope.
The current full audit is in progress; no result is asserted from partial progress.

## Archive source and temporary fixture checks

Archive build retains raw originals and fingerprints source files before adding
them. Public JSON is gzip-tar; existing gzip logs use plain tar. Verification
checks whole archive digest, registered regular members, no duplicates, safe
repository-relative names, streamed payload length/digest and retained originals'
bytes. Verification currently requires originals to exist, intentionally; it is
not an archive-only verifier after raw deletion. Index generation refuses an
existing index and archive build refuses existing target archives. A failed build
can leave partial new archives; these are retained rather than overwritten.

An isolated two-file fixture exercised both formats and complete streaming
verification. Restoration created two missing files, then skipped both identical
existing files; a deliberately differing destination file was refused without
changing its bytes. Additional synthetic tar fixtures confirmed rejection of an
unregistered member, duplicate member, nonregular symlink member, lexical parent
traversal and wrong archive digest. Measured fixture CPU0.011429seconds,
wall0.015135seconds. No research file or production policy was modified.

One hypothesis was falsified: the original restore only sanitizes lexical member
names. A pre-existing destination/results directory symlink caused new creation
outside destination in the temporary fixture. Its fresh-temporary-directory tests
do not establish safety on arbitrary existing destination trees. The director was
notified with the concrete counterexample. Running archive_results.py bytes remain
unchanged to preserve executed-source provenance; a separate secure restore tool
is being prepared for canonical restoration and archive-only verification.
Final restoration safety acceptance requires independent inspection/testing of
that helper. The original internal fresh-directory test result remains valid for
its stated scope and is not silently reclassified as secure arbitrary restoration.

## Separate secure canonical restore accepted

The director added restore_artifacts.py without editing the running archive
builder/verifier. Independent source inspection confirms destination-root and
per-component dirfd/O_NOFOLLOW opens, exclusive creation, symlink-refusing existing
leaf reads, duplicate-index detection, registered regular-member checks and payload
length/digest verification. Archive-only verification does not require raw originals.
The helper expects a trusted index/final manifest; this is not a guarantee against
arbitrary concurrent filesystem tampering or a compromised operating system.
An interrupted new-file write can leave a partial new destination file that a
later call refuses as differing; no pre-existing file is overwritten. Use canonical
secure helper instructions rather than the original restore implementation for
arbitrary existing destination trees.

Fourteen temporary synthetic fixture checks pass, retained in
results/research5/restore_security_checks.json. They cover tar.gz/plain tar,
archive-only verification after deleting both original files, restoring two files,
identical-existing skip, differing-existing refusal without byte changes, and
root/parent/leaf symlink refusal. No file is created outside destination in the
parent-symlink case; even a leaf symlink to matching bytes is refused. Negative
fixtures reject a wrong archive digest, duplicate index entry, unregistered member,
duplicate tar member, nonregular member, parent traversal and payload mismatch.
Measured CPU0.017924seconds, wall0.020063seconds. No real large audit/archive scan
or policy replay was duplicated. Source SHA is recorded for each tested helper;
the original archive source still matches its running provenance.

These tests accept the scoped canonical restoration behavior and resolve the
identified existing-parent-symlink counterexample. Final package completion still
requires full director log/archive audit outputs, their source/input/index digests,
exact registered committed-grid coverage, original/interrupted-file preservation
and final manifest checks. Neither fixture success nor partial audit progress
alone certifies the full5160episode package.
