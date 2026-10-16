from pathlib import Path
import fcntl, json, os
from research8.soft_query_followup.v3.continuation import build
from research8.soft_query_followup.v3.runner import Research8Runner
from research8.soft_query_followup.v3.audit import audit_cell
from research8.soft_query_followup.v2.registration import ROOT, write_once
base=ROOT/'research8/soft_query_followup/storage_recovery'
output=base/'diagnostic_replay'
output.mkdir(exist_ok=True)
original=base/'campaign_before_recovery/replication_registration.json'
reg=build(original,output,base/'recovery_note.md')
write_once(base/'diagnostic_registration.json',reg)
results=[]
with (ROOT/'research8/soft_query_followup/v2/.simulation.lock').open('a') as lease:
    fcntl.flock(lease.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    for arm in ('G','Q6'):
        cell=next(c for c in reg['cells'] if c['seed']==840001 and c['family']=='development' and c['policy_id']==arm)
        row=Research8Runner(ROOT,reg,output).execute_cell(cell)
        old=json.loads((ROOT/'results/research8/soft_query_followup/v2_replication/commits'/(cell['cell_key']+'.json')).read_text())
        assert row['is_valid'],row['error']
        for key in ('world_sha256','action_sha256','metrics','invocation_count','fallback_count'):
            assert row[key]==old[key],(arm,key)
        proof=audit_cell(output,row,reg)
        results.append(dict(arm=arm,exact_world_action_endpoint_parity=True,audit=proof))
        print(arm,'exact parity and independent audit passed',flush=True)
write_once(base/'diagnostic_replay_result.json',dict(scope='already-retained diagnostic replays; not extra study samples',results=results))
