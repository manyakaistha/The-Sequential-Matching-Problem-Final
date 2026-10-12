"""Fail-closed registered grids; max three workers and durable resume."""
import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import sys
import time

from research6.recorder import run_cell, sha, write_new

SOURCE_PATHS = ('kit.py','evaluate.py','research6/recorder.py','research6/orchestrator.py',
                'research6/policies/policy.py','research6/policies/allocation.py',
                'research4/policy.py','research4/candidates.py','research3/policy.py',
                'research3/model_candidates.py','research/terminal_model.py')


def sources():
    return {p:sha(p) for p in SOURCE_PATHS}


def log(root, event):
    record = {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), **event}
    print(record.get('message',json.dumps(record)), flush=True)
    with (root/'events.jsonl').open('a') as stream:
        stream.write(json.dumps(record,allow_nan=False)+'\n')
        stream.flush()
        os.fsync(stream.fileno())


def load_design(path):
    design = json.loads(Path(path).read_text())
    required = ('cells','configs','sources','stage','resource_forecast','reviews','seed_inventory_sha256')
    if any(k not in design for k in required):
        raise ValueError('incomplete registration')
    if design['sources'] != sources():
        raise ValueError('source changed after registration')
    cells = design['cells']
    identities = [(c['policy'],c['seed'],c['family']) for c in cells]
    if len(identities) != len(set(identities)) or not cells:
        raise ValueError('empty/duplicate grid')
    if any(set(c) != {'policy','seed','family'} or c['policy'] not in design['configs'] for c in cells):
        raise ValueError('invalid cell/config')
    if any(design['configs'][c['policy']].get('id') != c['policy'] for c in cells):
        raise ValueError('candidate label/config id mismatch')
    import evaluate
    if any(c['family'] not in evaluate.VARIANTS for c in cells):
        raise ValueError('invalid scenario')
    if design['stage'] not in ('smoke','A','training','validation','B','C','D','E','replay'):
        raise ValueError('invalid stage')
    if not design['reviews'] or not all(r['passed'] for r in design['reviews']):
        raise ValueError('unclosed reviews')
    for review in design['reviews']:
        if sha(review['path']) != review['sha256']:
            raise ValueError('review bytes changed')
    if sha('research6/audits/seed_inventory.json') != design['seed_inventory_sha256']:
        raise ValueError('seed inventory changed')
    budget = design['resource_forecast']
    if budget['main_cpu_seconds'] > 40*3600 or budget['fit_cpu_seconds'] > 10*3600:
        raise ValueError('budget ceiling exceeded')
    return design


