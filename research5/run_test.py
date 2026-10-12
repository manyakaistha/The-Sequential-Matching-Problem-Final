"""Run one immutable fresh test; --check performs no episode/world generation."""
from datetime import datetime,timezone
import argparse,hashlib,json,math,resource,shutil,subprocess,sys,time
import os,selectors,signal
from pathlib import Path
from research4.benchmark import hashes

ROOT=Path('results/research5')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def check():
    design=json.loads((ROOT/'design.json').read_text())
    import numpy,scipy
    assert numpy.__version__==design['versions']['numpy'] and scipy.__version__==design['versions']['scipy']
    assert design['frozen_inherited_hashes']==hashes(),'Frozen inherited code changed'
    for section in ('initializer_hashes','setup_source_hashes','analysis_helper_hashes'):
        for path,h in design[section].items():assert sha(path)==h,path
    assert sha('research5/EXPERIMENT_REGISTRY.md')==design['registry_sha256']
    assert sha('results/research4/manifest.json')==design['prior_manifest_sha256']
    assert design['n_clusters']==430 and design['seeds']==list(range(90001,90431))
    assert design['policies']==['greedy','population_control'] and design['planned_episodes']==5160
    assert not set(design['seeds'])&set(design['seed_inventory']['blocked_seeds'])
    if design.get('recovery'):
        recovery=design['recovery']
        assert sha(recovery['source_result'])==recovery['source_result_sha256']
        assert sha(recovery['archive']+'/design.json')==recovery['prior_design_sha256']
        assert sha(recovery['archive_manifest'])==recovery['archive_manifest_sha256']
        evidence=json.loads(Path(recovery['archive_manifest']).read_text())
        for path,expected in evidence['files'].items():
            assert Path(path).stat().st_size==expected['bytes'] and sha(path)==expected['sha256'],path
    return design

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    print("[CHECK] Checking registered design, frozen policy hashes and software versions...", flush=True)
    design=check()
    if args.check:
        print('Prepared immutable test passes preflight; no worlds generated or episodes executed.');return
    target=ROOT/'confirmation.json'
    for path in (target,ROOT/'execution.json',ROOT/'confirmation.log',ROOT/'confirmation_traces',ROOT/'confirmation_traces_full'):
        if path.exists():raise ValueError(f'Refuse duplicate/partial test: {path}. Preserve artifacts; do not rerun missing outcomes ad hoc.')
    required=design['logging']['minimum_free_disk_bytes']
    free=shutil.disk_usage(ROOT).free
    print(f'[CHECK] Disk: {free/1e9:.1f} GB free; {required/1e9:.0f} GB required.', flush=True)
    if shutil.disk_usage(ROOT).free<required:raise ValueError('Insufficient projected free disk space for full fixed sample and archives')
    command=[sys.executable,'-m','research5.benchmark','--policies',','.join(design['policies']),'--seeds','90001:90430','--workers',str(design['research_workers']),'--variants','all','--output',str(target),'--traces',str(ROOT/'confirmation_traces')]
    if design.get('recovery'):
        command += ['--resume-from', design['recovery']['source_result']]
        print(f"[RECOVERY] Preserving {design['recovery']['preserved_rows']} archived episodes; remaining cells use the same fixed sample.", flush=True)
    print(f"[START] 430 seeds × 6 families × 2 policies = 5,160 episodes; {design['research_workers']} workers.", flush=True)
    print(f'[LOGGING] Console: {ROOT / "confirmation.log"}', flush=True)
    print(f'[LOGGING] Full requests/responses: {ROOT / "confirmation_traces_full"}', flush=True)
    print('[WAIT] Starting workers. Heartbeat every 15 seconds while waiting; scores are withheld until the full test ends.', flush=True)
    execution={'started_utc':datetime.now(timezone.utc).isoformat(),'command':command,'design_sha256':sha(ROOT/'design.json'),'status':'running','required_free_disk_bytes':required,'notes':'No interim effect computation, no significance stopping or sample extension. All rows/failures retained.'}
    (ROOT/'execution.json').write_text(json.dumps(execution,indent=2)+'\n')
    cpu=resource.getrusage(resource.RUSAGE_CHILDREN);started=time.perf_counter()
    returncode = None
    interrupted = False
    with (ROOT/'confirmation.log').open('x') as out:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, bufsize=1, start_new_session=True)
        execution['pid']=proc.pid
        (ROOT/'execution.json').write_text(json.dumps(execution,indent=2)+'\n')
        selector = selectors.DefaultSelector()
        selector.register(proc.stdout, selectors.EVENT_READ)
        last_notice = time.monotonic()
        progress_active = False
        try:
            while True:
                ready = selector.select(timeout=1)
                if ready:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    out.write(line);out.flush()
                    if line.startswith('[PROGRESS]') and sys.stdout.isatty():
                        sys.stdout.write('\r' + line.rstrip() + '     ');sys.stdout.flush()
                        progress_active=True
                    else:
                        if progress_active:
                            print();progress_active=False
                        print(line, end='', flush=True)
                    last_notice=time.monotonic()
                elif time.monotonic()-last_notice >= 15:
                    if progress_active:
                        print();progress_active=False
                    message=f'[RUNNING] Elapsed {(time.perf_counter()-started)/60:.1f}m; workers active, writing episode logs. Waiting for next completed episode.'
                    print(message,flush=True);out.write(message+'\n');out.flush()
                    last_notice=time.monotonic()
            returncode=proc.wait()
        except KeyboardInterrupt:
            interrupted=True
            print('\n[STOP] Interrupt received; stopping worker process group and retaining partial logs.',flush=True)
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            returncode=proc.returncode
        finally:
            selector.close()
            proc.stdout.close()

    end=resource.getrusage(resource.RUSAGE_CHILDREN)
    execution.update(completed_utc=datetime.now(timezone.utc).isoformat(),status='interrupted' if interrupted else ('completed' if returncode==0 else 'failed'),returncode=returncode,wall_seconds=time.perf_counter()-started,os_child_cpu_seconds=end.ru_utime+end.ru_stime-cpu.ru_utime-cpu.ru_stime)
    (ROOT/'execution.json').write_text(json.dumps(execution,indent=2)+'\n')
    if interrupted:raise KeyboardInterrupt
    if returncode:raise RuntimeError('Failed test retained; no automatic replacement or resampling')
    check()
    print('[ANALYSIS] Full grid complete. Computing registered paired statistics...',flush=True)
    subprocess.run([sys.executable,'-m','research5.analyze'],check=True)
    print(f'[DONE] Results saved in {ROOT}. Independent replay/production/archive checks are still required.',flush=True)

if __name__=='__main__':main()
