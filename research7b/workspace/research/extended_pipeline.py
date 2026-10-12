"""Finish registered stages sequentially after development, with fail-closed gates.

This orchestration never changes models after selection or extends confirmation.
Each actual command is recorded; output is streamed to per-stage logs.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

PY=sys.executable
RESULTS=Path('results/extended')
COMMANDS=RESULTS/'experiment_commands.json'
records=json.loads(COMMANDS.read_text()) if COMMANDS.exists() else []


def stamp():return datetime.now(timezone.utc).isoformat()
def read(name):return json.loads((RESULTS/name).read_text())
def run(args,log,env=None):
    record=dict(command=args,log=str(RESULTS/log),started_at_utc=stamp())
    records.append(record);COMMANDS.write_text(json.dumps(records,indent=2)+'\n')
    print('START',stamp(),log,flush=True)
    with (RESULTS/log).open('w') as output:
        p=subprocess.run(args,stdout=output,stderr=subprocess.STDOUT,env=env)
    record.update(exit_code=p.returncode,finished_at_utc=stamp());COMMANDS.write_text(json.dumps(records,indent=2)+'\n')
    if p.returncode:raise RuntimeError('Failed '+log)
    print('DONE',stamp(),log,flush=True)


def main():
    if (RESULTS/'pipeline_complete.json').exists():
        raise RuntimeError('Completed study: use the reproduction guide in a separate checkout; do not overwrite frozen artifacts.')
    while not (RESULTS/'development.json').exists() or not read('development.json')['complete']:
        time.sleep(15)
    dev=read('development.json')
    assert all(r['valid'] for r in dev['episodes'])
    safe=read('stress_container_safe.json')
    assert safe['complete'] and all(r['valid_protocol'] for r in safe['cases'])
    assert hashlib.sha256(Path('research/extended_policy_safe.py').read_bytes()).hexdigest()==safe['source_sha256']
    source=Path('extended_policy.py');archived=Path('research/extended_policy_development.py')
    shutil.copyfile(source,archived)
    assert hashlib.sha256(archived.read_bytes()).hexdigest()==dev['code_hashes']['extended_policy.py']
    shutil.copyfile('research/extended_policy_safe.py',source)
    record=dict(adopted_at_utc=stamp(),old_source=str(archived),
                old_sha256=dev['code_hashes']['extended_policy.py'],
                new_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                change='Production guard only; unchanged probability, learning, query and allocation objectives.',
                patch='research/extended_safety.patch',stress_original='results/extended/stress_container_original.json',
                stress_fixed='results/extended/stress_container_safe.json')
    (RESULTS/'production_guard_adoption.json').write_text(json.dumps(record,indent=2)+'\n')
    import os
    env=dict(os.environ,EXTENDED_SAFETY_TEST_TARGET='actual')
    run([PY,'-m','unittest','-v','research.test_extended_policy','research.test_extended_safety'],'tests_final_policy.log',env)
    names=','.join(sorted({r['policy'] for r in dev['episodes']}))
    run([PY,'-m','research.extended_benchmark','--policies',names,'--seeds','1001','--output',str(RESULTS/'guard_regression.json'),
         '--traces',str(RESULTS/'guard_regression_traces')],'guard_regression.log')
    run([PY,'-m','research.extended_guard_verify'],'guard_regression_check.log')
    run([PY,'-m','research.extended_analysis',str(RESULTS/'development.json')],'development_statistics.log')
    run([PY,'-m','research.extended_interactions',str(RESULTS/'development.json')],'interactions.log')
    run([PY,'-m','research.extended_select','shortlist'],'shortlist.log')
    plan=read('selection_plan.json')
    run([PY,'-m','research.extended_benchmark','--policies',','.join(plan['policies']),'--seeds','2001:2012',
         '--output',str(RESULTS/'selection.json')],'selection.log')
    run([PY,'-m','research.extended_analysis',str(RESULTS/'selection.json')],'selection_statistics.log')
    run([PY,'-m','research.extended_select','freeze'],'freeze.log')
    frozen=read('frozen_candidate.json');name=frozen['policy'];cfg=json.dumps(frozen['configuration'])
    from research.extended_select import inference_hashes,auxiliary_hashes,complete
    assert inference_hashes()==frozen['code_hashes'] and auxiliary_hashes()==frozen['auxiliary_code_hashes']
    run([PY,'-m','research.extended_analysis',str(RESULTS/'development.json'),'--reference',name,
         '--output',str(RESULTS/'development_vs_selected_statistics.json')],'development_vs_selected_statistics.log')
    run([PY,'-m','research.extended_benchmark','--policies','greedy,'+name,'--seeds','3001:3040',
         '--output',str(RESULTS/'confirmation.json'),'--traces',str(RESULTS/'confirmation_traces')],'confirmation.log')
    complete(str(RESULTS/'confirmation.json'),range(3001,3041),['greedy',name])
    assert read('confirmation.json')['code_hashes']==frozen['code_hashes']
    assert inference_hashes()==frozen['code_hashes'] and auxiliary_hashes()==frozen['auxiliary_code_hashes']
    run([PY,'-m','research.extended_analysis',str(RESULTS/'confirmation.json'),'--confirmatory',name],'confirmation_statistics.log')
    run([PY,'-m','research.extended_benchmark','--policies','greedy,'+name,'--seeds','1001','--output',str(RESULTS/'subprocess.json'),
         '--execution','subprocess','--traces',str(RESULTS/'subprocess_traces')],'subprocess.log')
    run(['docker','build','-f','Dockerfile.extended','-t','sequential-extended:1.0','.'],'docker_build_final.log')
    run([PY,'-m','research.extended_production','--config',cfg,'--output',str(RESULTS/'production.json')],'production.log')
    (RESULTS/'pipeline_complete.json').write_text(json.dumps(dict(completed_at_utc=stamp(),frozen_policy=name,
        stages='development guard regression selection confirmation subprocess container',
        remaining='Lead calibration/mechanism audit, report/figures, provenance and final integrity review'),indent=2)+'\n')
    print('PIPELINE COMPLETE',name,stamp(),flush=True)

if __name__=='__main__':main()