def verify_commit(row, expected_sources, expected_config=None):
    if expected_config is not None and row['config'] != expected_config:
        raise ValueError('committed config mismatch')
    if row['source_hashes'] != expected_sources:
        raise ValueError('committed sources mismatch')
    path = Path(row['attempt_path'])
    for name, expected in row['files'].items():
        artifact = path / name
        if artifact.stat().st_size != expected['bytes'] or sha(artifact) != expected['sha256']:
            raise ValueError('committed evidence corrupt: '+str(artifact))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--workers',type=int,default=3)
    args = parser.parse_args()
    if not 1 <= args.workers <= 3:
        parser.error('worker limit 1–3')
    for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[name] = '1'
    print('[preflight] checking immutable registration and sources',flush=True)
    design = load_design(args.design)
    root = Path(args.output)
    root.mkdir(parents=True,exist_ok=True)
    design_sha = sha(args.design)
    registration = root/'registration.json'
    if registration.exists():
        if sha(registration) != design_sha:
            raise ValueError('resume design mismatch')
    else:
        with registration.open('xb') as out:
            out.write(Path(args.design).read_bytes()); out.flush(); os.fsync(out.fileno())
    reserve = 20*1024**3
    required = design['resource_forecast']['storage_bytes_with_headroom'] + reserve
    if shutil.disk_usage(root).free < required:
        raise ValueError('complete-stage storage forecast plus reserve unavailable')
    environment = root/'environment.json'
    if not environment.exists():
        import importlib.metadata
        versions = {}
        for package in ('numpy','scipy','networkx'):
            versions[package] = importlib.metadata.version(package)
        write_new(environment, {'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
                  'versions':versions,'command':sys.argv,'environment_threads':{k:os.environ[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}})
    commits = root/'commits'
    commits.mkdir(exist_ok=True)
    rows = {}
    allowed = {(c['policy'],c['seed'],c['family']) for c in design['cells']}
    for path in commits.glob('*.json'):
        row = json.loads(path.read_text()); key = row['policy'],row['seed'],row['family']
        if key not in allowed or key in rows:
            raise ValueError('foreign/duplicate commit')
        verify_commit(row,design['sources'],design['configs'][row['policy']]); rows[key] = row
    pending = [c for c in design['cells'] if (c['policy'],c['seed'],c['family']) not in rows]
    log(root,{'kind':'startup','message':f"[logs] {root}/attempts | commits {len(rows)}/{len(allowed)} | workers {args.workers} | stage {design['stage']}"})
    stopping = False
    def stop(signum, frame):
        nonlocal stopping
        stopping = True
        log(root,{'kind':'interruption','signal':signum,'message':'[interrupt] preserving attempts; draining active cells; resume original registration'})
    previous = signal.signal(signal.SIGINT,stop)
    started = time.monotonic()
    cpu_before = os.times()
    queue = iter(pending)
    futures = {}
    try:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            def submit():
                if stopping: return
                cell = next(queue,None)
                if cell is not None:
                    future = pool.submit(run_cell,(str(root),cell,design['configs'][cell['policy']],design['sources']))
                    futures[future] = cell
                    log(root,{'kind':'worker_start','cell':cell,'message':f'[worker] starting {cell}'})
            for _ in range(args.workers): submit()
            while futures:
                completed,_ = wait(futures,timeout=10,return_when=FIRST_COMPLETED)
                for future in completed:
                    cell = futures.pop(future)
                    try:
                        row = future.result(); verify_commit(row,design['sources'],design['configs'][row['policy']])
                        rows[(row['policy'],row['seed'],row['family'])] = row
                        log(root,{'kind':'commit','cell':cell,'valid':row['valid'],'attempt_id':row['attempt_id']})
                    except BaseException as error:
                        stopping = True
                        log(root,{'kind':'worker_failure','cell':cell,'error':repr(error),'message':f'[failure] {cell}: {error}; preserve and stop scheduling'})
                    submit()
                elapsed = time.monotonic()-started
                count,total = len(rows),len(allowed)
                completed_here = count-(total-len(pending))
                eta = elapsed*(total-count)/completed_here if completed_here else None
                bar = '#'*int(28*count/total)+'.'*(28-int(28*count/total))
                log(root,{'kind':'heartbeat','committed':count,'planned':total,'active':list(futures.values()),
                    'elapsed_seconds':elapsed,'eta_seconds':eta,'message':f'[progress] [{bar}] {count}/{total} elapsed {elapsed:.1f}s | active {len(futures)} | durable logs confirmed'})
                actual_cpu = sum(r['cpu_seconds'] for r in rows.values())
                if actual_cpu > design['resource_forecast']['main_cpu_seconds'] or shutil.disk_usage(root).free < reserve:
                    stopping = True
                    log(root,{'kind':'resource_stop','cpu_seconds':actual_cpu,'message':'[resource] registration ceiling/reserve reached; incomplete grid preserved'})
    finally:
        signal.signal(signal.SIGINT,previous)
    cpu_after = os.times()
    summary = {'stage':design['stage'],'registration_sha256':design_sha,'complete':len(rows)==len(allowed),
          'planned':len(allowed),'committed':len(rows),'invalid':sum(not r['valid'] for r in rows.values()),
          'fallbacks':sum(r['fallback_count'] for r in rows.values()),'wall_seconds':time.monotonic()-started,
          'child_cpu_seconds_this_launch':cpu_after.children_user+cpu_after.children_system-cpu_before.children_user-cpu_before.children_system,
          'episode_cpu_seconds':sum(r['cpu_seconds'] for r in rows.values()),
          'storage_bytes':sum(p.stat().st_size for p in root.rglob('*') if p.is_file()),
          'attempts':len(list((root/'attempts').glob('*/*/started.json'))),
          'remaining':len(allowed)-len(rows),'stopped':stopping}
    destination = root / ('summary-'+str(time.time_ns())+'.json')
    write_new(destination,summary)
    log(root,{'kind':'finished','message':f'[done] {destination} | complete={summary["complete"]} invalid={summary["invalid"]}'})
    return 0 if summary['complete'] and not summary['invalid'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
