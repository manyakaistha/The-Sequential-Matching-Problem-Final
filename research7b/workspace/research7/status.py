"""Read-only progress counters, not an integrity certificate or workload."""
import argparse,collections,datetime,fcntl,json
from pathlib import Path

def snapshot(output):
 output=Path(output);reg=json.loads((output/'registration.json').read_text());rows=[json.loads(p.read_text()) for p in (output/'commits').glob('*.json')];active=False
 if (output/'coordinator.lock').exists():
  with (output/'coordinator.lock').open('r') as lock:
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:active=True
 return {'updated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running' if active else 'complete_pending_final_review' if len(rows)==len(reg['cells']) else 'stopped_incomplete','phase':reg['stage_id'],'planned_cells':len(reg['cells']),'committed_cells':len(rows),'invalid_cells':[{'cell':x['cell'],'error':x['error_message']} for x in rows if not x['is_valid']],'fallbacks':sum(x['metrics'].get('fallback_count',0) for x in rows),'completed_by_policy':dict(collections.Counter(x['cell']['policy_id'] for x in rows)),'cpu_seconds_completed':sum(x['metrics'].get('cpu_seconds',0) for x in rows),'bytes_current':sum(p.stat().st_size for p in output.rglob('*') if p.is_file()),'physical_world_records':len(list((output/'attempts').glob('*/*/privileged/initial_world.bin'))),'scope':'reference-only integration/resource calibration; progress counters are not an integrity certificate'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default='results/research7/research7_20261012/7b/P1_smoke');p.add_argument('--save',action='store_true');a=p.parse_args();d=snapshot(a.output)
 if a.save:(Path(a.output)/'progress.json').write_text(json.dumps(d,indent=2)+'\n')
 print(json.dumps(d,indent=2))
if __name__=='__main__':main()
