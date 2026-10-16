from pathlib import Path
import json, os, subprocess, sys, time
from research8.soft_query_followup.v3.continuation import build
from research8.soft_query_followup.v2.registration import ROOT, write_once
base=ROOT/'research8/soft_query_followup/storage_recovery'
output=ROOT/'results/research8/soft_query_followup/v2_replication'
proof=json.loads((base/'diagnostic_replay_result.json').read_text())
assert len(proof['results'])==2 and all(x['exact_world_action_endpoint_parity'] and x['audit']['status']=='passed' for x in proof['results'])
reg=build(base/'campaign_before_recovery/replication_registration.json',output,base/'recovery_note.md')
assert reg['completed_at_recovery']==480 and reg['remaining_cells']==2400
regpath=base/'continuation_registration.json'
write_once(regpath,reg)
log=base/'continuation_launcher.log'
env=dict(os.environ,PYTHONPATH=str(ROOT),TMPDIR=str(ROOT/'research8/soft_query_followup/v2/.tmp'),PYTHONDONTWRITEBYTECODE='1')
with log.open('xb') as stream:
    proc=subprocess.Popen([sys.executable,'-B','-m','research8.soft_query_followup.v3.launcher','--registration',str(regpath),'--output',str(output),'--workers','7'],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
record=dict(pid=proc.pid,registration_sha256=reg['registration_sha256'],retained_cells=480,remaining_cells=2400,workers=7,log=str(log),started_unix=time.time())
write_once(base/'continuation_launch_record.json',record)
print(json.dumps(record,indent=2))
