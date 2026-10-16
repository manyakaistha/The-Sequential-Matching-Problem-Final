"""One final finite campaign; no reward peeking, retries or extra search."""
import json,os,subprocess,sys,time
from pathlib import Path
from .registration import ROOT,BASE,freeze,verify_registration
from research8.soft_query_followup.v2.registration import write_once,file_sha256

def launch_stage(stage):
    regpath=BASE/(stage+'_registration.json')
    if not regpath.exists():reg=freeze(stage)
    else:reg=json.loads(regpath.read_text());verify_registration(reg)
    out=ROOT/'results/research9/final_campaign'/stage
    env=dict(os.environ,PYTHONPATH=str(ROOT),TMPDIR=str(BASE/'.tmp'),PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    command=[sys.executable,'-B','-m','research9.final_campaign.launcher','--registration',str(regpath),'--output',str(out),'--workers','7']
    with (BASE/(stage+'_launcher.log')).open('xb') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        write_once(BASE/(stage+'_launch.json'),dict(pid=proc.pid,workers=7,started_unix=time.time(),registered_cells=reg['total_cells'],source_registration_sha256=reg['registration_sha256']))
        print(json.dumps({'event':'stage_started','stage':stage,'pid':proc.pid,'cells':reg['total_cells']}),flush=True)
        code=proc.wait()
    if code:raise RuntimeError(stage+' stage failed; all evidence preserved, no automatic retry/repair. Exit'+str(code))
    print(json.dumps({'event':'stage_simulations_complete','stage':stage}),flush=True)

def main():
    (BASE/'.tmp').mkdir(exist_ok=True)
    fit=json.loads((BASE/'fit_freeze.json').read_text())
    for relative,sha in fit['source_manifest'].items():
        if file_sha256(ROOT/relative)!=sha:raise ValueError('fit source changed after freeze: '+relative)
    if not (BASE/'selected_model.json').exists():raise ValueError('fixed fit not complete')
    write_once(BASE/'workflow_start.json',dict(status='running_final_finite_campaign',started_unix=time.time(),screen_cap=336,confirmation_cells=2304,sim_workers=7,scope='one selection then one independent final test; no outcome-based sample extension'))
    from .analyze import select,final_report
    launch_stage('screen')
    selected=select()
    if selected is None:
        report=dict(status='closed_no_candidate_qualified',reason='No fixed candidate exceededG in audited development screen. No final outcome was opened.',selection_sha256=file_sha256(BASE/'selection.json'))
        write_once(BASE/'campaign_closed.json',report)
        (BASE/'FINAL_REPORT.md').write_text('# Final campaign closed\n\nNo candidate qualified in the fixed audited development screen. No final confirmation worlds were opened. Preserve the negative result; no extra fits, seeds or policy variants are authorized by this campaign.\n')
        print(json.dumps(report),flush=True);return
    # Selection and asset are immutable before the first independent final world.
    launch_stage('confirmation')
    final_report()
    write_once(BASE/'campaign_closed.json',dict(status='completed',final_results_sha256=file_sha256(BASE/'final_results.json')))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        path=BASE/'workflow_failure.json'
        if not path.exists():write_once(path,dict(status='stopped_fail_closed',error=type(exc).__name__+': '+str(exc),stopped_unix=time.time(),evidence_preserved=True))
        raise
