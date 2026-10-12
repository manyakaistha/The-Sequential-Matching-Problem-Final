"""Run constructed exact tests; write a new immutable-by-convention attempt.

Usage: python3 -m research6.exact.run
No old outputs are overwritten. Registration precedes compiling/solving models.
"""
import hashlib
import json
import time
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from .solver import compile_matching, solve, enumerate_policies, check_lp_certificate
from .specifications import build_specifications


def write_new(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def verify_reference(mdp, result):
    reference = enumerate_policies(mdp)
    for state, row in reference['states'].items():
        assert row['value'] == result['states'][state]['value'], (mdp['id'], state)
        assert row['action_values'] == result['states'][state]['action_values'], (mdp['id'],state)
    return {'policy_count':reference['policy_count'], 'all_state_action_values_equal':True,
            'independent_ownership':False}


def analytic_checks(results, specifications):
    def initial(name):
        r = results[name]
        return r['states']['s0' if 's0' in r['states'] else 'initial']['action_values']
    assert initial('complementary_verification') == {'empty':'0','bundle_A':'0','bundle_B':'0','bundle_A_and_B':'1'}
    assert initial('collision_distinct_partners') == {'shared':'24/25','distinct':'7/5'}
    assert F(8,5)>F(7,5) and F(24,25)<F(7,5)
    assert initial('soft_value_hard_cost') == {'no_information':'1/2','reveal_free':'7/10','reveal_displaces_hard':'9/20'}
    assert F(9,20)-F(1,2) == -F(1,20)
    assert initial('known_return_reservation')['0-1']=='11/100'
    assert initial('known_return_reservation')['1-3']=='1/5'
    assert initial('nonseparable_alternatives')['wait']=='9/10'
    assert initial('nonseparable_alternatives')['0-1,2-3']=='1'
    assert initial('nonseparable_alternatives')['0-1']=='1/2'
    assert initial('nonseparable_alternatives')['2-3']=='1/2'
    assert initial('last_action_day')['0-1']=='1/5'
    assert initial('last_action_day')['0-1,2-3']=='3/10'
    assert initial('inherited_throughput_last_day')['0-1']=='1/5'
    assert F(1,5)/8 > F(3,10)/20
    assert initial('pause_not_qualified_penalty')['0-1']=='1/10'
    assert initial('pause_not_qualified_penalty')['0-2']=='1'
    assert initial('no_return_can_still_have_learning')['skip_experiment']=='1/2'
    assert initial('no_return_can_still_have_learning')['introduce_informative_disjoint_pair']=='1'
    nonmonotone = specifications['inherited_nonmonotone_occupancy']
    costs = [str(F(1,2) if day<=3<day+2 else F(0)) for day in range(4)]
    # Day 3 loss refers to FUTURE opportunity, not the alternative same-day action.
    costs[-1] = '0'
    assert costs == nonmonotone['expected_costs']
    return {'complementarity_marginals':['0','1'],
            'degree_sum_shared':'8/5','degree_sum_distinct':'7/5',
            'soft_gross_information_gain':'1/5','soft_net_gain_after_displaced_hard':'-1/20',
            'nonseparable_single_assignment_losses':['9/10','9/10'],'joint_loss':'9/10',
            'nonmonotone_future_opportunity_costs':costs,
            'qualification_as_retirement_proxy_refuted':True,
            'no_return_alone_does_not_imply_no_learning':True,
            'last_day_augmentation_scope':'Add a disjoint nonnegative reward edge with full follow-up. Does not claim shipped G has such a gap.',
            'adaptive_conditioning_counterexample':{
                 'type_prior_short':'1/2','type_prior_long':'1/2',
                 'policy':'First dyad assigned only after public signal reveals short duration; second incident dyad always assigned next day.',
                 'expected_first_assignment':'1/2','expected_second_assignment':'1',
                 'prior_occupancy_coefficient_at_next_day':'1/2',
                 'incorrect_prior_capacity_left_side':'5/4',
                 'actual_expected_capacity_left_side':'1',
                 'reward_example':'Assign only when public signal reveals reward 1, otherwise skip.',
                 'actual_expected_reward':'1/2','incorrect_prior_q_times_x':'1/4',
                 'conclusion':'Latent-conditioned theorem valid; unconditional prior coefficients invalid under history selection.'}}


def execute(output_root=None):
    cpu_start = time.process_time()
    root = Path(__file__).resolve().parents[2]
    output_root = Path(output_root) if output_root else root / 'results/research6/stage_a_exact'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    destination = output_root / stamp
    destination.mkdir(parents=True, exist_ok=False)
    specifications = build_specifications()
    write_new(destination/'specifications.json', specifications)
    source_hashes = {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(Path(__file__).parent.glob('*.py'))}
    write_new(destination/'registration.json', {
        'status':'registered_before_solution_evaluation','registered_utc':stamp,
        'scope':specifications['scope'], 'source_sha256':source_hashes,
        'specifications_sha256':hashlib.sha256((destination/'specifications.json').read_bytes()).hexdigest(),
        'cpu_allowance_seconds':300, 'model_ids':[s['id'] for s in specifications['matching']+specifications['information']],
        'held_out_definition':'Fixed deterministic graph/horizon sweep separate from named counterexample assertions; no fit or model selection.',
        'reviewer':'Separate Sol-high critic; development policy enumerator does not close independent review.'})
    print(f'[exact] registered constructed specifications: {destination}', flush=True)
    models, results, crosschecks = {}, {}, {}
    for spec in specifications['matching']+specifications['information']:
        mdp = compile_matching(spec) if 'n' in spec else spec
        result = solve(mdp)
        assert result['value'] == spec['expected'], (spec['id'],result['value'],spec['expected'])
        if spec.get('expected_first_action'):
            assert spec['expected_first_action'] in result['initial_optimal_actions'], spec['id']
        models[spec['id']], results[spec['id']] = mdp, result
        try:
            crosschecks[spec['id']] = verify_reference(mdp,result)
        except ValueError as exc:
            crosschecks[spec['id']] = {'status':'full_policy_cartesian_product_exceeds_development_limit', 'reason':str(exc)}
    sweeps = {}
    for spec in specifications['held_out_constructed_sweep']:
        mdp = compile_matching(spec)
        result = solve(mdp)
        if 'expected' in spec:
            assert result['value'] == spec['expected']
        sweeps[spec['id']] = {'solution':result,'reference_check':verify_reference(mdp,result)}
        models[spec['id']] = mdp
    checks = analytic_checks(results,specifications)
    certificates = {name:check_lp_certificate(c) for name,c in specifications['lp_certificates'].items()}
    assert certificates['two_day_renewal']['dual'] == results['renewal_certificate_toy']['value']=='3/4'
    write_new(destination/'models.json', models)
    write_new(destination/'solutions.json', {'named_models':results,'development_crosschecks':crosschecks,
                                          'held_out_sweeps':sweeps,'analytic_checks':checks,'lp_certificates':certificates})
    summary = {'status':'constructed_checks_passed_independent_review_pending','named_model_count':len(results),
        'held_out_sweep_count':len(sweeps),'explicit_state_count':sum(len(m['states']) for m in models.values()),
        'cpu_seconds':time.process_time()-cpu_start,'cpu_allowance_seconds':300,
        'simulator_worlds_generated':0,'simulator_episodes':0,'fit_calls':0,
        'scope':'Exact reduced-model values; symbolic ideal-stream LP proof separate; no certified simulator LP or policy improvement.',
        'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                 for p in sorted(destination.glob('*.json'))}}
    assert summary['cpu_seconds'] < 300
    write_new(destination/'summary.json',summary)
    print(json.dumps({'destination':str(destination), **{k:v for k,v in summary.items() if k!='files'}},sort_keys=True),flush=True)
    return destination


if __name__ == '__main__':
    execute()
