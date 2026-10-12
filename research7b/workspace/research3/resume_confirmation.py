"""Resume only interrupted missing jobs of an already frozen, fixed-sample run."""
import hashlib,json,shutil,time,resource
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
from research3.benchmark import hashes,run
from research3.analyze import analyze
from research3.stages import ledger,save_new
ROOT=Path('results/research3')
def main():
    target=ROOT/'confirmation.json';data=json.loads(target.read_text());freeze=json.loads((ROOT/'freeze.json').read_text())
    assert data['code_hashes']==freeze['code_hashes']==hashes()
    assert hashlib.sha256(Path('research3/EXPERIMENT_REGISTRY.md').read_bytes()).hexdigest()==freeze['registry_sha256']
    assert data['planned_seeds']==list(range(freeze['confirmation_seeds'][0],freeze['confirmation_seeds'][1]+1))
    assert data['planned_policies']==['greedy',freeze['policy']]
    seen={(r['policy'],r['seed'],r['variant']) for r in data['episodes']};assert len(seen)==len(data['episodes'])
    jobs=[(n,s,v,str(ROOT/'confirmation_traces'),'in_process_json') for s in data['planned_seeds'] for v in data['planned_variants'] for n in data['planned_policies'] if (n,s,v) not in seen]
    backup=ROOT/'confirmation_interrupted.json';assert not backup.exists();shutil.copyfile(target,backup)
    ledger(['python3','-m','research3.resume_confirmation'],'started',reason='host process interruption; missing registered jobs only',existing_episodes=len(seen),missing_episodes=len(jobs))
    before=resource.getrusage(resource.RUSAGE_CHILDREN);started=time.perf_counter()
    with ProcessPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(run,j) for j in jobs]):
            row=future.result();data['episodes'].append(row);data['episodes'].sort(key=lambda r:(r['seed'],r['variant'],r['policy']))
            data['complete']=len(data['episodes'])==data['planned_episodes'];tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(target)
            print(row['policy'],row['seed'],row['variant'],row['valid'],flush=True)
    result=analyze(target);save_new('confirmation_statistics.json',result)
    after=resource.getrusage(resource.RUSAGE_CHILDREN);ledger(['python3','-m','research3.resume_confirmation'],'finished',wall_seconds=time.perf_counter()-started,child_cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,missing_episodes=len(jobs))
if __name__=='__main__': main()
