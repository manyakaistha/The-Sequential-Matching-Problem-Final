"""Write-once registrations and repository-visible seed inventories.

No proposed seed is silently called universally fresh. Inspect archive omissions
and supply an independent freshness review before freezing a campaign.
"""
import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FAMILIES = ['development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift']
POLICIES = {
    'G': {'entrypoint': 'research8.soft_query_trial.policies.g:decide', 'config': {'id': 'G'}},
    'G_random_soft': {'entrypoint': 'research8.soft_query_trial.policies.g_random_soft:decide',
                      'config': {'id': 'G_random_soft', 'salt': 'research8_g_random_soft_v1'}},
    'G_targeted_soft': {'entrypoint': 'research8.soft_query_trial.policies.g_targeted_soft:decide',
                        'config': {'id': 'G_targeted_soft'}},
    'Q6': {'entrypoint': 'research8.soft_query_followup.v2.reference_adapter:decide', 'config': {'id': 'Q6'}},
    'P': {'entrypoint': 'research8.soft_query_followup.v2.reference_adapter:decide', 'config': {'id': 'P'}},
}
CAPS = {'max_workers': 7, 'max_total_worker_rss_gib': 8.0, 'max_attempt_cpu_seconds': 90, 'max_attempt_wall_seconds': 180,
        'max_rss_gib': 4.0, 'free_reserve_gib_min': 10.0, 'boot_free_reserve_gib_min': .25,
        'invocation_wall_seconds': 10.0, 'wire_limit_bytes': 1048576}


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def registration_hash(reg):
    payload = {k: v for k, v in reg.items() if k != 'registration_sha256'}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False).encode()).hexdigest()


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())


def source_manifest(root=ROOT):
    paths = {root / 'kit.py', root / 'policy.py', root / 'research/terminal_model.py',
             root / 'research3/__init__.py', root / 'research3/model_candidates.py',
             root / 'research7b/workspace/research7/policies/references.py',
             root / 'research7b/workspace/research7/runtime/interfaces.py',
             root / 'research8/w2/protocol.py', root / 'research8/w2/public_rules.py'}
    for directory in ['research8/soft_query_followup/v2', 'research8/soft_query_trial/policies',
                      'research6/policies']:
        paths.update((root / directory).rglob('*.py'))
    # Include package initialization code along every imported namespace.
    for path in list(paths):
        parent = path.parent
        while parent != root and parent.is_relative_to(root):
            init = parent / '__init__.py'
            if init.exists(): paths.add(init)
            parent = parent.parent
    return {str(p.relative_to(root)): file_sha256(p) for p in sorted(paths)}


