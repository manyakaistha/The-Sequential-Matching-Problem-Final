"""Single coordinator, bounded process workers; no container admission claim."""
import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import fcntl
import importlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import time

from .leases import CellLease, LeaseManager
from .recorder import DurableRecorder, write_json
from .runner import RegisteredRunner, RunnerBlockerError


def output_size(path):
    return sum(p.stat().st_size for p in Path(path).rglob('*') if p.is_file())

def worker(job):
    workspace, registration, output, cell, lease_data = job
    caps = registration['resource_forecast']
    def interrupted(signum, frame):
        raise TimeoutError('Physical attempt resource guard')
    signal.signal(signal.SIGALRM, interrupted)
    signal.signal(signal.SIGPROF, interrupted)
    signal.setitimer(signal.ITIMER_REAL, caps.get('max_attempt_wall_seconds',180))
    signal.setitimer(signal.ITIMER_PROF, caps.get('max_attempt_cpu_seconds',90))
    try:
        spec=registration['policies'][cell['policy_id']]
        module,name=spec['entrypoint'].split(':')
        runner=RegisteredRunner(Path(workspace),registration,DurableRecorder(output),LeaseManager(Path(output)/'leases.jsonl'))
        row=runner.execute_cell_guarded(cell,getattr(importlib.import_module(module),name),spec['config'],CellLease(**lease_data))
        usage=resource.getrusage(resource.RUSAGE_SELF)
        children=resource.getrusage(resource.RUSAGE_CHILDREN)
        row['worker_cpu_seconds']=usage.ru_utime+usage.ru_stime+children.ru_utime+children.ru_stime
        return row
    finally:
        signal.setitimer(signal.ITIMER_REAL,0); signal.setitimer(signal.ITIMER_PROF,0)


def run_registered(registration, output, workspace, workers=6):
    if type(workers) is not int or not 1<=workers<=8:
        raise RunnerBlockerError('ThisMac coordinator permits 1 to 8 workers')
    output,workspace=Path(output),Path(workspace)
    output.mkdir(parents=True,exist_ok=True)
    lock=(output/'coordinator.lock').open('a')
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close(); raise RunnerBlockerError('Another coordinator owns this output')
    try:
        from research7.registry.validator import RegistrationValidator
        ready, blockers = RegistrationValidator(workspace).validate_executable_readiness(registration)
        if not ready: raise RunnerBlockerError('\n'.join(blockers))
        if not registration.get('cells'): raise RunnerBlockerError('Empty grid')
        recorder=DurableRecorder(output)
        reconciliation=recorder.reconcile()
        expected={c['cell_key']:c for c in registration['cells']}
        for key,commit in reconciliation['commits'].items():
            if key not in expected or commit['cell'] != expected[key]:
                raise RunnerBlockerError('Output contains commit outside this exact registration')
        manager=LeaseManager(output/'leases.jsonl')
        # Commits publish before lease journal; repair only verified published commits.
        for key,commit in reconciliation['commits'].items():
            manager.committed_cells.add(key)
            lease=manager.active_leases.pop(key,None)
            if lease:
                lease.status='committed'; manager._append(lease)
        cells=registration.get('cells',[])
        runner=RegisteredRunner(workspace,registration,recorder,manager)
        for cell in cells:
            blockers=runner.check_execution_blockers(cell)
            if blockers: raise RunnerBlockerError('\n'.join(blockers))
        caps=registration['resource_forecast']
        reservation=caps.get('max_attempt_cpu_seconds',90)
        attempts=list((output/'attempts').glob('*/*/started.json'))
        reservations_dir=output/'reservations'
        reservations_dir.mkdir(exist_ok=True)
        used_attempts=max(len(attempts),len(list(reservations_dir.glob('*.json'))))
        max_attempts=caps.get('max_physical_attempts',len(cells))
        def guard():
            coordinator_rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if __import__('sys').platform=='darwin' else 1024)
            if coordinator_rss>1024**3: raise RunnerBlockerError('Coordinator RSS reserve exceeded')
            if (used_attempts+1)*reservation>caps['max_cpu_hours']*3600:
                raise RunnerBlockerError('CPU physical-attempt reservation exhausted')
            if used_attempts>=max_attempts: raise RunnerBlockerError('Physical attempt ceiling exhausted')
            if output_size(output)+caps.get('max_attempt_output_bytes',32*1024**2)*(workers+1)>=caps['max_output_gib']*1024**3: raise RunnerBlockerError('Output budget exhausted')
            if shutil.disk_usage(output).free-caps.get('max_attempt_output_bytes',32*1024**2)*(workers+1)<=caps['free_reserve_gib_min']*1024**3:
                raise RunnerBlockerError('Free storage reserve reached')
        if any(a['state']=='interrupted' for a in reconciliation['attempts']):
            raise RunnerBlockerError('Interrupted attempt requires explicit infrastructure retry review; evidence preserved')
        queue=[c for c in cells if c['cell_key'] not in reconciliation['commits']]
        results=[]; pending={}
        with ProcessPoolExecutor(max_workers=workers) as pool:
            while queue or pending:
                while queue and len(pending)<workers:
                    guard(); cell=queue.pop(0)
                    # Every scheduled attempt consumes its full CPU reservation, also on failure.
                    lease=manager.issue_lease(cell['cell_key'],'mac-01',duration_seconds=int(caps.get('max_attempt_wall_seconds',180)+60))
                    write_json(reservations_dir/(lease.lease_id+'.json'),dict(cell=cell,lease=lease.to_dict(),cpu_seconds=reservation,output_bytes=caps.get('max_attempt_output_bytes',32*1024**2)))
                    used_attempts+=1
                    future=pool.submit(worker,(str(workspace),registration,str(output),cell,lease.to_dict()))
                    pending[future]=cell
                done,_=wait(pending,timeout=1,return_when=FIRST_COMPLETED)
                for future in done:
                    cell=pending.pop(future)
                    try:
                        results.append(future.result())
                    except BaseException as exc:
                        write_json(output/('worker_error_'+cell['cell_key']+'_'+str(time.time_ns())+'.json'),dict(cell=cell,error=repr(exc)))
                        # Stop launch; preserve running attempts and every error.
                        queue.clear()
                        raise
        final=recorder.reconcile()
        return dict(committed=len(final['commits']),valid=set(final['commits'])==set(expected) and all(c['is_valid'] for c in final['commits'].values()),attempts=final['attempts'])
    finally:
        lock.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--registration',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--workers',type=int,default=6)
    parser.add_argument('--workspace',default=str(Path(__file__).resolve().parents[2]))
    args=parser.parse_args()
    try:
        result=run_registered(json.loads(Path(args.registration).read_bytes()),args.output,args.workspace,args.workers)
        print(json.dumps(result)); return 0 if result['valid'] else 2
    except Exception as exc:
        print(json.dumps({'blocked':True,'error':str(exc)})); return 2

if __name__=='__main__': raise SystemExit(main())
