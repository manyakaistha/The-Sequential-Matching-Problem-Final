# Inherited manifest reconciliation

During round-four packaging preparation, the director checked every record in
round-three's completed manifest and its inherited manifest. Exactly three
round-three metadata files differ from their recorded hashes; all other 3377
round-three records and all 1889 older records match. No raw results, simulator,
policy source, frozen configuration or archive changed.

Two differences are append-only review completion notes. The first 8359 bytes of
`research3/FINAL_REVIEW.md` and first 3995 bytes of `research3/REPLICATION.md`
match their manifest hashes exactly. Their 990-byte and 2168-byte addenda record
the completed 48 independent replays and disclosed compute overrun. These notes
were completed after the prior manifest was built. They do not change outcomes.

The third difference is `results/research3/package_gate.log`. Shell redirection
created it empty before the package collected hashes. The package subsequently
printed successful archive/provenance messages into the same file. Its manifest
therefore records an empty SHA while the completed log has 146 bytes. This is a
self-log capture ordering defect, not evidence that the prior gate was rerun or
results altered. Source inspection supports that explanation; hashes alone do
not prove historical timing.

We preserve all three current files and the original manifest. Manifest-matching
prefixes are recovered into `research4/inherited_manifest_exceptions/`, including
the empty log. The recovery is performed now and is not a historical prelaunch
snapshot. `results/research4/inherited_manifest_exceptions.json` binds original
records, exact current hashes, byte lengths and copied prefixes. Round four's
gate permits only these three exact documented mismatches and checks every other
prior record. The reviewer independently verifies this reconciliation.

The prior claim that the completed manifest sealed every final byte was too
strong. Policy/raw-result preservation holds; review/log metadata require the
explicit reconciliation above. No old file or old manifest is rewritten to make
the mismatch disappear. The new gate finalizes its own log before collecting hashes and is invoked
directly, without redirecting stdout into the manifest roots. Final tool output
and manifest.completed record completion; no log or ledger is appended after
sealing. This avoids repeating the self-log defect.
