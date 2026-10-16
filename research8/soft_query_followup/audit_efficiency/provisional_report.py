"""Reuse the registered statistic code; no audit rerun, no raw-log extraction.

Results are explicitly provisional until the full independent proof completes.
Only unchanged committed endpoint metrics enter the seven registered contrasts.
"""
import inspect,json,hashlib
from pathlib import Path
from research8.soft_query_followup.v2 import analysis
from research8.soft_query_followup.v3.continuation import verify_continuation,verify_commit_identity
from research8.soft_query_followup.v2.registration import ROOT


def main():
    base=ROOT/'research8/soft_query_followup/audit_efficiency'
    out=ROOT/'results/research8/soft_query_followup/v2_replication'
    regpath=ROOT/'research8/soft_query_followup/storage_recovery/continuation_registration.json'
    reg=json.loads(regpath.read_text());original=verify_continuation(reg,output=out)
    commits={}
    for path in (out/'commits').glob('*.json'):
        row=json.loads(path.read_text());verify_commit_identity(out,row,reg,original)
        commits[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
    assert len(commits)==2880
    source=inspect.getsource(analysis.analyze)
    anchor='    closure = audit_run(output, registration_path)\n'
    assert source.count(anchor)==1
    source=source.replace(anchor,"    closure = {'status':'pending_full_independent_audit','complete_registered_grid':True,'public_event_reconstruction_verified':False}\n")
    start=source.index('    diagnostics = {}\n');end=source.index("    return {'status':",start)
    source=source[:start]+"    diagnostics = {'status':'deferred; no duplicate raw-log scan'}\n"+source[end:]
    source=source.replace("'status': 'audited_development_results'","'status': 'provisional_completed_grid_results_audit_pending'")
    namespace=dict(analysis.__dict__);exec(compile(source,str(Path(__file__))+':registered_statistics','exec'),namespace)
    report=namespace['analyze'](out,regpath)
    report['warning']='Not independently certified yet; do not treat as an audited winner or fresh-seed confirmation.'
    report['commit_inventory_sha256']=hashlib.sha256(json.dumps(commits,sort_keys=True).encode()).hexdigest()
    report['registered_statistics_source_sha256']=hashlib.sha256(inspect.getsource(analysis.analyze).encode()).hexdigest()
    path=base/'provisional_results.json'
    with path.open('x') as stream:json.dump(report,stream,indent=2,allow_nan=False)
    print(json.dumps({'status':report['status'],'report':str(path),'arm_means':{k:v['mean_msmi'] for k,v in report['arm_summary'].items()},'contrasts':{k:{'delta':v['mean_diff'],'p_holm':v['p_value_holm']} for k,v in report['contrasts'].items()}},indent=2))
if __name__=='__main__':main()
