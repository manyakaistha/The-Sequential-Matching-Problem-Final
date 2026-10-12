"""Finite independent wrapper stress and restricted dense parity, existing seed101."""
import argparse,contextlib,hashlib,io,json,resource,signal,sys,time,unittest
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
import evaluate
from kit import HARD,Simulator,generate
from research4 import policy
from research4.production import captured_invoke

class WrapperChecks(unittest.TestCase):
    def req(self):return dict(phase='match',state=Simulator(generate(101,200,'evaluation')).observe(),memory=None)
    def test_empty_exhausted_no_edges(self):
        for cfg in policy.CANDIDATES.values():
            r=self.req();r['state']['members']=[]
            self.assertEqual(policy.decide(r,cfg),dict(pairs=[],memory={}))
            r=self.req();r['phase']='ask';r['state']['ask_budget_remaining']=0
            self.assertEqual(policy.decide(r,cfg),dict(asks=[],memory={}))
            r=self.req()
            for m in r['state']['members']:m['available']=False
            self.assertEqual(policy.decide(r,cfg),dict(pairs=[],memory={}))
    def test_malformed_memory_ignored(self):
        r=self.req()
        for cfg in policy.CANDIDATES.values():
            expected=policy.decide(r,cfg)
            for memory in (None,'broken',[],{'actors':'bad'}):
                r['memory']=memory;self.assertEqual(policy.decide(r,cfg),expected)
    def test_oversized_and_malformed_state(self):
        r=self.req();r['memory']='x'*(policy.LIMIT+1)
        self.assertEqual(policy.decide(r),dict(pairs=[],memory={}))
        before=policy.FALLBACK_COUNT
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(policy.decide(dict(phase='match',state={'members':None},memory=None)),dict(pairs=[],memory={}))
        self.assertEqual(policy.FALLBACK_COUNT,before+1)
        self.assertIn('round4 fallback:',err.getvalue())
    def test_real_deadline_and_outer_timer(self):
        old_handler=signal.getsignal(signal.SIGALRM);old_timer=signal.getitimer(signal.ITIMER_REAL)
        try:
            signal.signal(signal.SIGALRM,lambda *_:None);signal.setitimer(signal.ITIMER_REAL,.03)
            before=policy.FALLBACK_COUNT;start=time.monotonic()
            with patch.object(policy,'inner',side_effect=lambda *args:time.sleep(.2)),contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(policy.decide(self.req()),dict(pairs=[],memory={}))
            self.assertLess(time.monotonic()-start,.15);self.assertEqual(policy.FALLBACK_COUNT,before+1)
            signal.setitimer(signal.ITIMER_REAL,5.)
            policy.decide(self.req());self.assertGreater(signal.getitimer(signal.ITIMER_REAL)[0],4.)
        finally:
            signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old_handler)
            if old_timer[0]:signal.setitimer(signal.ITIMER_REAL,*old_timer)
    def test_subprocess_control_equivalence(self):
        for name,cfg in policy.CANDIDATES.items():
            r=self.req();expected=policy.decide(r,cfg)
            actual,_,stderr=captured_invoke([sys.executable,'-m','research4.policy','--candidate',name],r)
            self.assertEqual(actual,expected);self.assertEqual(stderr,'')

def dense(image):
    sim=Simulator(generate(101,200,'evaluation'));sim.day=20;s=sim.observe()
    fields=dict(age_min=18,age_max=65,who_to_meet=['man'],relationship_structure='monogamous',smoking='no',partner_smoking='any',has_children=False,partner_children='any',wants_children='unsure',acceptable_zones=['zone_a'],schedule=['weekend_day'])
    for m in s['members']:
        m.update(age=30,gender='man',zone='zone_a',available=True);m['fields'].update(fields)
        for k in HARD:m['field_status'][k]='observed';m['field_observed_day'][k]=0
    # Four independent complete dyads per endpoint =>800public response events.
    # These use only constructed public records, not hidden world truth.
    s['introductions']=[];s['feedback']=[]
    ids=[m['member_id'] for m in s['members']]
    for n in range(4):
        for j,ident in enumerate(ids):
            other=ids[(j+n+1)%len(ids)];intro='stress_'+str(n)+'_'+str(j)
            s['introductions'].append(dict(introduction_id=intro,user_a=ident,user_b=other,assigned_day=0))
            s['feedback'].append(dict(introduction_id=intro,member_id=ident,event='introduction_response',value='yes' if n%2 else 'no'))
    rows=[]
    for name,cfg in policy.CANDIDATES.items():
        req=dict(phase='match',state=s,memory={'bad':'ignored'})
        before=policy.FALLBACK_COUNT;t=time.monotonic();expected=policy.decide(req,cfg);host=time.monotonic()-t
        actual,seconds,stderr=captured_invoke(evaluate.docker_command(image)+['--candidate',name],req)
        assert actual==expected and not stderr and policy.FALLBACK_COUNT==before
        assert len(actual['pairs'])==100
        rows.append(dict(candidate=name,pairs=len(actual['pairs']),exact_response_equal=True,host_seconds=host,container_seconds=seconds,request_bytes=len(json.dumps(req).encode()),memory_bytes=len(json.dumps(actual['memory']).encode()),fallback_warning_count=0))
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--dense',action='store_true');p.add_argument('--image',default='sequential-round4:research');a=p.parse_args()
    target=Path(a.output)
    if target.exists():raise ValueError('refuse overwrite')
    start=time.monotonic();utc=datetime.now(timezone.utc).isoformat();self0=resource.getrusage(resource.RUSAGE_SELF);child0=resource.getrusage(resource.RUSAGE_CHILDREN)
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WrapperChecks))
    print(stream.getvalue(),flush=True)
    rows=dense(a.image) if a.dense and result.wasSuccessful() else []
    self1=resource.getrusage(resource.RUSAGE_SELF);child1=resource.getrusage(resource.RUSAGE_CHILDREN)
    out=dict(valid=result.wasSuccessful(),tests=result.testsRun,log=stream.getvalue(),dense_rows=rows,scope='Existingseed101/synthetic public states, finite workload only; no universal timeout or peakRSS guarantee',wall_seconds=time.monotonic()-start,compute=dict(started_utc=utc,host_self_cpu_seconds=self1.ru_utime+self1.ru_stime-self0.ru_utime-self0.ru_stime,host_children_cpu_seconds=child1.ru_utime+child1.ru_stime-child0.ru_utime-child0.ru_stime,docker_daemon_container_cpu_seconds=None),source_hashes={s:hashlib.sha256(Path(s).read_bytes()).hexdigest() for s in ('research4/policy.py','research4/candidates.py','research4/test_wrapper.py')},command=[sys.executable,'-m','research4.test_wrapper']+sys.argv[1:])
    target.write_text(json.dumps(out,indent=2)+'\n')
    with Path('results/research4/commands_production.jsonl').open('a') as f:f.write(json.dumps(dict(command=out['command'],output=str(target),compute=out['compute'],wall_seconds=out['wall_seconds']))+'\n')
    if not result.wasSuccessful():raise SystemExit(1)
if __name__=='__main__':main()
