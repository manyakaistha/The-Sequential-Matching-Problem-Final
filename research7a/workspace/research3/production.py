"""Restricted image replay and resource audit on already examined seed101.
No research data/audit artifacts are copied to the image. No inference network.
"""
import argparse,hashlib,json,platform,subprocess,sys,time,tempfile,shutil,contextlib,io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import evaluate
from kit import generate
from research3.policy import decide,CANDIDATES
from research3 import policy as policy_module

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def captured_invoke(command,request,timeout=10):
    """Same bounded file-backed child protocol, with retained stderr diagnostics."""
    raw=json.dumps(request,allow_nan=False).encode()
    if len(raw)>evaluate.LIMIT:raise ValueError('oversized request')
    started=time.perf_counter()
    with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
        proc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=out,stderr=err)
        try:proc.communicate(raw,timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill();proc.communicate()
            if command[:2]==['docker','run'] and '--name' in command:
                subprocess.run(['docker','rm','-f',command[command.index('--name')+1]],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5)
            raise ValueError('child exceeded invocation deadline')
        if out.tell()>evaluate.LIMIT or err.tell()>evaluate.LIMIT:raise ValueError('child output exceeds limit')
        out.seek(0);err.seek(0);stderr=err.read().decode(errors='replace')
        if proc.returncode:raise ValueError('child failed: '+stderr[:2048])
        response=evaluate.validate_response(evaluate.strict_json(out.read().decode()),request['phase'])
    return response,time.perf_counter()-started,stderr

def run(candidate,execution,image):
    original=evaluate.invoke;calls=[];actions=[];initial_fallbacks=policy_module.FALLBACK_COUNT
    def invoke(command,request,timeout=10):
        if execution=='direct':
            raw=json.dumps(request);start=time.perf_counter()
            with contextlib.redirect_stderr(io.StringIO()) as captured:
                response=decide(json.loads(raw),CANDIDATES[candidate])
            stderr=captured.getvalue();evaluate.validate_response(response,request['phase']);elapsed=time.perf_counter()-start
        else:response,elapsed,stderr=captured_invoke(command,request,timeout)
        key='asks' if request['phase']=='ask' else 'pairs'
        actions.append([request['phase'],request['state']['day'],response[key]])
        calls.append(dict(stderr=stderr,fallback_warning_count=stderr.count('round3 fallback:'),seconds=elapsed,request_bytes=len(json.dumps(request).encode()),memory_bytes=len(json.dumps(response['memory']).encode()),response_bytes=len(json.dumps(response).encode())))
        return response,elapsed
    evaluate.invoke=invoke
    command=evaluate.docker_command(image)+['--candidate',candidate] if execution=='container' else [sys.executable,'-m','research3.policy','--candidate',candidate]
    try:
        row=evaluate.episode(generate(101,200,'evaluation','development'),command)
    except Exception as e:row=dict(valid=False,error=type(e).__name__+': '+str(e))
    finally:evaluate.invoke=original
    semantic=[[phase,day,sorted([sorted(p) if phase=='match' else p for p in acts],key=lambda p:json.dumps(p,sort_keys=True))] for phase,day,acts in actions]
    row.update(optimized_fallback_count=policy_module.FALLBACK_COUNT-initial_fallbacks if execution=='direct' else None,captured_fallback_warning_count=sum(c['fallback_warning_count'] for c in calls),execution=execution,seed=101,variant='development',candidate=candidate,calls=calls,semantic_action_sha256=hashlib.sha256(json.dumps(semantic,sort_keys=True).encode()).hexdigest(),command=command)
    return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',default='greedy',choices=CANDIDATES);p.add_argument('--output',required=True);p.add_argument('--image',default='sequential-round3:research');p.add_argument('--skip-build',action='store_true');a=p.parse_args()
    target=Path(a.output)
    if target.exists():raise ValueError('refuse overwrite')
    started=time.monotonic();build_command=['docker','build','-f','research3/Dockerfile','-t',a.image,'.']
    build=None
    if not a.skip_build:
        with tempfile.TemporaryDirectory(prefix='round3-image-') as directory:
            context=Path(directory)
            for name in ('kit.py','research/terminal_model.py','research3/__init__.py','research3/policy.py','research3/model_candidates.py'):
                dest=context/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,dest)
            shutil.copyfile('research3/Dockerfile',context/'Dockerfile')
            build_command=['docker','build','-t',a.image,str(context)]
            b=subprocess.run(build_command,capture_output=True,text=True,timeout=180)
        build=dict(returncode=b.returncode,stdout=b.stdout,stderr=b.stderr,command=build_command)
        if b.returncode:target.write_text(json.dumps(dict(build=build,valid=False),indent=2)+'\n');return
    metadata=json.loads(subprocess.check_output(['docker','image','inspect',a.image],text=True))[0]
    rows=[]
    for mode in ('direct','subprocess','container'):
        rows.append(run(a.candidate,mode,a.image));print(mode,rows[-1].get('valid'),rows[-1].get('action_sha256'),flush=True)
    fields=('assignments','mutual_acceptances','dates','mutual_second_meeting_intention','coverage','ask_cost','action_sha256','semantic_action_sha256')
    equivalence={f:all(r.get(f)==rows[0].get(f) for r in rows) for f in fields}
    # Inspect the actual command's configured enforced resource options.
    out=dict(scope='Finite complete seed101 replay, not universal latency guarantee',build=build,image=dict(id=metadata['Id'],size_bytes=metadata['Size'],below_documented_2GiB=metadata['Size']<=2*1024**3,user=metadata['Config']['User'],entrypoint=metadata['Config']['Entrypoint']),resource_command=evaluate.docker_command(a.image),rows=rows,equivalence=equivalence,valid=all(r.get('valid') for r in rows) and all(equivalence.values()) and metadata['Size']<=2*1024**3,wall_seconds=time.monotonic()-started,source_hashes={q:digest(q) for q in ('kit.py','evaluate.py','research/terminal_model.py','research3/policy.py','research3/model_candidates.py','research3/Dockerfile','research3/production.py')},python=platform.python_version(),command=sys.argv)
    target.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(valid=out['valid'],equivalence=equivalence,image=out['image'],wall_seconds=out['wall_seconds']),indent=2))
if __name__=='__main__':main()
