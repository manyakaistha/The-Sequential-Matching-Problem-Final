from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations
from research8.planner import Actor, EdgeLaw, Model, ReturnOutcome, ScenarioState
from research8.w2.public_rules import HARD, SOFT
from research8.w2.public_adapter import Projection


def request(n=4, phase='match', day=0, unknown=0):
    hard = dict(age_min=18, age_max=65, who_to_meet=['woman','man','non_binary'],
                relationship_structure='monogamous', smoking='no', partner_smoking='no_smoking',
                has_children=False, partner_children='any', wants_children='yes',
                acceptable_zones=['zone_a'], schedule=['weekend'])
    members = []
    for i in range(n):
        fields = dict(hard, **{k:'shared' for k in SOFT})
        status = {k:'observed' for k in HARD+SOFT}
        times = {k:0 for k in HARD+SOFT}
        if i < unknown:
            fields['age_min']=None;status['age_min']='not_asked';times['age_min']=None
        members.append(dict(member_id=f'm_{i:03}',pool_id='public_fixture',synthetic=True,
                            age=30,gender='woman',zone='zone_a',arrived_day=0,
                            fields=fields,field_status=status,field_observed_day=times,
                            source='constructed_public_fixture',available=True))
    state=dict(schema_version='1.0.0',synthetic=True,day=day,ask_budget_remaining=12,
               members=members,introductions=[],feedback=[],ask_log=[])
    return dict(schema_version='1.0.0',phase=phase,state=state,memory=None)


def absorbing(day, pair, q):
    outcomes=[]
    if q:outcomes.append(ReturnOutcome(q,(None,None),True))
    if q<1:outcomes.append(ReturnOutcome(1-q,(None,None),False))
    return EdgeLaw(day,pair,q,tuple(outcomes))


def waiting_projection(public):
    # Explicit finite fixture hypotheses, no hidden world/calendar access.
    names=tuple('ABCD');ids=tuple(m['member_id'] for m in public['state']['members'][:4])
    positive={(0,('A','B')):F(1,2),(1,('A','C')):F(2,5),(2,('A','D')):F(9,10)}
    laws=tuple(absorbing(d,pair,positive.get((d,pair),F(0)))
               for d in range(3) for pair in combinations(names,2))
    model=Model(tuple(Actor(a) for a in names),laws,end_day=2)
    return Projection(model,ScenarioState(0,names),tuple(zip(names,ids)))
