"""Constructed paired-data checks; no policy invocation or sampled outcomes."""
import json
from pathlib import Path
from unittest.mock import patch

from research8.soft_query_followup.v2.analysis import analyze


def sample(tmp_path, gains):
    arms=['G','G_random_soft','G_targeted_soft'];families=['development','sparse','cold_start','delayed','shift','drift']
    reg={'ordered_seed_list':[1,2],'families':families,'policy_ids':arms,
         'registration_sha256':'fixture','analysis':{'contrasts':[['G_random_soft','G'],['G_targeted_soft','G'],['G_targeted_soft','G_random_soft']]}}
    (tmp_path/'registration.json').write_text(json.dumps(reg));(tmp_path/'commits').mkdir()
    for seed in (1,2):
        for family in families:
            for arm in arms:
                key=f'{seed}_{family}_{arm}'; attempt=tmp_path/'attempts'/key;attempt.mkdir(parents=True)
                (attempt/'daily_telemetry.jsonl').write_text(json.dumps({'budget_remaining_after_hard':12,'candidate_count':0,'match_changed':False})+'\n')
                q=2+(gains[seed-1] if arm!='G' else 0)
                metric={'arrived_members':200,'mutual_second_meeting_intention':q,'coverage':.3,'hard_asks':1,'soft_asks':0}
                row={'cell':{'seed':seed,'family':family,'policy_id':arm},'metrics':metric,
                     'attempt_relative_path':f'attempts/{key}','invocation_seconds_max':.1}
                (tmp_path/'commits'/f'{key}.json').write_text(json.dumps(row))
    return tmp_path/'registration.json'


def test_inference_uses_seed_groups_and_reports_ties(tmp_path):
    reg=sample(tmp_path,[1,0])
    with patch('research8.soft_query_followup.v2.analysis.audit_run',return_value={'status':'fixture'}):
        result=analyze(tmp_path,reg)
    c=result['contrasts']['G_targeted_soft - G']
    assert c['n_clusters']==2 and c['df']==1
    assert c['mean_diff']==.25 and c['se']==.25
    assert result['contrasts']['G_targeted_soft - G_random_soft']['degeneracy']=='all_ties'


def test_constant_nonzero_difference_has_no_fake_confidence_interval(tmp_path):
    reg=sample(tmp_path,[1,1])
    with patch('research8.soft_query_followup.v2.analysis.audit_run',return_value={'status':'fixture'}):
        result=analyze(tmp_path,reg)
    c=result['contrasts']['G_random_soft - G']
    assert c['ci_95_exploratory'] is None
    assert c['p_value_unadjusted']==1.0
    assert c['degeneracy']=='constant_nonzero_difference_no_standard_t_inference'
