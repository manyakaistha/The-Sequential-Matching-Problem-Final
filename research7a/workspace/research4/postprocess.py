"""Run named exploratory summaries only after exact fixed stages finish."""
import hashlib,json,resource,subprocess,sys,time
from pathlib import Path
from research4.stages import ledger
ROOT=Path('results/research4')
def complete(name):
    p=ROOT/(name+'.json')
    if not p.exists():return False
    return json.loads(p.read_text()).get('complete',False)
def run(command,source):
    digest=hashlib.sha256(Path(source).read_bytes()).hexdigest();ledger(command,'started',analysis_source_sha256=digest)
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.perf_counter();log=ROOT/(Path(source).stem+'_'+command[-1].split('/')[-1]+'.log')
    with log.open('x') as out:done=subprocess.run(command,stdout=out,stderr=subprocess.STDOUT)
    after=resource.getrusage(resource.RUSAGE_CHILDREN);assert hashlib.sha256(Path(source).read_bytes()).hexdigest()==digest,'running analysis source changed'
    ledger(command,'finished',returncode=done.returncode,wall_seconds=time.perf_counter()-start,child_cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,analysis_source_sha256=digest)
    if done.returncode:raise ValueError('analysis failed; preserve log')
def main():
    for stage in ('focus','confirmation'):
        while not complete(stage):time.sleep(10)
        if stage=='focus':run([sys.executable,'-m','research4.ablations',str(ROOT/'focus.json'),'--output',str(ROOT/'focus_ablations.json')],'research4/ablations.py')
        run([sys.executable,'-m','research4.mechanisms',str(ROOT/(stage+'.json')),'--output',str(ROOT/(stage+'_mechanisms.json'))],'research4/mechanisms.py')
        run([sys.executable,'-m','research4.deadline_audit','--input',str(ROOT/(stage+'.json')),'--output',str(ROOT/('deadline_audit_'+stage+'.json'))],'research4/deadline_audit.py')
if __name__=='__main__':main()
