"""Generate reproducibility manifest without altering prior research artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='results/extended/manifest.json');a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    code=[root/'REPORT.md',root/'policy.py',root/'research_policy.py',root/'extended_policy.py',root/'kit.py',root/'evaluate.py',
          root/'Dockerfile.extended',root/'requirements-research.txt',root/'docs/REFERENCES.md',root/'research/EXPERIMENT_REGISTRY.md']
    code+=sorted((root/'research').glob('extended_*.py'))+sorted((root/'research').glob('EXTENDED_*.md'))
    code+=sorted((root/'research').glob('FINAL_*.md'))
    code+=sorted((root/'research').glob('*2026-10-07.md'))
    code+=[root/'research/terminal_model.py',root/'research/test_extended_policy.py',root/'research/test_extended_safety.py',
           root/'research/extended_safety.patch',root/'.dockerignore',root/'.gitignore',
           root/'research/THEORY.md',root/'research/legacy_references.md',root/'data_manifest.json',
           root/'requirements-research.lock.txt']
    files={str(f.relative_to(root)):dict(sha256=digest(f),bytes=f.stat().st_size) for f in code if f.exists()}
    artifacts={str(f.relative_to(root)):dict(sha256=digest(f),bytes=f.stat().st_size)
               for f in sorted((root/'results/extended').rglob('*')) if f.is_file() and f!=root/a.output and f.suffix in ('.json','.png','.log','.gz')}
    experiments={}
    for name in ('development','guard_regression','selection','confirmation','subprocess'):
        f=root/'results/extended'/f'{name}.json'
        if not f.exists():continue
        raw=json.loads(f.read_text());rows=raw['episodes']
        experiments[name]=dict(complete=raw['complete'],episodes=len(rows),planned_episodes=raw['planned_episodes'],
                              seeds=sorted({r['seed'] for r in rows}),families=sorted({r['variant'] for r in rows}),
                              configurations={r['policy']:r['configuration'] for r in rows},code_hashes=raw['code_hashes'],
                              execution=sorted({r['execution'] for r in rows}))
    out=dict(scope='Public synthetic simulator only; evaluated policies observation-only; oracle audits explicitly offline.',
             git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
             git_status=subprocess.check_output(['git','status','--short'],cwd=root,text=True),
             python=sys.version,platform=platform.platform(),
             packages=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True).splitlines(),
             files=files,artifacts=artifacts,experiments=experiments,
             legacy_configuration_aliases={'prior_product':{'fusion':'product'},'greedy':{'baseline':'greedy'}},
             prior_report=dict(path='research/REPORT_2026-10-07.md',sha256=digest(root/'research/REPORT_2026-10-07.md')),
             caveat='Working tree contains pre-existing user research. Git head alone is not the experiment code; file hashes identify it.')
    Path(a.output).write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('Manifest:',len(files),'sources,',len(artifacts),'artifacts')

if __name__=='__main__':main()
