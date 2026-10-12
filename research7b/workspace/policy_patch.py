def eligibility(a, b):
    if a['member_id'] == b['member_id']: return {'status': 'infeasible', 'reasons': ['same_member']}
    if a['pool_id'] != b['pool_id']: return {'status': 'infeasible', 'reasons': ['different_pool']}
    if min(a['age'], b['age']) < 18: return {'status': 'infeasible', 'reasons': ['underage']}
    fa, fb = a['fields'], b['fields']
    missing = []
    for member, f in ((a, fa), (b, fb)):
        missing += [member['member_id'] + ':' + k for k in HARD if f.get(k) is None]
    for x, y, fx, fy in ((a, b, fa, fb), (b, a, fb, fa)):
        if fx.get('age_min') is not None and y['age'] < fx['age_min']: return {'status': 'infeasible'}
        if fx.get('age_max') is not None and y['age'] > fx['age_max']: return {'status': 'infeasible'}
        w = fx.get('who_to_meet')
        if w is not None and y['gender'] not in w: return {'status': 'infeasible'}
        if fx.get('relationship_structure') is not None and fy.get('relationship_structure') is not None and fx['relationship_structure'] != fy['relationship_structure']: return {'status': 'infeasible'}
        p_smoke = fx.get('partner_smoking')
        if p_smoke is not None and fy.get('smoking') is not None and p_smoke == 'no_smoking' and fy['smoking'] != 'no': return {'status': 'infeasible'}
        p_child = fx.get('partner_children')
        if p_child is not None and fy.get('has_children') is not None and p_child == 'no_children' and fy['has_children']: return {'status': 'infeasible'}
        wants = fx.get('wants_children')
        other_wants = fy.get('wants_children')
        if wants == 'yes' and other_wants == 'no': return {'status': 'infeasible'}
        if wants == 'no' and other_wants == 'yes': return {'status': 'infeasible'}
        zones = fx.get('acceptable_zones')
        if zones is not None and y['zone'] not in zones: return {'status': 'infeasible'}
        sch1 = fx.get('schedule')
        sch2 = fy.get('schedule')
        if sch1 is not None and sch2 is not None and not set(sch1).intersection(set(sch2)): return {'status': 'infeasible'}
    return {'status': 'feasible' if not missing else 'missing_hard', 'missing': missing}