def verify_registration(reg, root=ROOT):
    if reg.get('schema_version') != 'R8-evidence-v2' or reg.get('status') != 'frozen_execution_registration':
        raise ValueError('not a v2 frozen registration')
    if reg.get('registration_sha256') != registration_hash(reg):
        raise ValueError('registration hash mismatch')
    if reg.get('execution_authorized') is not True:
        raise ValueError('execution not authorized')
    stage = reg.get('stage_id')
    if type(stage) is not str or not stage or not all(c.isalnum() or c in '_-' for c in stage):
        raise ValueError('unsafe stage name')
    seeds, families, arms = reg['ordered_seed_list'], reg['families'], reg['policy_ids']
    if (not seeds or len(set(seeds)) != len(seeds) or
            any(type(s) is not int or s < 0 for s in seeds) or families != FAMILIES or
            not arms or len(set(arms)) != len(arms) or any(a not in POLICIES for a in arms)):
        raise ValueError('invalid registration identities')
    if reg['policies'] != {a: POLICIES[a] for a in arms}:
        raise ValueError('policy definitions are not the frozen unchanged arms')
    expected = [{'stage_id': reg['stage_id'], 'seed': s, 'family': f, 'policy_id': a,
                 'cell_key': f"{reg['stage_id']}_{s}_{f}_{a}"}
                for s, f, a in itertools.product(seeds, families, arms)]
    if reg['cells'] != expected or reg['total_cells'] != len(expected):
        raise ValueError('registration is not the complete ordered grid')
    if reg['observation_cutoff'] != 99 or reg['active_days'] != 60 or reg['followup_days'] != 40:
        raise ValueError('wrong horizon')
    cap = reg['resource_forecast']
    if set(cap) != set(CAPS):
        raise ValueError('resource guards missing')
    for key, value in cap.items():
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError('invalid resource guard')
    if any(cap[key] > CAPS[key] for key in ('max_attempt_cpu_seconds', 'max_attempt_wall_seconds', 'max_rss_gib', 'max_total_worker_rss_gib')):
        raise ValueError('attempt limit exceeds authorized ceiling')
    if any(cap[key] < CAPS[key] for key in ('free_reserve_gib_min', 'boot_free_reserve_gib_min')):
        raise ValueError('disk reserve below authorized floor')
    if cap['max_workers'] != 7 or cap['wire_limit_bytes'] != 1048576 or cap['invocation_wall_seconds'] > 10:
        raise ValueError('protocol limits changed')
    manifest = reg['source_manifest']
    required = set(source_manifest(root))
    if not required.issubset(manifest):
        raise ValueError('source manifest omitted a required dependency')
    for rel, digest in manifest.items():
        target = root / rel
        if Path(rel).is_absolute() or '..' in Path(rel).parts or not target.resolve().is_relative_to(root.resolve()):
            raise ValueError('unsafe manifest path')
        if not target.is_file() or file_sha256(target) != digest:
            raise ValueError(f'source hash mismatch: {rel}')
    expected_contrasts = [[a, b] for a in ('G_random_soft', 'G_targeted_soft') if a in arms
                          for b in ('G', 'Q6', 'P') if b in arms]
    if all(a in arms for a in ('G_targeted_soft', 'G_random_soft')):
        expected_contrasts.append(['G_targeted_soft', 'G_random_soft'])
    if reg.get('analysis') != {'unit': 'seed_cluster_mean_of_six_family_differences',
                               'confidence': 'exploratory95',
                               'multiplicity': 'Holm_all_registered_contrasts',
                               'contrasts': expected_contrasts}:
        raise ValueError('registered analysis/comparison graph altered')
    evidence = reg['freshness_evidence']
    audit_path, review_path = root / evidence['audit_path'], root / evidence['review_path']
    for key in ('audit', 'review'):
        rel = evidence[key + '_path']
        if Path(rel).is_absolute() or '..' in Path(rel).parts:
            raise ValueError('unsafe freshness path')
        if file_sha256(root / rel) != evidence[key + '_sha256']:
            raise ValueError('freshness evidence changed')
    audit = strict_json(audit_path.read_text())
    review = strict_json(review_path.read_text())
    if audit['proposed_seeds'] != seeds or audit['collisions'] or audit['status'] != 'repository_visible_no_overlap':
        raise ValueError('freshness audit failed')
    if (review.get('status') != 'accepted_repository_visible_freshness' or review.get('proposed_seeds') != seeds
            or review.get('audit_sha256') != file_sha256(audit_path)
            or not review.get('reviewer') or not review.get('archive_omissions_disposition')
            or (audit.get('unreadable_or_oversized') and not review.get('unreadable_omissions_disposition'))):
        raise ValueError('independent freshness review missing')
    return True


def build_registration(stage, seeds, arms, audit_path, review_path, *, root=ROOT):
    if not stage or not all(c.isalnum() or c in '_-' for c in stage):
        raise ValueError('unsafe stage name')
    audit_path, review_path = Path(audit_path).resolve(), Path(review_path).resolve()
    reg = {'schema_version': 'R8-evidence-v2', 'status': 'frozen_execution_registration',
           'execution_authorized': True, 'stage_id': stage, 'ordered_seed_list': seeds,
           'families': FAMILIES, 'policy_ids': arms, 'policies': {a: POLICIES[a] for a in arms},
           'active_days': 60, 'followup_days': 40, 'observation_cutoff': 99,
           'resource_forecast': dict(CAPS), 'source_manifest': source_manifest(root),
           'freshness_evidence': {'audit_path': str(audit_path.relative_to(root.resolve())),
                                  'audit_sha256': file_sha256(audit_path),
                                  'review_path': str(review_path.relative_to(root.resolve())),
                                  'review_sha256': file_sha256(review_path)},
           'analysis': {'unit': 'seed_cluster_mean_of_six_family_differences',
                        'confidence': 'exploratory95', 'multiplicity': 'Holm_all_registered_contrasts',
                        'contrasts': [[a, b] for a in ('G_random_soft', 'G_targeted_soft') if a in arms
                                      for b in ('G', 'Q6', 'P') if b in arms] +
                                     ([['G_targeted_soft', 'G_random_soft']] if all(a in arms for a in
                                       ('G_targeted_soft', 'G_random_soft')) else [])}}
    reg['cells'] = [{'stage_id': stage, 'seed': s, 'family': f, 'policy_id': a,
                     'cell_key': f'{stage}_{s}_{f}_{a}'} for s, f, a in itertools.product(seeds, FAMILIES, arms)]
    reg['total_cells'] = len(reg['cells'])
    reg['registration_sha256'] = registration_hash(reg)
    verify_registration(reg, root)
    return reg


