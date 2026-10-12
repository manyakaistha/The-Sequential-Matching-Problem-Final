"""Revalidate unchanged round4 inference without writing its sealed CLI ledger."""
import argparse,hashlib,json,platform,resource,shutil,subprocess,sys,tempfile,time,traceback
from datetime import datetime,timezone
from pathlib import Path
from research4 import production as inherited

ROOT=Path('results/research5')
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def audit_seal():
 manifest_path=Path('results/research4/manifest.json');m=json.loads(manifest_path.read_text());bad=[p for p,v in m['files'].items() if not Path(p).is_file() or sha(p)!=v['sha256']]
 if bad:raise ValueError('Sealed round4 bytes differ: '+str(bad[:10]))
 return dict(manifest_sha256=sha(manifest_path),files_checked=len(m['files']),all_bytes_match=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',default=str(ROOT/'production_selected.json'));p.add_argument('--image',default='sequential-round5:production-checks');p.add_argument('--skip-build',action='store_true');a=p.parse_args();target=Path(a.output)
 if target.exists():raise ValueError('refuse output overwrite')
 ROOT.mkdir(parents=True,exist_ok=True);start=time.monotonic();utc=datetime.now(timezone.utc).isoformat();cpu0=resource.getrusage(resource.RUSAGE_SELF);child0=resource.getrusage(resource.RUSAGE_CHILDREN)
 design=json.loads((ROOT/'design.json').read_text());out=dict(valid=False,prepare_only=False,scope='Finite complete previously examined seed101 development 60+40 replay; no fresh confirmation generation or universal timeout guarantee',candidate=design['candidate'],rows=[],source_hashes={},command=[sys.executable,'-m','research5.production_checks']+sys.argv[1:])
 try:
  expected={**design['frozen_inherited_hashes'],**design['initializer_hashes']}
  for path,digest in expected.items():
   if sha(path)!=digest:raise ValueError('Frozen hash mismatch: '+path)
  if inherited.CANDIDATES[design['candidate']]!=design['configuration']:raise ValueError('Selected configuration mismatch')
  out['sealed_round4_before']=audit_seal()
  out['build']=None
  if not a.skip_build:
   with tempfile.TemporaryDirectory(prefix='round5-production-') as directory:
    context=Path(directory)
    for name in inherited.SOURCES:
     dest=context/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,dest)
    shutil.copyfile('research4/Dockerfile',context/'Dockerfile')
    command=['docker','build','-t',a.image,str(context)];b=subprocess.run(command,capture_output=True,text=True,timeout=180)
   out['build']=dict(command=command,returncode=b.returncode,stdout=b.stdout,stderr=b.stderr)
   if b.returncode:raise ValueError('Docker build failed')
  metadata=json.loads(subprocess.check_output(['docker','image','inspect',a.image],text=True))[0]
  out['image']=dict(id=metadata['Id'],size_bytes=metadata['Size'],below_documented_2GiB=metadata['Size']<2*1024**3,user=metadata['Config']['User'],entrypoint=metadata['Config']['Entrypoint'])
  out['docker_version']=subprocess.check_output(['docker','version','--format','{{json .}}'],text=True)
  out['resource_probe']=inherited.probe(a.image)
  for mode in ('direct','subprocess','container'):
   row=inherited.run(design['candidate'],mode,a.image);out['rows'].append(row);print(mode,row.get('valid'),row.get('action_sha256'),flush=True)
  skip={'calls','execution','command','optimized_fallback_count','inference_seconds'}
  out['equivalence']={k:all(r.get(k)==out['rows'][0][k] for r in out['rows']) for k in out['rows'][0] if k not in skip}
  out['resource_command']=inherited.evaluate.docker_command(a.image)
  out['source_hashes']={name:sha(name) for name in tuple(expected)+('research4/production.py','research4/Dockerfile','research5/production_checks.py')}
  out['sealed_round4_after']=audit_seal()
  for path,digest in expected.items():
   if sha(path)!=digest:raise ValueError('Frozen hash changed during replay: '+path)
  valid_calls=all(r.get('valid') and len(r['calls'])==120 and r['captured_fallback_warning_count']==0 and (r['execution']!='direct' or r['optimized_fallback_count']==0) and all(c['seconds']<10 and c['memory_bytes']<1048576 and c['request_bytes']<=1048576 and c['fallback_warning_count']==0 for c in r['calls']) for r in out['rows'])
  out['valid']=len(out['rows'])==3 and valid_calls and all(out['equivalence'].values()) and out['resource_probe']['valid'] and out['image']['below_documented_2GiB'] and out['sealed_round4_before']==out['sealed_round4_after']
 except Exception as e:out['error']=type(e).__name__+': '+str(e);out['traceback']=traceback.format_exc();print(out['traceback'],flush=True)
 cpu1=resource.getrusage(resource.RUSAGE_SELF);child1=resource.getrusage(resource.RUSAGE_CHILDREN)
 out['python']=platform.python_version();out['wall_seconds']=time.monotonic()-start;out['compute']=dict(started_utc=utc,host_self_cpu_seconds=cpu1.ru_utime+cpu1.ru_stime-cpu0.ru_utime-cpu0.ru_stime,host_children_cpu_seconds=child1.ru_utime+child1.ru_stime-child0.ru_utime-child0.ru_stime,docker_daemon_build_container_cpu_seconds=None,note='Sequential modes, one host verification worker. Docker client CPU is included; daemon/build/container CPU unknown. Seal hashing is offline overhead.')
 target.write_text(json.dumps(out,indent=2)+'\n')
 with (ROOT/'production_commands.jsonl').open('a') as f:f.write(json.dumps(dict(command=out['command'],output=str(target),compute=out['compute'],wall_seconds=out['wall_seconds'],valid=out['valid']))+'\n')
 print(json.dumps(dict(valid=out['valid'],wall_seconds=out['wall_seconds'],compute=out['compute']),indent=2),flush=True)
 if not out['valid']:raise SystemExit(1)
if __name__=='__main__':main()
