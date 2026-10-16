"""Vendored public-only protocol helpers; no simulator or generator imports."""

import itertools

VERSION = '1.0.0'

HARD = ['age_min','age_max','who_to_meet','relationship_structure','smoking',
        'partner_smoking','has_children','partner_children','wants_children',
        'acceptable_zones','schedule']

SOFT = ['relationship_goal','relationship_pace','lifestyle','conversations',
        'emotional_availability','space_for_relationship','relocate']

def eligibility(a,b):
    """Public pair-level hard checks only; availability is separately checked by simulator."""
    if a['member_id']==b['member_id']: return {'status':'infeasible','reasons':['same_member']}
    if a['pool_id']!=b['pool_id']: return {'status':'infeasible','reasons':['different_pool']}
    if min(a['age'],b['age'])<18: return {'status':'infeasible','reasons':['underage']}
    fa,fb=a['fields'],b['fields']; missing=[]; failures=[]
    for member,f in ((a,fa),(b,fb)):
        missing += [member['member_id']+':'+k for k in HARD if f.get(k) is None]
    for x,y,fx,fy in ((a,b,fa,fb),(b,a,fb,fa)):
        if fx.get('who_to_meet') is not None and y['gender'] not in fx['who_to_meet']: failures.append('who_to_meet')
        if fx.get('age_min') is not None and y['age']<fx['age_min']: failures.append('age')
        if fx.get('age_max') is not None and y['age']>fx['age_max']: failures.append('age')
        if fx.get('acceptable_zones') is not None and y['zone'] not in fx['acceptable_zones']: failures.append('geography')
        if fx.get('partner_smoking')=='no_smoking' and fy.get('smoking') in ('yes','occasionally'): failures.append('smoking')
        if fx.get('partner_children')=='no_children' and fy.get('has_children') is True: failures.append('children_present')
    if fa.get('relationship_structure') is not None and fb.get('relationship_structure') is not None and fa['relationship_structure']!=fb['relationship_structure']: failures.append('relationship_structure')
    if {fa.get('wants_children'),fb.get('wants_children')}=={'yes','no'}: failures.append('children_plans')
    if fa.get('schedule') is not None and fb.get('schedule') is not None and not set(fa['schedule'])&set(fb['schedule']): failures.append('schedule')
    return {'status':'infeasible' if failures else ('needs_clarification' if missing else 'feasible'),
            'reasons':sorted(set(failures)),'missing':missing}

def baseline_asks(state):
    eligible=[m for m in state['members'] if m['available'] and any(m['fields'][k] is None for k in HARD)
              and not any(m['field_status'][k]=='declined' for k in HARD)]
    return [{'member_id':m['member_id'],'field':'constraints'} for m in eligible[:state['ask_budget_remaining']//3]]

def baseline_match(state):
    members=[m for m in state['members'] if m['available']]
    past={tuple(sorted((i['user_a'],i['user_b']))) for i in state['introductions']}
    edges=[]
    for a,b in itertools.combinations(members,2):
        key=tuple(sorted((a['member_id'],b['member_id'])))
        if key in past or eligibility(a,b)['status']!='feasible':continue
        score=sum(a['fields'].get(k) is not None and a['fields'].get(k)==b['fields'].get(k) for k in SOFT)
        edges.append((-score,key))
    used=set();out=[]
    for _,pair in sorted(edges):
        if not used.intersection(pair):out.append(list(pair));used.update(pair)
    return out
