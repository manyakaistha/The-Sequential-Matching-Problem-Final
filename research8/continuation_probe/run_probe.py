"""Run the fixed development probe once, then audit/report it without replay."""
from pathlib import Path
import json,os,subprocess,sys,time
from .registration import ROOT,freeze,write_once

def main():
    base=ROOT/'research8/continuation_probe'
    freeze()
    out=ROOT/'results/research8/continuation_probe/v1'
    env=dict(os.environ,PYTHONPATH=str(ROOT),TMPDIR=str(base/'.tmp'),PYTHONDONTWRITEBYTECODE='1')
    (base/'.tmp').mkdir(exist_ok=True)
    cmd=[sys.executable,'-B','-m','research8.continuation_probe.launcher','--registration',str(base/'registration.json'),'--output',str(out),'--workers','7']
    with (base/'launch.log').open('xb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        write_once(base/'launch_record.json',dict(pid=proc.pid,workers=7,started_unix=time.time(),scope='fixed24-cell reused-development mechanism probe; no fresh evidence'))
        print('Fixed24-cell mechanism probe started, coordinator '+str(proc.pid),flush=True)
        result=proc.wait()
    if result:raise RuntimeError('Probe stopped; preserve all artifacts and inspectlaunch.log. Exit '+str(result))
    print('All24cells finished; one independent archive-aware audit/report pass.',flush=True)
    from .summarize import main as summarize
    summarize()
if __name__=='__main__':main()
