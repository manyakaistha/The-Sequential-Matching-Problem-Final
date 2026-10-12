"""Paired before/after production-guard regression on examined development worlds."""
import json
from pathlib import Path

FIELDS=('assignments','mutual_acceptances','dates','mutual_second_meeting_intention',
        'coverage','ask_cost','served_members','first_introduction_wait_days')


def main():
    old=json.loads(Path('results/extended/development.json').read_text())
    new=json.loads(Path('results/extended/guard_regression.json').read_text())
    assert old['complete'] and new['complete']
    previous={(r['policy'],r['variant'],r['seed']):r for r in old['episodes']}
    differences=[];ordering=[]
    for row in new['episodes']:
        before=previous[row['policy'],row['variant'],row['seed']]
        if not row['valid'] or any(row.get(k)!=before.get(k) for k in FIELDS):
            differences.append(dict(policy=row['policy'],variant=row['variant'],seed=row['seed'],kind='outcomes'))
        if row.get('action_sha256')!=before.get('action_sha256'):
            if row.get('semantic_action_sha256')==before.get('semantic_action_sha256'):
                ordering.append(dict(policy=row['policy'],variant=row['variant'],seed=row['seed']))
            else:differences.append(dict(policy=row['policy'],variant=row['variant'],seed=row['seed'],kind='semantic_actions'))
    changed=[p for p,h in old['code_hashes'].items() if new['code_hashes'].get(p)!=h]
    maximum=max(r['peak_latency_seconds'] for r in old['episodes'])
    out=dict(complete=True,paired_episodes=len(new['episodes']),semantic_or_outcome_differences=differences,
             ordering_only_differences=ordering,changed_inference_files=changed,
             old_code_hashes=old['code_hashes'],new_code_hashes=new['code_hashes'],
             original_development_max_call_seconds=maximum,original_max_below_guard=maximum<7,
             scope='Tested ordinary-world semantic equivalence, not all-resource/all-state proof. Stress demonstrates changed protective behavior.')
    Path('results/extended/guard_regression_check.json').write_text(json.dumps(out,indent=2)+'\n')
    assert not differences and changed==['extended_policy.py'] and maximum<7
    print('Guard parity passed:',len(new['episodes']),'paired episodes')

if __name__=='__main__':main()
