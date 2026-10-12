"""Independent process/container protocol verification for a frozen configuration."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evaluate import docker_command, invoke
from kit import Simulator, VERSION, generate


def limits(image):
    cmd=docker_command(image)
    cmd[cmd.index(image):cmd.index(image)]=['--entrypoint','python']
    code='''import json, pathlib, os
out={}
for n in ('cpu.max','memory.max','pids.max'):
 out[n]=(pathlib.Path('/sys/fs/cgroup')/n).read_text().strip()
try:
 pathlib.Path('/write_probe').write_text('x');out['root_write_blocked']=False
except OSError as e:
 out['root_write_blocked']=True;out['write_errno']=e.errno
out['uid']=os.getuid()
out['up_interfaces']=[p.name for p in pathlib.Path('/sys/class/net').iterdir() if p.is_dir() and int((p/'flags').read_text(),16)&1]
out['app_files']=[str(p.relative_to('/app')) for p in pathlib.Path('/app').rglob('*') if p.is_file()]
print(json.dumps(out))
'''
    r=subprocess.run(cmd+['-c',code],capture_output=True,text=True,timeout=10)
    if r.returncode:raise ValueError(r.stderr)
    out=json.loads(r.stdout)
    q,p=map(int,out['cpu.max'].split())
    assert q/p==2 and out['memory.max']=='1073741824' and out['pids.max']=='64'
    assert out['root_write_blocked'] and out['uid']==65534 and out['up_interfaces']==['lo']
    info=json.loads(subprocess.check_output(['docker','image','inspect',image]))[0]
    out.update(image_id=info['Id'],image_size_bytes=info['Size'],command=docker_command(image))
    assert info['Size']<=2*1024**3
    versions=subprocess.check_output(cmd+['-c','import sys,networkx,json; print(json.dumps(dict(python=sys.version,networkx=networkx.__version__)))'],text=True,timeout=10)
    out['package_versions']=json.loads(versions)
    return out


def canonical(phase,actions):
    return sorted([sorted(a) if phase=='match' else a for a in actions],key=lambda a:json.dumps(a,sort_keys=True))


def replay(cfg,image,seed,variant):
    from extended_policy import decide
    world=generate(seed,200,'evaluation',variant)
    sims=[Simulator(world) for _ in range(3)];memories=[None]*3
    times=[[] for _ in sims];raw_diff=[];semantic_diff=[];peakmem=[0]*3;peakreq=[0]*3
    digests=[hashlib.sha256() for _ in sims]
    for day in range(60):
        for phase in ('ask','match'):
            acts=[]
            for i,sim in enumerate(sims):
                req=dict(schema_version=VERSION,phase=phase,state=sim.observe(),memory=memories[i])
                raw=json.dumps(req,allow_nan=False);peakreq[i]=max(peakreq[i],len(raw.encode()))
                if i==0:
                    import time
                    from evaluate import strict_json,validate_response
                    t=time.perf_counter();r=validate_response(strict_json(json.dumps(decide(strict_json(raw),cfg),allow_nan=False)),phase);elapsed=time.perf_counter()-t
                else:
                    command=[sys.executable,'extended_policy.py','--config',json.dumps(cfg)] if i==1 else docker_command(image)+['--config',json.dumps(cfg)]
                    r,elapsed=invoke(command,req)
                times[i].append(elapsed);memories[i]=r['memory'];peakmem[i]=max(peakmem[i],len(json.dumps(r['memory']).encode()))
                action=r['asks' if phase=='ask' else 'pairs'];acts.append(action)
                digests[i].update(json.dumps([phase,day,action],sort_keys=True).encode())
            for i in (1,2):
                if acts[i]!=acts[0]:
                    record=dict(day=day,phase=phase,execution=i,host=acts[0],other=acts[i])
                    if canonical(phase,acts[i])==canonical(phase,acts[0]):raw_diff.append(record)
                    else:semantic_diff.append(record)
            for i,sim in enumerate(sims):
                if phase=='ask':sim.resolve_asks(acts[i])
                else:sim.advance(acts[i])
    for sim in sims:
        for _ in range(40):sim.advance([])
    out=dict(seed=seed,variant=variant,configuration=cfg,execution_order=['in_process','subprocess','container'],
             ordering_only_differences=raw_diff,semantic_differences=semantic_diff,
             action_sha256=[d.hexdigest() for d in digests],metrics=[s.metrics() for s in sims],
             total_inference_seconds=[sum(t) for t in times],max_call_seconds=[max(t) for t in times],
             peak_memory_bytes=peakmem,peak_request_bytes=peakreq)
    assert not semantic_diff and out['metrics'][0]==out['metrics'][1]==out['metrics'][2]
    assert max(peakmem)<1024**2 and max(peakreq)<=1024**2 and max(out['max_call_seconds'])<10
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--image',default='sequential-extended:1.0')
    p.add_argument('--config',required=True);p.add_argument('--seed',type=int,default=1001)
    p.add_argument('--variant',default='development');p.add_argument('--output',default='results/extended/production.json')
    args=p.parse_args();cfg=json.loads(args.config)
    out=dict(limits=limits(args.image),replay=replay(cfg,args.image,args.seed,args.variant))
    Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(semantic_differences=len(out['replay']['semantic_differences']),max_call_seconds=out['replay']['max_call_seconds'])))

if __name__=='__main__':main()
