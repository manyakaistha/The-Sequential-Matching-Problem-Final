"""Execute the finite registered B--E funnel; no significance-dependent repetition."""
from datetime import datetime,timezone
import hashlib,json,resource,subprocess,sys,time
from pathlib import Path
from research4.benchmark import hashes
from research4.policy import CANDIDATES
from research4.stages import ROOT,ledger,save_new

def main():
    registry=Path('research4/EXPERIMENT_REGISTRY.md')
    save_new('screen_freeze.json',dict(utc=datetime.now(timezone.utc).isoformat(),code_hashes=hashes(),configuration=CANDIDATES,registry_sha256=hashlib.sha256(registry.read_bytes()).hexdigest()))
    command=[sys.executable,'-m','research4.benchmark','--policies',','.join(CANDIDATES),'--seeds','80001:80012','--workers','2','--output',str(ROOT/'screen.json'),'--traces',str(ROOT/'screen_traces')]
    ledger(command,'started');before=resource.getrusage(resource.RUSAGE_CHILDREN);started=time.perf_counter()
    with (ROOT/'screen.log').open('x') as out:completed=subprocess.run(command,stdout=out,stderr=subprocess.STDOUT)
    after=resource.getrusage(resource.RUSAGE_CHILDREN);ledger(command,'finished',returncode=completed.returncode,wall_seconds=time.perf_counter()-started,child_cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime)
    if completed.returncode:raise ValueError('retain failed screen; no silent replacement')
    for phase in ('focus','selection','confirmation'):
        command=[sys.executable,'-m','research4.stages',phase];ledger(command,'started')
        subprocess.run(command,check=True);ledger(command,'finished')
if __name__=='__main__':main()
