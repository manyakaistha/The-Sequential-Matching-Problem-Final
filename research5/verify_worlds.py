"""Privileged initial-world provenance only; no policy/evaluator invocation."""
import gzip,hashlib,json,time,resource,sys
from pathlib import Path
from kit import generate
ROOT=Path('results/research5')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 target=ROOT/'world_checks.json';assert not target.exists(),'refuse overwrite'
 start=time.process_time();wall=time.monotonic();data=json.loads((ROOT/'confirmation.json').read_text());design=json.loads((ROOT/'design.json').read_text());assert data['complete']
 assert sha('kit.py')==design['frozen_inherited_hashes']['kit.py']
 expected={(p,s,v) for p in ('greedy','population_control') for s in range(90001,90431) for v in design['families']};seen=set();pairs={};failures=[];generator_calls=0
 for index,row in enumerate(data['episodes']):
  key=row['policy'],row['seed'],row['variant'];assert key in expected and key not in seen;seen.add(key)
  cell=row['seed'],row['variant'];path=Path(row['privileged_audit_log'])
  try:
   with gzip.open(path,'rt',encoding='utf-8') as f:record=json.loads(f.readline())
   assert record['kind']=='initial_world' and record['privileged'] is True
   world=record['world'];canonical=json.dumps(world,sort_keys=True,allow_nan=False).encode();stored=hashlib.sha256(canonical).hexdigest()
   if cell not in pairs:
    actual=generate(row['seed'],200,'evaluation',row['variant']);generator_calls+=1
    generated=hashlib.sha256(json.dumps(actual,sort_keys=True,allow_nan=False).encode()).hexdigest()
    assert world==actual,'Saved initial world differs from frozen generation'
    pairs[cell]={'stored_sha256':stored,'generated_sha256':generated,'policies':[row['policy']]}
   else:
    assert stored==pairs[cell]['stored_sha256'],'Policies did not start from equal world'
    pairs[cell]['policies'].append(row['policy'])
  except Exception as error:failures.append({'policy':key[0],'seed':key[1],'variant':key[2],'path':str(path),'error_type':type(error).__name__,'error':str(error)})
  if (index+1)%600==0:print('initial-world audit',index+1,'/',len(data['episodes']),flush=True)
  if time.process_time()-start>110:
   failures.append({'error':'CPU guard reached; remaining records unaudited','audited_rows':index+1});break
 complete=seen==expected and len(seen)==5160 and len(pairs)==2580 and all(set(x['policies'])=={'greedy','population_control'} and len(x['policies'])==2 for x in pairs.values())
 obj={'complete':complete,'pass':complete and not failures,'committed_rows_processed':len(seen),'paired_seed_family_cells':len(pairs),'generator_calls':generator_calls,'failures':failures,'cpu_seconds':time.process_time()-start,'wall_seconds':time.monotonic()-wall,'scope':'Offline initial-world regeneration of alreadyexaminedfixed90001–90430 worlds only; one worker; no policy inference or fitting, no future outcome inspection. First gzip JSONL line only; closure/integrity checked separately by fullartifactaudit. One generation percell with exact world equality for firstpolicy, equal canonical worlddigest for secondpolicy.','command':sys.argv,'source_hashes':{'kit.py':sha('kit.py'),'research5/verify_worlds.py':sha(__file__),'results/research5/design.json':sha(ROOT/'design.json'),'results/research5/confirmation.json':sha(ROOT/'confirmation.json')},'world_digests':{str(s)+':'+v:info for (s,v),info in sorted(pairs.items())}}
 target.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps({k:obj[k] for k in ('complete','pass','committed_rows_processed','paired_seed_family_cells','generator_calls','cpu_seconds','wall_seconds','failures')},indent=2));assert obj['pass'],'Partial/mismatch audit retained without passing claim'
if __name__=='__main__':main()