def seed_inventory(seeds, root=ROOT, exclude=()):
    """Metadata-only scan; excludes private worlds and reports unseen archives.

    Seed fields/ranges in JSON/JSONL and historical seed= numeric literals in
    Python/shell/Markdown are conservative reservations, not policy features.
    """
    import re
    used = set()
    scanned, failures, archives = [], [], []
    excluded = {Path(p).resolve() for p in exclude}
    def collect(obj):
        if isinstance(obj, dict):
            for key, val in obj.items():
                low = key.lower()
                if 'seed' in low:
                    if type(val) is int:
                        used.add(val)
                    elif isinstance(val, list):
                        used.update(v for v in val if type(v) is int)
                if low in ('range', 'seed_range') and isinstance(val, list) and len(val) == 2 and all(type(v) is int for v in val):
                    if 0 <= val[1] - val[0] <= 100000:
                        used.update(range(val[0], val[1] + 1))
                collect(val)
        elif isinstance(obj, list):
            for val in obj:
                collect(val)
    for directory, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', '.venv', 'node_modules', 'results', '.tmp', '.policy_tmp', 'test_temp_v2')]
        for name in files:
            path = Path(directory) / name
            if path.resolve() in excluded or name == 'world.json':
                continue
            if name.endswith(('.tar', '.tar.gz', '.zip', '.zst', '.tgz')):
                archives.append(str(path.relative_to(root)))
            if path.suffix not in ('.json', '.jsonl', '.py', '.sh', '.md'):
                continue
            if path.stat().st_size > 16 * 1024 * 1024:
                failures.append(str(path.relative_to(root)))
                continue
            try:
                raw = path.read_text()
                if path.suffix == '.json':
                    collect(strict_json(raw))
                elif path.suffix == '.jsonl':
                    for line in raw.splitlines():
                        if line.strip(): collect(strict_json(line))
                else:
                    used.update(int(v) for v in re.findall(r'\bseed\s*[=:]\s*(\d+)\b', raw))
                scanned.append(str(path.relative_to(root)))
            except (UnicodeError, OSError, ValueError):
                failures.append(str(path.relative_to(root)))
    return {'status': 'repository_visible_no_overlap' if not (set(seeds) & used) else 'overlap_found',
            'proposed_seeds': seeds, 'collisions': sorted(set(seeds) & used),
            'scanned_file_count': len(scanned), 'scanned_inventory_sha256': hashlib.sha256(
                '\n'.join(sorted(scanned)).encode()).hexdigest(), 'unreadable_or_oversized': failures,
            'archives_not_decoded': archives, 'scope': 'repository-visible metadata; not universal freshness',
            'private_worlds_read': False}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    audit = sub.add_parser('audit-seeds')
    audit.add_argument('--seeds', required=True, help='comma-separated explicit integer seeds')
    audit.add_argument('--output', required=True)
    freeze = sub.add_parser('freeze')
    freeze.add_argument('--stage', required=True)
    freeze.add_argument('--seeds', required=True)
    freeze.add_argument('--arms', required=True)
    freeze.add_argument('--freshness-audit', required=True)
    freeze.add_argument('--freshness-review', required=True)
    freeze.add_argument('--output', required=True)
    args = parser.parse_args()
    seeds = [int(s) for s in args.seeds.split(',')]
    if args.command == 'audit-seeds':
        result = seed_inventory(seeds, exclude=[args.output])
    else:
        result = build_registration(args.stage, seeds, args.arms.split(','), args.freshness_audit,
                                    args.freshness_review)
    write_once(args.output, result)
    print(json.dumps({'written': args.output, 'status': result['status']}))


if __name__ == '__main__':
    main()
