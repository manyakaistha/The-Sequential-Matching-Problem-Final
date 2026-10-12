"""Registered benchmarks through unchanged evaluate.episode and strict JSON.

Trace files contain public assignment snapshots plus completed offline audit events.
Latent simulator members are never handed to a policy. Resume uses exact job keys.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evaluate
from kit import Simulator, VERSION, generate
from policy import decide as baseline
from research_policy import decide as prior


def percentile(values, q):
    xs = sorted(values)
    if not xs:
        return 0.
    p = (len(xs)-1)*q
    i = int(p)
    return xs[i] + (xs[min(i+1,len(xs)-1)]-xs[i])*(p-i)


def run(job):
    name, variant, seed, execution, trace_dir, custom_config = job
    from extended_policy import decide
    from research.extended_candidates import CANDIDATES
    cfg = custom_config if custom_config is not None else CANDIDATES.get(name,{})
    legacy = name in ('greedy', 'random', 'no_asks', 'prior_product', 'prior_full')
    command = ([sys.executable, 'policy.py', '--baseline', name] if name in ('greedy','random','no_asks')
               else [sys.executable, 'research_policy.py', '--config', json.dumps({'fusion':'product'} if name=='prior_product' else {})]
               if name.startswith('prior_') else [sys.executable, 'extended_policy.py', '--config', json.dumps(cfg)])
    if execution.startswith('container:'):
        command = evaluate.docker_command(execution.split(':',1)[1])
        if not legacy:
            command += ['--config', json.dumps(cfg)]
    latencies = []
    sizes = {'memory':0,'request':0,'response':0}
    snapshots, actions, sims = [], [], []
    original = evaluate.invoke

    class RecordingSimulator(Simulator):
        def __init__(self, world):
            super().__init__(world)
            sims.append(self)

    def invoke(cmd, request, timeout=10):
        raw = json.dumps(request, allow_nan=False)
        sizes['request'] = max(sizes['request'], len(raw.encode()))
        if len(raw.encode()) > evaluate.LIMIT:
            raise ValueError('request size')
        if execution != 'in_process_json':
            response, elapsed = original(cmd, request, timeout)
        else:
            start = time.perf_counter()
            req = evaluate.strict_json(raw)
            response = (baseline(req,name) if name in ('greedy','random','no_asks')
                        else prior(req,{'fusion':'product'} if name=='prior_product' else {})
                        if name.startswith('prior_') else decide(req,cfg))
            response = evaluate.validate_response(evaluate.strict_json(json.dumps(response,allow_nan=False)),request['phase'])
            elapsed = time.perf_counter()-start
        latencies.append(elapsed)
        for key in ('memory','response'):
            size = len(json.dumps(response['memory'] if key=='memory' else response,allow_nan=False).encode())
            sizes[key] = max(sizes[key],size)
            if size >= evaluate.LIMIT:
                raise ValueError(key+' size must be strictly below 1MiB')
        if elapsed > timeout:
            raise ValueError('invocation exceeded timeout in fast mode')
        phase, state = request['phase'], request['state']
        act = response['asks' if phase=='ask' else 'pairs']
        actions.append([phase,state['day'],act])
        if trace_dir and phase=='match':
            by_id = {m['member_id']:m for m in state['members']}
            for u,v in act:
                snap = dict(user_a=u,user_b=v,assigned_day=state['day'],
                            member_a=by_id[u],member_b=by_id[v],
                            prior_introductions=len(state['introductions']),
                            prior_feedback=len(state['feedback']))
                if not legacy:
                    from research.terminal_model import predict_funnel
                    snap['prediction'] = predict_funnel(by_id[u],by_id[v],state,response['memory'],cfg)
                snapshots.append(snap)
        return response,elapsed

    evaluate.invoke = invoke
    started = time.perf_counter()
    try:
        row = evaluate.episode(generate(seed,200,'evaluation',variant),command,simulator_class=RecordingSimulator)
        row.update(mutual_acceptance_rate=row['mutual_acceptances']/max(1,row['assignments']),
                   date_completion_rate=row['dates']/max(1,row['mutual_acceptances']))
    except Exception as error:
        row = dict(valid=False,error=type(error).__name__+': '+str(error),failure_count=1)
    finally:
        evaluate.invoke = original
    row.update(policy=name,variant=variant,seed=seed,execution=execution,configuration=cfg,
               failure_count=row.get('failure_count',0),wall_seconds=time.perf_counter()-started,
               peak_memory_bytes=sizes['memory'],peak_request_bytes=sizes['request'],
               peak_response_bytes=sizes['response'],mean_inference_ms=1000*sum(latencies)/len(latencies) if latencies else 0,
               latency_p95_seconds=percentile(latencies,.95),latency_p99_seconds=percentile(latencies,.99),
               peak_latency_seconds=max(latencies,default=0),invocation_count=len(latencies))
    if trace_dir:
        target=Path(trace_dir);target.mkdir(parents=True,exist_ok=True)
        canonical = [[p,d,sorted([sorted(a) if p=='match' else a for a in acts],key=lambda a:json.dumps(a,sort_keys=True))]
                     for p,d,acts in actions]
        sim = sims[0] if sims else None
        trace = dict(policy=name,variant=variant,seed=seed,execution=execution,configuration=cfg,
                     assignment_snapshots=snapshots,actions=actions,
                     semantic_action_sha256=hashlib.sha256(json.dumps(canonical,sort_keys=True).encode()).hexdigest(),
                     introductions=sim.introductions if sim else [],
                     completed_feedback=sim.receive_feedback() if sim else [],
                     final_public_members=sim.observe()['members'] if sim else [],
                     audit_boundary='Only completed events and public fields; no latent world members serialized.')
        file=target/(name+'_'+variant+'_'+str(seed)+'.json')
        file.write_text(json.dumps(trace,allow_nan=False)+'\n')
        row.update(trace=str(file),semantic_action_sha256=trace['semantic_action_sha256'])
    return row


def seed_range(text):
    if ':' in text:
        lo,hi=map(int,text.split(':'));return list(range(lo,hi+1))
    return [int(s) for s in text.split(',')]


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--policies',required=True);p.add_argument('--seeds',required=True)
    p.add_argument('--variants',default='all');p.add_argument('--output',required=True)
    p.add_argument('--execution',default='in_process_json');p.add_argument('--traces')
    p.add_argument('--workers',type=int,default=2);p.add_argument('--resume',action='store_true')
    p.add_argument('--config',help='JSON config used for every nonlegacy named policy')
    args=p.parse_args()
    from research.extended_candidates import CANDIDATES
    code_hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in
                 [Path('extended_policy.py'),Path('research/terminal_model.py'),
                  Path('research/extended_candidates.py'),Path('research_policy.py'),Path('kit.py'),Path('evaluate.py')]}
    variants=evaluate.VARIANTS if args.variants=='all' else args.variants.split(',')
    jobs=[(n,v,s,args.execution,args.traces,json.loads(args.config) if args.config else None)
          for s in seed_range(args.seeds) for v in variants for n in args.policies.split(',')]
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
    existing=json.loads(target.read_text()) if args.resume and target.exists() else None
    if existing is not None and existing.get('code_hashes') != code_hashes:
        raise ValueError('Resume requires identical recorded code hashes')
    rows=existing['episodes'] if existing else []
    for row in rows:
        cfg=json.loads(args.config) if args.config else CANDIDATES.get(row['policy'],{})
        if row['configuration'] != cfg:
            raise ValueError('Resume configuration mismatch')
    done={(r['policy'],r['variant'],r['seed'],r['execution']) for r in rows}
    todo=[j for j in jobs if tuple(j[:4]) not in done]
    def save():
        rows.sort(key=lambda r:(r['seed'],r['variant'],r['policy']))
        tmp=target.with_suffix('.tmp')
        tmp.write_text(json.dumps(dict(episodes=rows,complete=len(rows)==len(jobs),planned_episodes=len(jobs),
                                       code_hashes=code_hashes,
                                       summaries={n:evaluate.summarise([r for r in rows if r['policy']==n])
                                                  for n in args.policies.split(',')} if len(rows)==len(jobs) else None),indent=2,allow_nan=False)+'\n')
        tmp.replace(target)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(run,j) for j in todo]
        for future in as_completed(futures):
            row=future.result();rows.append(row);save()
            print(row['policy'],row['variant'],row['seed'],row.get('msmi_per_100_arrived_members'),row['valid'],flush=True)
    save()


if __name__=='__main__':
    main()
