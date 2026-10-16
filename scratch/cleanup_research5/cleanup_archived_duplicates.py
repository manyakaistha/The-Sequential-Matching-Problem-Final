"""Verify and remove only exact R5 archived duplicates, retaining all evidence archives."""
import argparse,concurrent.futures,datetime,hashlib,json,os,shutil,stat,subprocess,time
from pathlib import Path

INDEX_ANCHOR='7fce78beefa52c25cae8bcf2c6068bb796d146b35a55cc3bacafce8d509996e6'

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as stream:
  for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
 return h.hexdigest()

def write_new(path,data):
 with Path(path).open('x') as stream:
  json.dump(data,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())

def rooted(root,relative):
 p=Path(relative)
 if p.is_absolute() or '..' in p.parts or p.parts[:2]!=('results','research5'):raise ValueError('Unsafe member '+relative)
 absolute=root/p
 if absolute.resolve()!=absolute or not absolute.resolve().is_relative_to(root/'results/research5'):raise ValueError('Symlink or escaping member '+relative)
 if not stat.S_ISREG(absolute.lstat().st_mode):raise ValueError('Not regular '+relative)
 return absolute

def stable_record(root,entry,archive):
 p=rooted(root,entry['path']);before=p.stat();actual=sha(p);after=p.stat()
 if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns):raise ValueError('Changing source '+entry['path'])
 if actual!=entry['sha256'] or after.st_size!=entry['bytes']:raise ValueError('Source/index hash mismatch '+entry['path'])
 return dict(entry,archive=archive,st_dev=after.st_dev,st_ino=after.st_ino,st_mtime_ns=after.st_mtime_ns)

def verify(root,out):
 started=time.monotonic();cpu=time.process_time();index=root/'results/research5/archive_index.json';checks=root/'results/research5/archive_build_checks.json'
 if sha(index)!=INDEX_ANCHOR:raise ValueError('Historical index anchor changed')
 data=json.loads(index.read_text());old=json.loads(checks.read_text())
 if old.get('valid') is not True or old.get('index_sha256')!=INDEX_ANCHOR or old.get('verified_members')!=sum(len(a['members']) for a in data['archives']):raise ValueError('Exhaustive archive verification not anchored')
 tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0'));archives=[];work=[];seen=set()
 for archive in data['archives']:
  p=rooted(root,archive['path'])
  if p.stat().st_size!=archive['bytes'] or sha(p)!=archive['sha256']:raise ValueError('Archive bytes changed '+archive['path'])
  archives.append({k:archive[k] for k in ('path','bytes','sha256')})
  for entry in archive['members']:
   if entry['path'] in seen or entry['path'] in tracked or entry['path'] in {a['path'] for a in data['archives']}:raise ValueError('Duplicate/protected indexed path')
   seen.add(entry['path']);work.append((entry,archive['path']))
 rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(stable_record,root,e,a) for e,a in work]
  for i,future in enumerate(futures,1):
   rows.append(future.result())
   if i%500==0:print(json.dumps({'verified_files':i,'planned':len(work)}),flush=True)
 report={'status':'verified_exact_archived_duplicates','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':str(root),'script_sha256':sha(__file__),'index_sha256':INDEX_ANCHOR,'archive_build_checks_sha256':sha(checks),'historical_exhaustive_verified_members':old['verified_members'],'archives_retained':archives,'files':rows,'removable_files':len(rows),'removable_logical_bytes':sum(r['bytes'] for r in rows),'free_disk_bytes_before':shutil.disk_usage(root).free,'verification_cpu_seconds':time.process_time()-cpu,'verification_wall_seconds':time.monotonic()-started,'preserved':'All archives, indexes, reports, summaries, source/data/configs and every unindexed/changed file; only exact indexed untracked extracted copies eligible','restore_command':'python3 research5/archive_results.py restore --destination .'}
 write_new(out/'verified_manifest.json',report);print(json.dumps({k:report[k] for k in ('status','removable_files','removable_logical_bytes','verification_wall_seconds')},indent=2),flush=True)

def remove(root,out,review):
 manifest=out/'verified_manifest.json';data=json.loads(manifest.read_text());approval=json.loads(Path(review).read_text())
 if approval.get('status')!='approved' or approval.get('manifest_sha256')!=sha(manifest) or approval.get('script_sha256')!=sha(__file__):raise ValueError('Missing/mismatched independent cleanup approval')
 if data['repository']!=str(root) or data['script_sha256']!=sha(__file__) or sha(root/'results/research5/archive_index.json')!=data['index_sha256']:raise ValueError('Verification context changed')
 for archive in data['archives_retained']:
  p=rooted(root,archive['path'])
  if p.stat().st_size!=archive['bytes'] or sha(p)!=archive['sha256']:raise ValueError('Archive changed since verification')
 # Check the entire removal set again before deleting any file. Hashes were
 # freshly verified above; stat seals prevent ordinary writes/replacements.
 tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0'))
 for row in data['files']:
  p=rooted(root,row['path']);s=p.stat()
  if row['path'] in tracked or (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)!=(row['st_dev'],row['st_ino'],row['bytes'],row['st_mtime_ns']):raise ValueError('Source changed since verification '+row['path'])
 journal=out/'removed_files.jsonl';deleted=0;total=0;before=shutil.disk_usage(root).free
 with journal.open('x') as log:
  for row in data['files']:
   p=rooted(root,row['path']);s=p.stat()
   if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)!=(row['st_dev'],row['st_ino'],row['bytes'],row['st_mtime_ns']):raise ValueError('Late source change '+row['path'])
   # Record intent before unlink; an interrupted cleanup remains auditable.
   log.write(json.dumps({'event':'unlink_intent','path':row['path'],'sha256':row['sha256'],'archive':row['archive']})+'\n');log.flush();os.fsync(log.fileno())
   p.unlink();deleted+=1;total+=row['bytes'];log.write(json.dumps({'event':'unlinked','path':row['path'],'bytes':row['bytes']})+'\n')
   if deleted%500==0:log.flush();os.fsync(log.fileno());print(json.dumps({'removed_files':deleted,'logical_bytes':total}),flush=True)
  log.flush();os.fsync(log.fileno())
 report={'status':'complete','removed_files':deleted,'removed_logical_bytes':total,'free_disk_bytes_before':before,'free_disk_bytes_after':shutil.disk_usage(root).free,'archives_retained':data['archives_retained'],'manifest_sha256':sha(manifest),'independent_approval_sha256':sha(review),'restore_command':data['restore_command'],'all_indexed_duplicates_removed':all(not (root/r['path']).exists() for r in data['files'])}
 write_new(out/'cleanup_result.json',report);print(json.dumps(report,indent=2),flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['verify','remove']);p.add_argument('--root',default='.');p.add_argument('--output',required=True);p.add_argument('--review');a=p.parse_args();root=Path(a.root).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
 if a.action=='verify':verify(root,out)
 else:
  if not a.review:raise ValueError('Review required')
  remove(root,out,a.review)
if __name__=='__main__':main()
