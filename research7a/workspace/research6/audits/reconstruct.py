"""Reconstruct registered, previously examined G traces; separate privileged state."""
import argparse
import json
from pathlib import Path
import time
from research6.recorder import sha, chunk, write_new
from kit import Simulator, generate, VERSION


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--registration',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();reg=json.loads(Path(args.registration).read_text())
    if reg['no_world_generation'] or reg['new_seed_worlds']!=0:raise ValueError('reconstruction scope mislabeled')
    for source,expected in reg['sources'].items():
        if sha(source)!=expected:raise ValueError('registered source mismatch')
    root=Path(args.output);root.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();cpu=time.process_time();rows=[];generation_calls=0
    print(f'[A reconstruction] {len(reg["cells"])} examined worlds | public={root}/public | privileged={root}/privileged',flush=True)
    for cell in reg['cells']:
        path=Path(cell['trace'])
        if sha(path)!=cell['trace_sha256']:raise ValueError('prior trace changed')
        trace=json.loads(path.read_text())
        if trace['policy']!='greedy' or trace['seed']!=cell['seed'] or trace['variant']!=cell['family']:raise ValueError('trace cell mismatch')
        ident=f'{cell["family"]}_{cell["seed"]}'
        public=root/'public'/ident;private=root/'privileged'/ident
        public.mkdir(parents=True,exist_ok=False);private.mkdir(parents=True,exist_ok=False)
        write_new(public/'started.json',{'cell':cell,'reconstruction':True,'new_seed_world':False})
        try:
            world=generate(cell['seed'],200,'evaluation',cell['family']);generation_calls+=1
            chunk(private/'initial.json.gz',{'privileged':True,'world':world})
            sim=Simulator(world);sequence=0
            match_states={item['day']:item['state'] for item in trace['match_states']}
            for phase,day,action in trace['actions']:
                sequence+=1
                if sim.day!=day or phase!=('ask' if sequence%2 else 'match'):raise ValueError('saved action sequence invalid')
                state=sim.observe()
                request={'schema_version':VERSION,'phase':phase,'state':state,'memory':None if sequence==1 else {}}
                chunk(public/f'{sequence:03d}.json.gz',{'request':request,'saved_action':action,'source':'examined shipped-G trace'})
                if phase=='ask':sim.resolve_asks(action)
                else:
                    stripped={k:v for k,v in state.items() if k!='ask_log'}
                    if stripped!=match_states[day]:raise ValueError('causal public reconstruction mismatch at '+str(day))
                    sim.advance(action)
            if sequence!=120 or sim.day!=60:raise ValueError('incomplete actions')
            for _ in range(40):sim.advance([])
            if sim.introductions!=trace['introductions'] or sim.receive_feedback()!=trace['completed_feedback']:raise ValueError('final outcomes mismatch')
            chunk(public/'outcomes.json.gz',{'introductions':sim.introductions,'feedback':sim.receive_feedback(),'metrics':sim.metrics(),'day':sim.day})
            chunk(private/'final.json.gz',{'privileged':True,'state':{k:sorted(v) if isinstance(v,set) else v for k,v in vars(sim).items()}})
            write_new(public/'closed.json',{'valid':True,'phase_calls':sequence,'final_day':sim.day,'cell':cell})
            rows.append({'cell':cell,'valid':True,'calls':sequence})
        except BaseException as error:
            write_new(public/'failed.json',{'valid':False,'error':repr(error),'cell':cell})
            raise
        elapsed=time.monotonic()-started;used=time.process_time()-cpu
        print(f'[A reconstruction] {len(rows)}/{len(reg["cells"])} {ident} | causal states/outcomes exact | {elapsed:.1f}s wall {used:.1f}s CPU | chunks saved',flush=True)
        if used>reg['cpu_seconds_max']:raise RuntimeError('registered A CPU ceiling reached; partial attempts preserved')
    if generation_calls!=reg['expected_generation_calls']:raise ValueError('generation count mismatch')
    write_new(root/'summary.json',{'complete':True,'cells':rows,'world_generation_calls':generation_calls,'new_seed_worlds':0,
        'public_phase_states':sum(r['calls'] for r in rows),'wall_seconds':time.monotonic()-started,'cpu_seconds':time.process_time()-cpu,
        'storage_bytes':sum(p.stat().st_size for p in root.rglob('*') if p.is_file()),'registration_sha256':sha(args.registration)})


if __name__=='__main__':main()
