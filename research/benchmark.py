"""Reproducible benchmark. All rollouts call evaluate.episode; fast mode replaces
only evaluate.invoke with the same strict JSON boundary in the current process.
Use --subprocess for official startup/timeout measurements. Two worker processes.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import evaluate
from kit import generate
from policy import decide as baseline
from research_policy import decide

CONFIGS={
 'full':{}, 'greedy_engine':{'engine':'greedy'}, 'hungarian':{'engine':'hungarian'},
 'fifo':{'asks':'fifo'}, 'soft_only':{'asks':'soft'}, 'no_active_asks':{'asks':'none'},
 'static':{'threshold':'static'}, 'zero':{'threshold':'zero'},
 'product':{'fusion':'product'}, 'unilateral':{'fusion':'unilateral'},
 'no_learning':{'learning':False}, 'no_dfm':{'dfm':False},
 'batch3':{'epoch':3},'batch5':{'epoch':5},'batch7':{'epoch':7},
 'hard15':{'hard_days':15},
 'hazard':{'threshold':'hazard'},
}

def run(job):
    name,variant,seed,subprocess=job
    command=[sys.executable,'policy.py','--baseline',name] if name in ('greedy','random','no_asks') else [sys.executable,'research_policy.py','--config',json.dumps(CONFIGS[name])]
    peak_memory=peak_request=peak_latency=0
    real_invoke=evaluate.invoke
    def invoke(command,request,timeout=10):
        nonlocal peak_memory,peak_request,peak_latency
        raw=json.dumps(request,allow_nan=False);peak_request=max(peak_request,len(raw.encode()))
        if len(raw.encode())>evaluate.LIMIT: raise ValueError('request size')
        if subprocess:
            response,elapsed=real_invoke(command,request,timeout)
        else:
            start=time.perf_counter()
            req=evaluate.strict_json(raw)
            response=baseline(req,name) if name in ('greedy','random','no_asks') else decide(req,CONFIGS[name])
            response=evaluate.validate_response(evaluate.strict_json(json.dumps(response,allow_nan=False)),request['phase'])
            elapsed=time.perf_counter()-start
        peak_memory=max(peak_memory,len(json.dumps(response['memory']).encode()))
        peak_latency=max(peak_latency,elapsed)
        return response,elapsed
    evaluate.invoke=invoke
    try:
        row=evaluate.episode(generate(seed,200,'evaluation',variant),command)
        row.update(policy=name,variant=variant,seed=seed,execution='subprocess' if subprocess else 'in_process_json',
                   peak_memory_bytes=peak_memory,peak_request_bytes=peak_request,peak_latency_seconds=peak_latency,
                   mean_inference_ms=1000*row['inference_seconds']/120,
                   mutual_acceptance_rate=row['mutual_acceptances']/max(1,row['assignments']),
                   date_completion_rate=row['dates']/max(1,row['mutual_acceptances']))
        return row
    finally: evaluate.invoke=real_invoke

def main():
    p=argparse.ArgumentParser();p.add_argument('--policies',default=','.join(['greedy','no_asks','random']+[name for name in CONFIGS if name!='hazard']))
    p.add_argument('--seeds',default='101,102,103,104,105');p.add_argument('--variants',default='all');p.add_argument('--subprocess',action='store_true')
    p.add_argument('--output',default='results/research/benchmark.json');p.add_argument('--workers',type=int,default=2);args=p.parse_args()
    variants=evaluate.VARIANTS if args.variants=='all' else args.variants.split(',')
    jobs=[(n,v,int(s),args.subprocess) for n in args.policies.split(',') for v in variants for s in args.seeds.split(',')]
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True);rows=[]
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for row in executor.map(run,jobs):
            rows.append(row)
            target.write_text(json.dumps({'episodes':rows,'complete':len(rows)==len(jobs),'planned_episodes':len(jobs)},indent=2)+'\n')
            print(row['policy'],row['variant'],row['seed'],row['msmi_per_100_arrived_members'],flush=True)
if __name__=='__main__':main()
