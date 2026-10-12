"""Execute registered deterministic shortlisting and freezing, without retuning."""
import argparse
import hashlib
from datetime import datetime, timezone
import json
from pathlib import Path
import shlex
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research.extended_candidates import CANDIDATES
from research.extended_analysis import analyze
from evaluate import VARIANTS


def auxiliary_hashes():
    return {str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in
            map(Path,('policy.py','research/extended_benchmark.py','research/extended_select.py'))}


def inference_hashes():
    return {str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in
            map(Path,('extended_policy.py','research/terminal_model.py','research/extended_candidates.py',
                      'research_policy.py','kit.py','evaluate.py'))}


def complexity(name):
    cfg=CANDIDATES[name]
    model=0 if cfg.get('model')=='simple' else 1 if cfg.get('learning') is False else 2
    return (model,int(cfg.get('asks') in ('value','two_query') or bool(cfg.get('soft'))),
            int(cfg.get('engine')=='blossom'),int(bool(cfg.get('batching')) or cfg.get('opportunity','none')!='none'),len(cfg))


def complete(path,seeds=None,policies=None):
    raw=json.loads(Path(path).read_text())
    if not raw['complete'] or len(raw['episodes'])!=raw['planned_episodes'] or not all(r['valid'] for r in raw['episodes']):
        raise ValueError('Selection requires a complete valid experiment')
    stats=analyze(raw['episodes'])
    if not all(r['eligible'] for r in stats['policies'].values()):raise ValueError('ineligible policy')
    if seeds is not None and policies is not None:
        actual={(r['policy'],r['variant'],r['seed']) for r in raw['episodes']}
        expected={(n,f,s) for n in policies for f in VARIANTS for s in seeds}
        if actual!=expected or len(raw['episodes'])!=len(expected):raise ValueError('Registered grid mismatch')
        for r in raw['episodes']:
            if r['policy'] in CANDIDATES and r['configuration']!=CANDIDATES[r['policy']]:raise ValueError('Configuration changed')
    return raw,stats


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('shortlist','freeze'));a=p.parse_args()
    if a.stage=='shortlist':
        raw,stats=complete('results/extended/development.json',range(1001,1009),list(CANDIDATES)+['greedy','prior_product'])
        guard=json.loads(Path('results/extended/guard_regression_check.json').read_text())
        if guard['semantic_or_outcome_differences'] or guard['new_code_hashes']!=inference_hashes():
            raise ValueError('Verified guard-only patch required before selection')
        order=sorted(CANDIDATES,key=lambda n:(-stats['policies'][n]['primary']['mean'],len(CANDIDATES[n]),n))
        names=list(dict.fromkeys(order[:4]+['terminal_fifo','simple_fifo','independent_fifo','no_learning_fifo']))
        result=dict(rule='top four development new configurations plus four mandatory controls, deduplicated',
                    policies=names+['greedy','prior_product'],development_order=order,
                    development_scores={n:stats['policies'][n]['primary']['mean'] for n in order},code_hashes=raw['code_hashes'],
                    selection_seeds=list(range(2001,2013)),auxiliary_code_hashes=auxiliary_hashes(),
                    selection_code_hashes=inference_hashes(),production_guard_regression='results/extended/guard_regression_check.json',
                    registered_at_utc=datetime.now(timezone.utc).isoformat())
        Path('results/extended/selection_plan.json').write_text(json.dumps(result,indent=2)+'\n')
        print(','.join(result['policies']))
    else:
        plan=json.loads(Path('results/extended/selection_plan.json').read_text())
        raw,stats=complete('results/extended/selection.json',range(2001,2013),plan['policies'])
        if raw['code_hashes']!=plan['selection_code_hashes']:raise ValueError('Code changed after guard-patch selection freeze')
        if inference_hashes()!=raw['code_hashes']:raise ValueError('Current inference differs from evaluated selection')
        if auxiliary_hashes()!=plan['auxiliary_code_hashes']:raise ValueError('Baseline/runner/selection code changed after shortlisting')
        names=[n for n in plan['policies'] if n in CANDIDATES]
        top=max(stats['policies'][n]['primary']['mean'] for n in names)
        close=[n for n in names if stats['policies'][n]['primary']['mean']>=top-.05-1e-12]
        name=min(close,key=lambda n:(complexity(n),-stats['policies'][n]['primary']['mean'],n))
        result=dict(policy=name,configuration=CANDIDATES[name],code_hashes=raw['code_hashes'],
                    selection_primary=stats['policies'][name]['primary']['mean'],maximum_selection_primary=top,
                    simplicity_candidates=close,complexity_order={n:complexity(n) for n in close},
                    rule='within .05 of top; registered model/query/allocation/waiting cost tuple, score, alphabetical',
                    frozen_before_confirmation=True,confirmation_seeds=list(range(3001,3041)),
                    confirmatory_comparison=name+' minus greedy, scenario-balanced seed clusters, two-sided alpha .05',
                    selection_artifact='results/extended/selection.json',auxiliary_code_hashes=auxiliary_hashes(),
                    frozen_at_utc=datetime.now(timezone.utc).isoformat())
        Path('results/extended/frozen_candidate.json').write_text(json.dumps(result,indent=2)+'\n')
        print(name)

if __name__=='__main__':main()
