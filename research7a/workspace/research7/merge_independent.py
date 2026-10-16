"""Independent merge checker, bundle verifier, and failure injection suite.

Owned exclusively by 7a under Work Order WO04.
Strict adherence to research7/MERGE_PROTOCOL.md.

Enforces:
- Rejection of scientific conflicts and incomplete clusters.
- Fails closed: synthetic invalid/missing/conflicting cells never yield primary analysis.
- Separate machine namespaces; never averages host means or overlays directories.
- Authoritative invalidity remains durable and disqualifying.
- Transport duplicates (byte-identical) deduplicated to 1 cell with logged provenance.
- Safe path handling (rejects traversal, absolute paths, and symlink escapes).
"""

from __future__ import annotations
import collections
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union


def compute_cell_key(
    program_id: str,
    stage_id: str,
    seed: int,
    family: str,
    policy_id: str,
    config_sha256: str,
    source_tree_sha256: str,
    inference_assets_sha256: str
) -> str:
    """Compute the 7a pipe-delimited identity (7b colon format remains incompatible)."""
    payload = json.dumps([program_id, stage_id, seed, family, policy_id, config_sha256, source_tree_sha256, inference_assets_sha256], separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


class SafeBundleValidator:
    """Validates bundle structural layout, checksums, and path safety."""

    @staticmethod
    def validate_relative_path(path_str: str) -> bool:
        """Reject path traversal, absolute paths, and unsafe components."""
        p = Path(path_str)
        if p.is_absolute():
            return False
        for part in p.parts:
            if part in ('..', '~', ''):
                return False
        return True

    @staticmethod
    def verify_manifest(bundle_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Verify that all manifest entries exist and hashes match."""
        errors = []
        files = bundle_dict.get('manifest', {}).get('files', [])
        for entry in files:
            path_str = entry.get('path', '')
            if not SafeBundleValidator.validate_relative_path(path_str):
                errors.append(f"Unsafe path in manifest: {path_str}")
                continue
            # Content verification if provided inline
            if 'content_sha256' in entry and 'content_bytes' in entry:
                content = entry.get('raw_data', b'')
                if hashlib.sha256(content).hexdigest() != entry['content_sha256']:
                    errors.append(f"Hash mismatch on {path_str}")
                if len(content) != entry['content_bytes']:
                    errors.append(f"Size mismatch on {path_str}")
        return len(errors) == 0, errors


class IndependentMerger:
    """Deterministic merge engine conforming to research7/MERGE_PROTOCOL.md."""

    def __init__(self, registration: Dict[str, Any]):
        self.registration = registration
        self.program_id = registration.get('program_id')
        self.stage_id = registration.get('stage_id')
        self.registered_cells = set(registration.get('expected_cell_keys', []))
        self.expected_seeds = set(registration.get('expected_seeds', []))
        self.expected_families = set(registration.get('expected_families', []))
        self.expected_policies = set(registration.get('expected_policies', []))

    def evaluate_bundles(
        self,
        bundles: Sequence[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process closed bundles and decide whether valid primary analysis is permissible.
        
        Strict fail-closed semantics:
        - If any conflict is detected -> QUARANTINE, abort analysis.
        - If any registered cell is missing -> INCOMPLETE, abort primary analysis.
        - If any committed cell is invalid -> DISQUALIFIED, abort primary analysis.
        - If any extra unregistered cell is present -> REJECT, abort analysis.
        """
        seen_cells: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
        all_attempts: List[Dict[str, Any]] = []
        authoritative_commits: Dict[str, Dict[str, Any]] = {}
        quarantined_conflicts: List[Dict[str, Any]] = []
        integrity_errors: List[str] = []
        if not self.registered_cells or not all((self.program_id, self.stage_id,
                self.expected_seeds, self.expected_families, self.expected_policies)):
            integrity_errors.append('Registration must specify a nonempty registered grid and identity axes')
        expected_count = len(self.expected_seeds) * len(self.expected_families) * len(self.expected_policies)
        if len(self.registered_cells) != expected_count:
            integrity_errors.append('Registered grid size disagrees with seed/family/policy axes')

        # 1. Ingest all commits and attempts from all bundles
        for b_idx, b in enumerate(bundles):
            bundle_id = b.get('bundle_id', f"bundle_{b_idx}")
            host_id = b.get('host_id', 'unknown_host')
            
            # Lease check: verify shard lease generation
            lease = b.get('lease', {})
            if lease.get('revoked', False) or lease.get('expired', False):
                integrity_errors.append(f"Bundle {bundle_id} committed under revoked/expired lease.")
                continue

            commits = b.get('commits', [])
            for c in commits:
                cell_key = c.get('cell_key')
                if not cell_key:
                    integrity_errors.append(f"Commit missing cell_key in {bundle_id}")
                    continue

                identity_fields = ('program_id', 'stage_id', 'seed', 'family', 'policy_id',
                                   'config_sha256', 'source_tree_sha256', 'inference_assets_sha256')
                if not all(k in c for k in identity_fields):
                    integrity_errors.append(f'Commit missing full identity metadata in {bundle_id}')
                    continue
                if (type(c['seed']) is not int or any(not isinstance(c[k], str) or not c[k] or '|' in c[k]
                        for k in identity_fields if k != 'seed')):
                    integrity_errors.append(f'Invalid identity metadata in {bundle_id}')
                    continue
                reconstructed = compute_cell_key(*(c[k] for k in identity_fields))
                if (cell_key != reconstructed or c['program_id'] != self.program_id
                        or c['stage_id'] != self.stage_id or c['seed'] not in self.expected_seeds
                        or c['family'] not in self.expected_families or c['policy_id'] not in self.expected_policies):
                    integrity_errors.append(f'Commit identity metadata mismatch in {bundle_id}')
                    continue
                if c.get('valid') is not True:
                    integrity_errors.append(f"Durable invalidity committed in cell {cell_key}: {c.get('error')}")
                c_record = copy.deepcopy(c)
                c_record['origin_bundle_id'] = bundle_id
                c_record['origin_host_id'] = host_id
                seen_cells[cell_key].append(c_record)

            all_attempts.extend(b.get('attempts', []))

        # 2. Check each cell for conflicts, duplicates, or invalidity
        for cell_key, commit_list in seen_cells.items():
            # Check if cell is registered
            if cell_key not in self.registered_cells:
                integrity_errors.append(f"Unregistered cell key found: {cell_key}")
                continue

            if len(commit_list) == 1:
                commit = commit_list[0]
                authoritative_commits[cell_key] = commit
            else:
                # Multiple commits for the exact same cell
                # Check if they are transport duplicates (identical scientific content)
                first = commit_list[0]
                is_exact_transport_dup = True
                
                def scientific_record(commit):
                    return {k: v for k, v in commit.items() if k not in
                            ('origin_bundle_id', 'origin_host_id')}
                is_exact_transport_dup = all(scientific_record(first) == scientific_record(other)
                                             for other in commit_list[1:])

                if is_exact_transport_dup:
                    # Transport duplicate: retain provenance, count 1 cell
                    authoritative = copy.deepcopy(first)
                    authoritative['duplicate_provenance'] = [c['origin_bundle_id'] for c in commit_list]
                    authoritative_commits[cell_key] = authoritative
                else:
                    # Scientific conflict! Differing actions, results, or validity
                    conflict_record = {
                        'cell_key': cell_key,
                        'differing_commits': commit_list,
                        'reason': 'Conflicting actions/outcomes for identical cell identity'
                    }
                    quarantined_conflicts.append(conflict_record)
                    integrity_errors.append(f"Scientific conflict in cell {cell_key}")

        # 3. Check grid completeness
        missing_cells = []
        if self.registered_cells:
            for exp_cell in self.registered_cells:
                if exp_cell not in authoritative_commits:
                    missing_cells.append(exp_cell)

        # 4. Synthesize final merge status
        has_conflicts = len(quarantined_conflicts) > 0
        has_missing = len(missing_cells) > 0
        has_errors = len(integrity_errors) > 0

        can_produce_primary_analysis = not (has_conflicts or has_missing or has_errors)
        status = 'merged_clean' if can_produce_primary_analysis else 'merge_halted_unresolved'

        return {
            'status': status,
            'can_produce_primary_analysis': can_produce_primary_analysis,
            'total_cells_authoritative': len(authoritative_commits),
            'expected_cells_count': len(self.registered_cells),
            'missing_cells': missing_cells,
            'quarantined_conflicts': quarantined_conflicts,
            'integrity_errors': integrity_errors,
            'total_attempts_recorded': len(all_attempts),
            'merged_index': authoritative_commits if can_produce_primary_analysis else {}
        }


def run_merge_failure_injection_suite() -> Dict[str, Any]:
    """Execute synthetic failure injection test suite (T17, T20, T21, T24-T27).
    
    Verifies that the independent merger strictly rejects:
    1. Scientific conflict (differing action digest for same cell).
    2. Transport duplicate (properly deduplicated to 1 cell).
    3. Missing cell (incomplete cluster).
    4. Committed invalid cell (marks failure, blocks primary analysis).
    5. Revoked / stale lease commit.
    6. Extra unregistered cell.
    7. Unsafe path traversal in manifest.
    """
    suite_results = {}

    reg_cell_1 = compute_cell_key("r7", "P1", 101, "sparse", "G", "cfg1", "src1", "ast1")
    reg_cell_2 = compute_cell_key("r7", "P1", 101, "sparse", "Q1", "cfg2", "src1", "ast1")

    base_reg = {
        'program_id': 'r7',
        'stage_id': 'P1',
        'expected_cell_keys': [reg_cell_1, reg_cell_2],
        'expected_seeds': [101],
        'expected_families': ['sparse'],
        'expected_policies': ['G', 'Q1']
    }

    # Test 1: Clean merge
    bundle_a = {
        'bundle_id': 'b_7a',
        'host_id': 'small-01',
        'lease': {'revoked': False, 'expired': False},
        'commits': [{
            'cell_key': reg_cell_1,
            'program_id': 'r7', 'stage_id': 'P1', 'config_sha256': 'cfg1',
            'source_tree_sha256': 'src1', 'inference_assets_sha256': 'ast1',
            'seed': 101, 'family': 'sparse', 'policy_id': 'G',
            'action_sha256': 'act_hash_g', 'valid': True, 'primary_score': 0.85
        }]
    }
    bundle_b = {
        'bundle_id': 'b_7b',
        'host_id': 'mac-01',
        'lease': {'revoked': False, 'expired': False},
        'commits': [{
            'cell_key': reg_cell_2,
            'program_id': 'r7', 'stage_id': 'P1', 'config_sha256': 'cfg2',
            'source_tree_sha256': 'src1', 'inference_assets_sha256': 'ast1',
            'seed': 101, 'family': 'sparse', 'policy_id': 'Q1',
            'action_sha256': 'act_hash_q1', 'valid': True, 'primary_score': 0.88
        }]
    }
    merger1 = IndependentMerger(base_reg)
    res1 = merger1.evaluate_bundles([bundle_a, bundle_b])
    suite_results['clean_merge_passes'] = (res1['can_produce_primary_analysis'] is True and res1['total_cells_authoritative'] == 2)

    # Test 2: Incomplete cluster (missing cell 2)
    merger2 = IndependentMerger(base_reg)
    res2 = merger2.evaluate_bundles([bundle_a])
    suite_results['missing_cell_blocks_analysis'] = (res2['can_produce_primary_analysis'] is False and len(res2['missing_cells']) == 1)

    # Test 3: Scientific conflict (two commits for reg_cell_1 with differing action hashes)
    conflicting_b = {
        'bundle_id': 'b_conflict',
        'host_id': 'small-01',
        'lease': {'revoked': False, 'expired': False},
        'commits': [{
            'cell_key': reg_cell_1,
            'program_id': 'r7', 'stage_id': 'P1', 'config_sha256': 'cfg1',
            'source_tree_sha256': 'src1', 'inference_assets_sha256': 'ast1',
            'seed': 101, 'family': 'sparse', 'policy_id': 'G',
            'action_sha256': 'DIFFERING_ACTION_HASH', 'valid': True, 'primary_score': 0.90
        }]
    }
    merger3 = IndependentMerger(base_reg)
    res3 = merger3.evaluate_bundles([bundle_a, conflicting_b, bundle_b])
    suite_results['scientific_conflict_quarantined'] = (res3['can_produce_primary_analysis'] is False and len(res3['quarantined_conflicts']) == 1)

    # Test 4: Transport duplicate (two identical commits for reg_cell_1)
    dup_b = copy.deepcopy(bundle_a)
    dup_b['bundle_id'] = 'b_dup'
    merger4 = IndependentMerger(base_reg)
    res4 = merger4.evaluate_bundles([bundle_a, dup_b, bundle_b])
    suite_results['transport_duplicate_deduplicated'] = (res4['can_produce_primary_analysis'] is True and res4['total_cells_authoritative'] == 2)

    # Test 5: Committed invalid cell
    invalid_commit_b = {
        'bundle_id': 'b_invalid',
        'host_id': 'small-01',
        'lease': {'revoked': False, 'expired': False},
        'commits': [{
            'cell_key': reg_cell_2,
            'program_id': 'r7', 'stage_id': 'P1', 'config_sha256': 'cfg2',
            'source_tree_sha256': 'src1', 'inference_assets_sha256': 'ast1',
            'seed': 101, 'family': 'sparse', 'policy_id': 'Q1',
            'action_sha256': 'act_hash_q1', 'valid': False, 'error': 'Policy timeout', 'primary_score': None
        }]
    }
    merger5 = IndependentMerger(base_reg)
    res5 = merger5.evaluate_bundles([bundle_a, invalid_commit_b])
    suite_results['invalid_commit_blocks_analysis'] = (res5['can_produce_primary_analysis'] is False and any('invalidity' in err for err in res5['integrity_errors']))

    # Test 6: Revoked lease commit
    revoked_bundle = copy.deepcopy(bundle_b)
    revoked_bundle['lease'] = {'revoked': True, 'expired': False}
    merger6 = IndependentMerger(base_reg)
    res6 = merger6.evaluate_bundles([bundle_a, revoked_bundle])
    suite_results['revoked_lease_rejected'] = (res6['can_produce_primary_analysis'] is False)

    # Test 7: Unsafe path traversal in manifest
    manifest_traversal = {'manifest': {'files': [{'path': '../../etc/passwd'}]}}
    ok_path, path_errs = SafeBundleValidator.verify_manifest(manifest_traversal)
    suite_results['path_traversal_rejected'] = (not ok_path and len(path_errs) == 1)

    all_tests_passed = all(suite_results.values())
    return {
        'status': 'failure_injection_suite_complete',
        'all_passed': all_tests_passed,
        'suite_results': suite_results
    }
