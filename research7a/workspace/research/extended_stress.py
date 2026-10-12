"""Independent observation-only stress harness; does not alter frozen policy code.

These are explicitly constructed public observations, not sampled simulator episodes
and not held-out performance data. Diverse valid actor posteriors challenge caches.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time

from kit import HARD,SOFT,VERSION
from evaluate import validate_response


def request(n=200,diverse=True,incomplete=0):
    members=[];users={}
    for index in range(n):
        ident='stress_%04d'%index
        fields=dict(age_min=18,age_max=65,who_to_meet=['woman','man','non_binary'],
                    relationship_structure='monogamous',smoking='no',partner_smoking='any',
                    has_children=False,partner_children='any',wants_children='unsure',
                    acceptable_zones=['zone_a'],schedule=['weekend_day'])
        fields.update({k:None for k in SOFT})
        if index<incomplete: fields['age_min']=None
        members.append(dict(member_id=ident,pool_id='constructed_stress',synthetic=True,
                            age=30,gender='woman' if index%2 else 'man',zone='zone_a',
                            arrived_day=0,available=True,fields=fields,
                            field_status={k:'observed' if v is not None else 'not_asked' for k,v in fields.items()},
                            field_observed_day={k:0 if v is not None else None for k,v in fields.items()},
                            source='constructed_observation_only'))
        if diverse:
            users[ident]=[5.+index%9,3.+index%7,-2.5+5*index/max(1,n-1),
                          2.1+index*.071,2.3-4.6*((index*37)%n)/max(1,n-1),4.+index*.037]
    return dict(schema_version=VERSION,phase='match',
                state=dict(schema_version=VERSION,synthetic=True,day=30,ask_budget_remaining=12,
                           members=members,introductions=[],feedback=[],ask_log=[]),
                memory=dict(version=2,users=users,snapshots={},seen=[],regime_seen=[],
                            regime_logweights=[0.,0.,0.],date_counts=[7.8,2.2],
                            date_lags=[0.,0.],date_logweights=[1.6094379124341003,0.]))


def run(name,req,cfg,timeout=10):
    raw=json.dumps(req,allow_nan=False).encode()
    rss=[];stop=threading.Event()
    started=time.perf_counter()
    with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
        proc=subprocess.Popen([sys.executable,'extended_policy.py','--config',json.dumps(cfg)],
                              stdin=subprocess.PIPE,stdout=out,stderr=err)
        def monitor():
            while not stop.is_set():
                try:
                    value=subprocess.run(['ps','-o','rss=','-p',str(proc.pid)],capture_output=True,text=True,timeout=.5)
                    if value.stdout.strip(): rss.append(int(value.stdout.strip())*1024)
                except (ValueError,subprocess.TimeoutExpired,OSError): pass
                stop.wait(.05)
        thread=threading.Thread(target=monitor,daemon=True);thread.start()
        timed_out=False
        try: proc.communicate(raw,timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out=True;proc.kill();proc.communicate()
        stop.set();thread.join(timeout=1)
        elapsed=time.perf_counter()-started
        out.seek(0);output=out.read(1024*1024+1);err.seek(0);stderr=err.read(2048).decode(errors='replace')
    row=dict(case=name,configuration=cfg,phase=req['phase'],members=len(req['state']['members']),
             diverse_actors=len(req.get('memory',{}).get('users',{})) if isinstance(req.get('memory'),dict) and isinstance(req.get('memory',{}).get('users',{}),dict) else None,
             timeout_seconds=timeout,timed_out=timed_out,exit_code=proc.returncode,wall_seconds=elapsed,
             peak_sampled_rss_bytes=max(rss,default=0),rss_sampling_interval_seconds=.05,
             request_bytes=len(raw),output_bytes=len(output),stderr=stderr)
    if not timed_out and proc.returncode==0:
        try:
            response=json.loads(output);validate_response(response,req['phase']);row['valid_protocol']=True
            row['action_count']=len(response['asks' if req['phase']=='ask' else 'pairs'])
            row['memory_bytes']=len(json.dumps(response['memory']).encode())
            row['empty_memory_fallback']=response['memory']=={}
        except (ValueError,KeyError,TypeError) as error: row.update(valid_protocol=False,error=str(error))
    else: row['valid_protocol']=False
    print(json.dumps({k:row[k] for k in ('case','wall_seconds','timed_out','peak_sampled_rss_bytes','valid_protocol')}),flush=True)
    return row


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='results/extended/stress.json')
    args=parser.parse_args();rows=[]
    cases=[]
    base=request()
    cases.append(('dense200_diverse_default',base,{}))
    cases.append(('dense200_homogeneous_default',request(diverse=False),{}))
    for mode in ('value','two_query'):
        cases.append(('dense200_diverse_'+mode,copy.deepcopy(base),dict(asks=mode,engine='blossom')))
    for mode in ('value','two_query'):
        req=request(incomplete=10);req['phase']='ask'
        cases.append(('dense200_diverse_incomplete10_'+mode,req,dict(asks=mode,engine='blossom')))
    for field,value in [('users',[]),('snapshots',[]),('regime_logweights',['invalid']),('date_counts',[0.,0.])]:
        req=request(n=4);req['memory'][field]=value
        cases.append(('corrupt_memory_'+field,req,{}))
    req=request(n=4)
    for index in range(300): req['memory']['users']['unused_%04d'%index]=[1.,1.,0.,2.,0.,4.]
    cases.append(('extra300_actor_records',req,{}))
    req=request(n=4);req['memory']['padding']='x'*(1024*1024)
    cases.append(('oversized_memory_input',req,{}))
    target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True)
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in map(Path,['extended_policy.py','research/terminal_model.py','research/extended_candidates.py'])}
    for name,req,cfg in cases:
        rows.append(run(name,req,cfg))
        target.write_text(json.dumps(dict(constructed_observation_only=True,simulator_performance_data=False,
                                         code_hashes=hashes,complete=len(rows)==len(cases),cases=rows),indent=2)+'\n')


if __name__=='__main__': main()
