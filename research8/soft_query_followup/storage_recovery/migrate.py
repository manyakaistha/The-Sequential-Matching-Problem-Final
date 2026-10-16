"""One-time quiescent byte-preserving migration. Never changes commit records."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from research8.soft_query_followup.v3.storage import archive_attempt

output=ROOT/'results/research8/soft_query_followup/v2_replication'
recovery=Path(__file__).resolve().parent
with (ROOT/'research8/soft_query_followup/v2/.simulation.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 commits={}
 before={}
 for p in sorted((output/'commits').glob('*.json')):
  row=json.loads(p.read_text());rel=row['attempt_relative_path'];commits[rel]=row
  before[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
 leaves=[p for p in (output/'attempts').glob('*/*') if p.is_dir() and any(q.is_file() for q in p.iterdir())]
 total_raw=total_compressed=0
 records=[]
 started=time.monotonic()
 for i,p in enumerate(sorted(leaves),1):
  rel=p.relative_to(output).as_posix();row=commits.get(rel)
  if row and {f.name for f in p.iterdir() if f.is_file()} != set(row['artifact_hashes']):
   raise ValueError('raw committed coverage changed '+rel)
  m=archive_attempt(output,rel,row['artifact_hashes'] if row else None,codec='zstd',level=3,remove_raw=True)
  total_raw+=sum(v['bytes'] for v in m['files'].values());total_compressed+=m['archive_bytes']
  records.append({'attempt_relative_path':rel,'committed':row is not None,'archive_sha256':m['archive_sha256'],
                  'archive_bytes':m['archive_bytes'],'logical_files':len(m['files'])})
  if i%25==0 or i==len(leaves):print(f'{i}/{len(leaves)} attempts verified and archived; {total_compressed/2**20:.1f}MiB compressed',flush=True)
 after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (output/'commits').glob('*.json')}
 assert before==after,'Commit bytes changed'
 report={'status':'all_attempts_archived_exact_bytes','committed_cells':len(commits),'attempts_archived':len(records),
         'logical_bytes_preserved':total_raw,'archive_bytes':total_compressed,'elapsed_seconds':time.monotonic()-started,
         'commits_unchanged':True,'commit_sha256':before,'attempts':records}
 with (recovery/'migration_result.json').open('x') as h:json.dump(report,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
 print(json.dumps({k:v for k,v in report.items() if k not in ('commit_sha256','attempts')},indent=2),flush=True)
