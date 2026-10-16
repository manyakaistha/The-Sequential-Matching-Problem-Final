"""Bind storage-only continuation to immutable original cells and source identities."""
import hashlib
import itertools
import json
import math
from pathlib import Path

from research8.soft_query_followup.v2.registration import (
    ROOT, strict_json, file_sha256, registration_hash, write_once)

SCHEMA = 'R8-storage-continuation-v1'


def manifest(root=ROOT, original=None):
    result = dict(original['source_manifest']) if original else {}
    paths = [root/'AGENTS.md'] + list((root/'research8/soft_query_followup/v3').rglob('*.py'))
    for path in paths:
        if any(x.startswith('.') or x=='__pycache__' for x in path.relative_to(root).parts):continue
        result[str(path.relative_to(root))] = file_sha256(path)
    return result


def verify_continuation(reg, original=None, *, root=ROOT, output=None, check_sources=True):
    if (reg.get('schema_version') != SCHEMA or reg.get('registration_sha256') != registration_hash(reg)
        or reg.get('status') != 'frozen_storage_only_continuation' or reg.get('execution_authorized') is not True):
        raise ValueError('invalid continuation schema/hash')
    rel = reg['original_registration_path']
    if Path(rel).is_absolute() or '..' in Path(rel).parts:
        raise ValueError('unsafe original registration path')
    original_path = root/rel
    if original is None:original=strict_json(original_path.read_text())
    if file_sha256(original_path) != reg['original_registration_file_sha256']:
        raise ValueError('original registration file changed')
    if (original.get('registration_sha256') != registration_hash(original) or
            reg['original_registration_sha256'] != original['registration_sha256']):
        raise ValueError('original registration identity mismatch')
    for key in ('stage_id','ordered_seed_list','families','policy_ids','policies','cells','total_cells','analysis'):
        if reg.get(key) != original.get(key):raise ValueError('fixed experiment changed: '+key)
    grid=[dict(stage_id=reg['stage_id'],seed=s,family=f,policy_id=a,
               cell_key=f"{reg['stage_id']}_{s}_{f}_{a}") for s,f,a in itertools.product(
               reg['ordered_seed_list'],reg['families'],reg['policy_ids'])]
    if reg['cells'] != grid or reg['total_cells'] != 2880 or len(reg['ordered_seed_list']) != 96 or len(reg['families']) != 6 or len(reg['policy_ids']) != 5:
        raise ValueError('not the original fixed2880-cell grid')
    if reg['resource_forecast'] != original['resource_forecast']:
        raise ValueError('execution resource caps changed')
    if reg['storage'] != {'codec':'zstd','level':3,'max_evidence_bytes':15*2**30,
                         'audit_transient_max_bytes':512*2**20,'raw_attempt_max_bytes':512*2**20}:
        raise ValueError('storage codec/budget changed')
    note=reg.get('recovery_note_path')
    if type(note) is not str or Path(note).is_absolute() or '..' in Path(note).parts or not (root/note).resolve().is_relative_to(root.resolve()):
        raise ValueError('unsafe recovery note path')
    if (root/note).is_symlink() or file_sha256(root/note) != reg['recovery_note_sha256']:
        raise ValueError('recovery note changed')
    retained=reg['retained_commits'];keys={c['cell_key'] for c in grid}
    if (len({r['cell_key'] for r in retained}) != len(retained) or
        any(set(r) != {'cell_key','commit_sha256'} or r['cell_key'] not in keys or
            type(r['commit_sha256']) is not str or len(r['commit_sha256']) != 64 or
            any(c not in '0123456789abcdef' for c in r['commit_sha256']) for r in retained)):
        raise ValueError('invalid retained commit list')
    if reg['completed_at_recovery'] != len(retained) or reg['remaining_cells'] != 2880-len(retained):
        raise ValueError('recovery counts inconsistent')
    for rel, digest in original['source_manifest'].items():
        if reg['source_manifest'].get(rel) != digest:
            raise ValueError('original executable source changed: '+rel)
    if check_sources:
        if not set(manifest(root,original)).issubset(reg['source_manifest']):
            raise ValueError('continuation source dependency missing')
        for rel,digest in reg['source_manifest'].items():
            if Path(rel).is_absolute() or '..' in Path(rel).parts or not (root/rel).resolve().is_relative_to(root.resolve()):
                raise ValueError('unsafe source path')
            if file_sha256(root/rel) != digest:raise ValueError('source hash mismatch: '+rel)
    if output is not None:
        output=Path(output)
        for row in retained:
            p=output/'commits'/(row['cell_key']+'.json')
            if p.is_symlink() or not p.is_file() or file_sha256(p)!=row['commit_sha256']:
                raise ValueError('retained commit changed/missing: '+row['cell_key'])
    return original


def verify_commit_identity(output, row, reg, original):
    output=Path(output);key=row['cell']['cell_key']
    expected={c['cell_key']:c for c in reg['cells']}
    if key not in expected or row['cell']!=expected[key]:raise ValueError('commit cell not in fixed grid')
    retained={r['cell_key']:r['commit_sha256'] for r in reg['retained_commits']}
    if key in retained:
        if file_sha256(output/'commits'/(key+'.json'))!=retained[key]:raise ValueError('retained bytes changed')
        expected_reg=original
    else:expected_reg=reg
    if row['registration_sha256']!=expected_reg['registration_sha256'] or row['source_sha256']!=expected_reg['source_manifest']:
        raise ValueError('commit source/registration attribution mismatch')
    if row.get('is_valid') is not True or row.get('metrics',{}).get('valid') is not True:
        raise ValueError('invalid committed version')
    return expected_reg


def build(original_path, output, recovery_note, *, root=ROOT):
    original_path=Path(original_path).resolve();output=Path(output).resolve()
    original=strict_json(original_path.read_text())
    cells={c['cell_key']:c for c in original['cells']}
    retained=[]
    for p in sorted((output/'commits').glob('*.json')):
        if p.is_symlink():raise ValueError('symlink commit')
        row=strict_json(p.read_text());key=row['cell']['cell_key']
        if key not in cells or row['cell']!=cells[key] or not row['is_valid'] or not row['metrics']['valid']:
            raise ValueError('cannot retain invalid/mismatched cell')
        if row['registration_sha256']!=original['registration_sha256'] or row['source_sha256']!=original['source_manifest']:
            raise ValueError('cannot retain different source version')
        retained.append({'cell_key':key,'commit_sha256':file_sha256(p)})
    reg={k:original[k] for k in ('stage_id','ordered_seed_list','families','policy_ids','policies','cells','total_cells','analysis','resource_forecast')}
    reg.update(schema_version=SCHEMA,status='frozen_storage_only_continuation',execution_authorized=True,
        original_registration_path=str(original_path.relative_to(root.resolve())),
        original_registration_sha256=original['registration_sha256'],
        original_registration_file_sha256=file_sha256(original_path),retained_commits=retained,
        completed_at_recovery=len(retained),remaining_cells=2880-len(retained),
        source_manifest=manifest(root,original),storage={'codec':'zstd','level':3,'max_evidence_bytes':15*2**30,
                         'audit_transient_max_bytes':512*2**20,'raw_attempt_max_bytes':512*2**20},
        recovery_note_path=str(Path(recovery_note).resolve().relative_to(root.resolve())),
        recovery_note_sha256=file_sha256(recovery_note),
        scope='same fixed development worlds; not fresh seeds; retained and new source identities distinguished')
    reg['registration_sha256']=registration_hash(reg)
    verify_continuation(reg,original,root=root,output=output)
    return reg
