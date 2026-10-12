"""Final round-three provenance gate. Run after reports/reviews/archives are final."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from research3.archive import verify
from research3.benchmark import hashes
from research3.analyze import analyze


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def main():
    root=Path('results/research3')
    freeze=json.loads((root/'freeze.json').read_text())
    if freeze['code_hashes']!=hashes():raise ValueError('frozen sources changed')
    confirmation=analyze(root/'confirmation.json')
    data=json.loads((root/'confirmation.json').read_text())
    expected_seeds=list(range(freeze['confirmation_seeds'][0],freeze['confirmation_seeds'][1]+1))
    if data['code_hashes']!=freeze['code_hashes'] or data['planned_seeds']!=expected_seeds or set(data['planned_policies'])!={'greedy',freeze['policy']}:
        raise ValueError('confirmation recorded freeze/grid mismatch')
    if sha('research3/EXPERIMENT_REGISTRY.md')!=freeze['registry_sha256']:
        raise ValueError('registered protocol changed after freeze')
    if confirmation['policies'][freeze['policy']]['primary']['n']!=freeze['confirmation_n']:raise ValueError('wrong confirmation n')
    inherited=json.loads((root/'inherited_manifest.json').read_text())
    changed=[p for p,r in inherited['files'].items() if not Path(p).exists() or sha(p)!=r['sha256']]
    if changed:raise ValueError('inherited artifact changed: '+str(changed[:10]))
    verify()
    required=['research3/FINAL_REPORT.md','research3/FINAL_REVIEW.md','research3/REPLICATION.md',
              'research3/PACKAGE_REVIEW.md','research3/IMPLEMENTATION_REVIEW.md',
              'research3/EXPERIMENT_REGISTRY.md','research3/REPRODUCTION.md',
              'results/research3/confirmation_statistics.json','results/research3/production_selected.json',
              'results/research3/resource_probe.json','results/research3/replication_confirmation.json',
              'results/research3/focus_prediction_audit.json']
    for p in required:
        if not Path(p).is_file():raise ValueError('missing required '+p)
    production=json.loads((root/'production_selected.json').read_text())
    if not production['valid']:raise ValueError('production failed')
    if production['rows'][0]['candidate']!=freeze['policy']:raise ValueError('wrong production candidate')
    for path in ('kit.py','evaluate.py','research/terminal_model.py','research3/policy.py','research3/model_candidates.py'):
        if production['source_hashes'][path]!=freeze['code_hashes'][path]:raise ValueError('production source mismatch')
    for row in production['rows']:
        if len(row['calls'])!=120:raise ValueError('production invocation completeness')
        if row['execution']=='direct' and row.get('optimized_fallback_count')!=0:
            raise ValueError('direct production fallback or unknown telemetry')
        if row['execution']!='direct' and any(call.get('fallback_warning_count')!=0 for call in row['calls']):
            raise ValueError('production fallback warning or unknown telemetry')
    probe=json.loads((root/'resource_probe.json').read_text())
    observed=probe['probe']
    if (observed['cgroups']!={'cpu.max':'200000 100000','memory.max':'1073741824','memory.swap.max':'0','pids.max':'64'}
        or observed['uid']!=65534 or observed.get('root_write_errno')!=30 or observed.get('egress_errno')!=101):
        raise ValueError('effective resource enforcement mismatch')
    for path in ('kit.py','research/terminal_model.py','research3/policy.py','research3/model_candidates.py'):
        if observed['source_hashes'][path]!=freeze['code_hashes'][path]:raise ValueError('probe frozen source mismatch')
    replica=json.loads((root/'replication_confirmation.json').read_text())
    runs=replica.get('runs',[replica])
    rep_rows=[row for run in runs for row in run['episodes']]
    if not any(row['policy']==freeze['policy'] for row in rep_rows):raise ValueError('selected replication missing')
    for row in rep_rows:
        if (not row['valid'] or row['fallback_count'] or row.get('metric_differences')
            or not row.get('byte_digest_match') or not row.get('semantic_digest_match')
            or not row.get('ordered_actions_equal') or not row.get('semantic_actions_equal')):
            raise ValueError('independent replication mismatch')
    audits=[run['independent_statistics'] for run in runs if 'independent_statistics' in run]
    if not audits or audits[-1]['clusters'][freeze['policy']]['n']!=freeze['confirmation_n']:
        raise ValueError('independent full confirmation statistics absent')
    files=[p for d in ['research3','results/research3'] for p in Path(d).rglob('*')
           if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json']
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),completed=True,
                  inherited_files_unchanged=len(inherited['files']),frozen_candidate=freeze,
                  code_hashes=hashes(),git_head=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
                  files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)},
                  scope='Recorded public family experiment; hashes prove consistency, not tamper-proof historical timestamps.')
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Completed provenance: unchanged inherited files',len(inherited['files']),'new files',len(files))


if __name__=='__main__':main()
