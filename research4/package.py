"""Completed-round consistency/preservation gate; no statistical fishing."""
from datetime import datetime,timezone
import hashlib,json,subprocess,io
from contextlib import redirect_stdout
from pathlib import Path
from research3.analyze import analyze
from research4.benchmark import hashes
from research4.archive import verify

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def main():
    root=Path('results/research4');freeze=json.loads((root/'freeze.json').read_text());screen=json.loads((root/'screen_freeze.json').read_text())
    assert hashes()==freeze['code_hashes']==screen['code_hashes']
    assert sha('research4/EXPERIMENT_REGISTRY.md')==freeze['registry_sha256']==screen['registry_sha256']
    for stage in ('screen','focus','selection','confirmation'):
        stats=analyze(root/(stage+'.json'));assert stats['code_hashes']==hashes()
    raw=json.loads((root/'confirmation.json').read_text());assert raw['planned_seeds']==list(range(freeze['confirmation_seeds'][0],freeze['confirmation_seeds'][1]+1));assert set(raw['planned_policies'])=={'greedy',freeze['policy']};assert len(raw['planned_seeds'])==freeze['confirmation_n']
    env=json.loads((root/'environment.json').read_text());assert sha('results/research3/manifest.json')==env['prior_round_manifest_sha256']
    old=json.loads(Path('results/research3/manifest.json').read_text());older=json.loads(Path('results/research3/inherited_manifest.json').read_text());changed=[]
    exceptions=json.loads((root/'inherited_manifest_exceptions.json').read_text())
    allowed={e['path']:e for e in exceptions['exceptions']}
    fixed={'research3/FINAL_REVIEW.md':'40df3e70a1945873fbfb5be246c3822ca049e5eaebf2e1de77b6df9fe289a1dc','research3/REPLICATION.md':'035a70fe0f2f1d5c5e2f01aece8118476c495e5e8cdda8ea94f3b29dec56abe5','results/research3/package_gate.log':'72c47f6c125de4ec18d0eb4a3a7ff5fb03b00af462a2829a66956eb558ab39ef'}
    assert set(allowed)==set(fixed) and exceptions['prior_manifest_sha256']==env['prior_round_manifest_sha256']
    for p,e in allowed.items():
        assert e['current_sha256']==fixed[p]==sha(p) and e['manifest_record']==old['files'][p]
        assert sha(e['manifest_matching_prefix_copy'])==e['manifest_record']['sha256']
        assert Path(p).read_bytes()[:e['manifest_record']['bytes']]==Path(e['manifest_matching_prefix_copy']).read_bytes()
    for mapping in (old['files'],older['files']):
        for p,r in mapping.items():
            if not Path(p).is_file() or (sha(p)!=r['sha256'] and p not in allowed):changed.append(p)
    assert not changed,changed[:10]
    required=['research4/FINAL_REPORT.md','research4/FINAL_REVIEW.md','research4/REPLICATION.md','research4/MECHANISMS.md','research4/CRITIC.md','research4/STATISTICAL_REVIEW.md','research4/IMPLEMENTATION_REVIEW.md','research4/PRODUCTION_REVIEW.md','research4/PREDICTION_REVIEW.md','research4/LITERATURE.md','research4/REPRODUCTION.md','research4/PACKAGE_REVIEW.md','research4/PROVENANCE_RECONCILIATION.md','research4/ORGANIZATION.md','research4/TRAJECTORY_REVIEW.md','results/research4/compute_summary.json','results/research4/deadline_audit_confirmation.json','results/research4/prediction_audit.json','results/research4/replication_confirmation.json','results/research4/production_selected.json','results/research4/confirmation_claim.json','results/research4/confirmation_mechanisms.json','results/research4/focus_ablations.json']
    for p in required:assert Path(p).is_file(),p
    production=json.loads((root/'production_selected.json').read_text());assert production['valid'] and not production['prepare_only'];assert len(production['rows'])==3 and {r['execution'] for r in production['rows']}=={'direct','subprocess','container'}
    for row in production['rows']:
        assert row['candidate']==freeze['policy'] and row['valid'] and len(row['calls'])==120 and row['captured_fallback_warning_count']==0
        if row['execution']=='direct':assert row['optimized_fallback_count']==0
    assert all(production['equivalence'].values());assert production['resource_probe']['valid'];assert production['image']['below_documented_2GiB']
    probe=production['resource_probe']['probe'];cgroups=probe['cgroups']
    quota,period=map(int,cgroups['cpu.max'].split());assert 0<quota/period<=2
    assert 0<int(cgroups['memory.max'])<=1024**3 and int(cgroups['memory.swap.max'])==0
    assert 0<int(cgroups['pids.max'])<=64 and probe['uid']==65534 and probe['gid']==65534
    assert probe['root_write_errno']==30 and probe['egress_errno']==101 and '--network=none' in production['resource_probe']['command']
    assert 0<production['image']['size_bytes']<2*1024**3 and production['image']['user']=='65534:65534'
    app_sources={'kit.py','research/terminal_model.py','research3/__init__.py','research3/policy.py','research3/model_candidates.py','research4/__init__.py','research4/policy.py','research4/candidates.py'}
    assert set(probe['source_hashes'])==set(production['resource_probe']['host_source_hashes'])==app_sources
    for p in app_sources:assert sha(p)==probe['source_hashes'][p]==production['resource_probe']['host_source_hashes'][p]==production['source_hashes'][p]
    metric_keys={'assignments','mutual_acceptances','dates','mutual_second_meeting_intention','missing_feedback','ask_cost','arrived_members','msmi_per_100_arrived_members','status','valid','served_members','unserved_members','coverage','mutual_acceptances_per_100','first_introduction_wait_days','action_sha256','semantic_action_sha256'}
    for metric in metric_keys:assert all(row[metric]==production['rows'][0][metric] for row in production['rows'])
    for row in production['rows']:
        for call in row['calls']:
            assert call['seconds']<10 and call['request_bytes']<=1024**2 and call['memory_bytes']<1024**2
    for p,v in freeze['code_hashes'].items():
        if p in production['source_hashes']:assert production['source_hashes'][p]==v
    replica=json.loads((root/'replication_confirmation.json').read_text());runs=replica.get('runs',[replica]);rep_rows=[r for run in runs for r in run['episodes']];assert any(r['policy']==freeze['policy'] for r in rep_rows)
    expected={(p,s,v,m) for p in ('greedy',freeze['policy']) for s in (83001,83002) for v in raw['planned_variants'] for m in ('direct','subprocess')}
    found=[(r['policy'],r['seed'],r['variant'],r['execution']) for r in rep_rows]
    assert len(found)==len(expected)==48 and set(found)==expected
    for run in runs:
        for p,h in run['source_hashes'].items():assert sha(p)==h
    for row in rep_rows:assert row['valid'] and not row['fallback_count'] and not row.get('metric_differences') and all(row.get(k) for k in ('byte_digest_match','semantic_digest_match','ordered_actions_equal','semantic_actions_equal'))
    audits=[run['independent_statistics'] for run in runs if 'independent_statistics' in run];assert audits and audits[-1]['clusters'][freeze['policy']]['n']==freeze['confirmation_n']
    independent=audits[-1]['clusters'][freeze['policy']]
    official=analyze(root/'confirmation.json')['policies'][freeze['policy']]['paired']
    assert abs(independent['paired_difference']-official['mean'])<1e-12
    current_stats=analyze(root/'confirmation.json')['policies']
    for p in ('greedy',freeze['policy']):assert abs(audits[-1]['clusters'][p]['mean']-current_stats[p]['primary']['mean'])<1e-12
    assert all(abs(a-b)<1e-12 for a,b in zip(independent['ci95'],official['ci95']))
    claim=json.loads((root/'confirmation_claim.json').read_text())
    checks=audits[-1]['confirmation_checks']
    assert claim['program_superiority']==checks['program_superiority'] and claim['nominal_superiority']==checks['nominal_superiority']
    assert all(abs(a-b)<1e-12 for a,b in zip(claim['program98_333333'],checks['program_ci98_333333']))
    wrapper=json.loads((root/'production_wrapper.json').read_text());diverse=json.loads((root/'production_diverse.json').read_text())
    assert wrapper['valid'] and diverse['all_optimized_pass'] and len(diverse['rows'])==8
    assert all(r['optimized_pass'] and not r['error'] and not r['direct_fallback_count'] and not r['container_fallback_warning_count'] for r in diverse['rows'])
    verified=io.StringIO()
    with redirect_stdout(verified):verify()
    # Finalize our own gate log before hashing. Never redirect stdout to this log.
    (root/'package_gate.log').write_text(verified.getvalue()+'All pre-manifest consistency gates passed. This log is finalized before provenance serialization; final completion is recorded by manifest.completed and tool stdout.\n')
    files=[p for d in ('research4','results/research4') for p in Path(d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json']
    manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'completed':True,'preserved_round3_files':len(old['files']),'preserved_older_files':len(older['files']),'documented_inherited_metadata_exceptions':exceptions,'prior_manifest_sha256':env['prior_round_manifest_sha256'],'frozen_candidate':freeze,'code_hashes':hashes(),'git_head':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),'files':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)},'scope':'Consistency evidence, not cryptographic proof of historical timestamps or unrecorded seed usage'}
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Completed round4 provenance; preserved',len(old['files']),'+',len(older['files']),'files; new',len(files))
if __name__=='__main__':main()
