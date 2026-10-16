"""Bind the existing registered statistics to the completed independent proof."""
import hashlib,json
from pathlib import Path
from research8.soft_query_followup.audit_efficiency.fast_audit import digest,_evidence_identity
from research8.soft_query_followup.v2.registration import ROOT

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    base=ROOT/'research8/soft_query_followup/audit_efficiency'
    out=ROOT/'results/research8/soft_query_followup/v2_replication'
    proofpath=base/'full_grid_proof.json';proof=json.loads(proofpath.read_text())
    assert proof['payload_sha256']==digest({k:v for k,v in proof.items() if k!='payload_sha256'})
    assert proof['result']['status']=='passed' and proof['result']['verified_cells']==2880 and proof['result']['complete_registered_grid']
    checkpoints={}
    expected={x['cell_key']:x['checkpoint_sha256'] for x in proof['checkpoints']}
    for p in (base/'checkpoints').glob('*.json'):
        row=json.loads(p.read_text());key=row['cell_key']
        assert key not in checkpoints and sha(p)==expected[key]
        assert row['payload_sha256']==digest({k:v for k,v in row.items() if k!='payload_sha256'})
        checkpoints[key]=row
    commits={}
    for p in (out/'commits').glob('*.json'):
        row=json.loads(p.read_text());key=row['cell']['cell_key'];checkpoint=checkpoints[key]
        assert checkpoint['binding']['commit']==dict(sha256=sha(p),bytes=p.stat().st_size)
        assert _evidence_identity(out,row)==checkpoint['binding']['evidence']
        assert checkpoint['result']['metrics']==row['metrics']
        commits[p.name]=sha(p)
    assert len(commits)==len(checkpoints)==len(expected)==2880
    for relative,digest_value in proof['sources'].items():assert sha(ROOT/relative)==digest_value
    report=json.loads((base/'provisional_results.json').read_text())
    assert report['commit_inventory_sha256']==hashlib.sha256(json.dumps(commits,sort_keys=True).encode()).hexdigest()
    report.pop('warning',None)
    report.update(status='audited_development_results',independent_public_event_audit=proof['result'],audit_proof_sha256=sha(proofpath),audit_proof_path=str(proofpath.relative_to(ROOT)),inference_scope='same fixed development experiment; not fresh confirmation; mechanism diagnostics deferred')
    dest=ROOT/'research8/continuation_probe'
    with (dest/'previous_final_results.json').open('x') as stream:json.dump(report,stream,indent=2,allow_nan=False)
    lines=['# Completed soft-query follow-up','', 'All2,880cells passed independent public-event audit.96seed clusters, six families and five arms. Statistics reuse the registered seven contrasts and Holm adjustment. This is development evidence, not fresh confirmation.','', '| Arm | MSMI/100 | Qualified pairs |','|---|---:|---:|']
    for arm,s in report['arm_summary'].items():lines.append(f"| {arm} | {s['mean_msmi']:.6f} | {s['qualified_total']} |")
    lines+=['','| Contrast | Difference | Exploratory95%CI | Holm p |','|---|---:|---|---:|']
    for name,c in report['contrasts'].items():lines.append(f"| {name} | {c['mean_diff']:+.6f} | {c['ci_95_exploratory']} | {c['p_value_holm']:.6f} |")
    lines+=['','No registered contrast establishes superiority. Targeted soft filling has a positive descriptive difference versus G but falls below Q6/P. Do not promote it or spend another large replication solely on this result. Mechanism diagnostics remain deferred; the completed full audit is reused without replay.']
    (dest/'PREVIOUS_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print('Bound all2880commits and compressed evidence identities to completed proof; final results saved.')
if __name__=='__main__':main()
