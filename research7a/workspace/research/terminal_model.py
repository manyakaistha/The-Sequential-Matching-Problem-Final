"""Observation-only funnel model; public mechanism priors are explicit assumptions.

Missing equality indicators are enumerated exactly. Gaussian logistic integrals use
five-point Gauss-Hermite quadrature, never sigmoid(E[feature]). Actor posteriors and
regime learning are approximate, so predictions require external calibration audits.
"""
import functools
import itertools
import math

FEATURES = ('relationship_goal', 'relationship_pace', 'lifestyle', 'conversations')
CARDINALITY = (2, 3, 3, 4)
REGIMES = ((.7, .4, .25, .2, 0.), (.25, .8, -.25, .5, 0.),
           (.7, .4, .25, .2, -.5))
# Standard-normal quadrature (weights sum to one).
NODES = (-2.8569700139, -1.35562618, 0., 1.35562618, 2.8569700139)
WEIGHTS = (.0112574113, .2220759220, .5333333334, .2220759220, .0112574113)
_RESPONSE_CONCENTRATION = .765*.235/((.98-.55)**2/12)-1
PRIOR_RESPONSE = (.765 * _RESPONSE_CONCENTRATION, .235 * _RESPONSE_CONCENTRATION)

def _lag_distribution(delayed):
    counts = {}
    for a,b,gap in itertools.product(range(1,8),range(1,8),range(1,15)):
        for extra in (range(5,13) if delayed else (0,)):
            lag=max(a,b)+gap+extra
            counts[lag]=counts.get(lag,0)+1
    denominator=sum(counts.values())
    return {lag:n/denominator for lag,n in counts.items()}
LAG_DISTRIBUTIONS=(_lag_distribution(False),_lag_distribution(True))


def sigmoid(x):
    return 1. / (1. + math.exp(-max(-35., min(35., x))))


def equality_probabilities(a, b):
    out = []
    for field, size in zip(FEATURES, CARDINALITY):
        u, v = a['fields'].get(field), b['fields'].get(field)
        out.append(float(u == v) if u is not None and v is not None else 1. / size)
    return tuple(out)


def user(memory, ident):
    # response successes/failures, acceptance mean/precision, second mean/precision
    return memory.get('users', {}).get(ident, [0., 0., 0., 1/.49, 0., 4.])


def response_moments(u):
    a, b = PRIOR_RESPONSE[0] + u[0], PRIOR_RESPONSE[1] + u[1]
    return a/(a+b), a*(a+1)/((a+b)*(a+b+1))


def regime_weights(memory):
    logits = memory.get('regime_logweights', [0., 0., 0.])
    vals = [math.exp(max(-30., x-max(logits))) for x in logits]
    return tuple(v/sum(vals) for v in vals)


@functools.lru_cache(maxsize=18000)
def logistic_integral(z, variance):
    scale = math.sqrt(max(0., variance))
    return sum(w*sigmoid(z+scale*x) for x,w in zip(NODES,WEIGHTS))


@functools.lru_cache(maxsize=12000)
def integrated(equal, ua, ub, day, regime, shared=True):
    """Return marginal acceptances, joint accept, second joint, full joint.

    Integrating independent actor effects conditional on common S preserves shared
    acceptance/second-stage dependence; distinct actor biases are independent priors.
    """
    wa = REGIMES[regime]
    drift = wa[4] if day >= 35 else 0.
    a_mean, a_var, s_mean, s_var = ua
    b_mean, b_var, t_mean, t_var = ub
    total = [0.] * 9
    uncertain = [i for i,p in enumerate(equal) if 0. < p < 1.]
    states = itertools.product((0.,1.), repeat=len(uncertain))
    for bits in states:
        eq = list(equal); prob = 1.
        for i, bit in zip(uncertain,bits):
            prob *= equal[i] if bit else 1-equal[i]; eq[i] = bit
        fit = -.25 + sum(w*(1 if e else -.5) for w,e in zip(wa[:4],eq)) + drift
        sec = .15 + .4*eq[0]
        for x,weight in zip(NODES if shared else (0.,), WEIGHTS if shared else (1.,)):
            common = .45*x
            extra_variance = 0. if shared else .45**2
            pa = logistic_integral(fit+a_mean+common,a_var+extra_variance)
            pb = logistic_integral(fit+b_mean+common,b_var+extra_variance)
            sa = logistic_integral(sec+s_mean+common,s_var+extra_variance)
            sb = logistic_integral(sec+t_mean+common,t_var+extra_variance)
            mass = prob*weight
            for j,v in enumerate((pa,pb,pa*pb,sa*sb,pa*pb*sa*sb,sa,sb,pa*pb*sa,pa*pb*sb)):
                total[j] += mass*v
    return tuple(total)


def actor_tuple(u, learning=True):
    if not learning: return (0., .49, 0., .25)
    return (round(u[2],5), round(1/u[3],5), round(u[4],5), round(1/u[5],5))


def predict_from_equal(equal, ids, day, memory, cfg):
    us = [user(memory,i) for i in ids]
    moments = [response_moments(u) for u in us]
    mean_product = moments[0][0]*moments[1][0]
    squared_product = moments[0][1]*moments[1][1]
    weights = regime_weights(memory) if cfg.get('regime',True) else (1.,0.,0.)
    vals = [integrated(tuple(equal),actor_tuple(us[0],cfg.get('learning',True)),
                       actor_tuple(us[1],cfg.get('learning',True)),day,r,
                       cfg.get('model') != 'independent') for r in range(3)]
    joined = tuple(sum(weights[r]*vals[r][j] for r in range(3)) for j in range(9))
    date_p = memory.get('date_counts',[7.8,2.2]); date_p = date_p[0]/sum(date_p)
    # Delayed-regime detection uses observed date lags, without scenario labels.
    lag_logits=memory.get('date_logweights',[math.log(5.),0.])
    delay_weight=1/(1+math.exp(max(-30.,min(30.,lag_logits[0]-lag_logits[1]))))
    on_time = 1.-delay_weight*(120/5488)
    response_a,response_b = moments[0][0], moments[1][0]
    pause = date_p*squared_product*joined[4]
    terminal = .36*on_time*pause
    result = dict(both_response=mean_product, both_accept_unconditional=mean_product*joined[2],
                date_unconditional=date_p*mean_product*joined[2],
                both_second_yes_unconditional=pause, terminal=terminal, pause=pause,
                response_a=response_a,response_b=response_b,
                accept_a=joined[0],accept_b=joined[1], second_a=joined[5],second_b=joined[6],
                second_a_given_mutual=joined[7]/max(1e-9,joined[2]),
                second_b_given_mutual=joined[8]/max(1e-9,joined[2]),
                both_accept_independent=mean_product*joined[0]*joined[1],
                terminal_independent=.36*on_time*date_p*squared_product*joined[0]*joined[1]*joined[5]*joined[6],
                date_conditional=date_p,
                both_accept_conditional=joined[2], deadline_conditional=.36*on_time)
    if cfg.get('model') == 'simple':
        counts=memory.get('simple_funnel',[[11.7,8.3],[3.6,16.4],[2.8,17.2],[.65,19.35],[.234,19.766]])
        probabilities=[a/(a+b) for a,b in counts]
        for k,p in zip(('both_response','both_accept_unconditional','date_unconditional','both_second_yes_unconditional','terminal'), probabilities): result[k]=p
        result['pause']=result['both_second_yes_unconditional']
    return result


def predict_funnel(a, b, state, memory, cfg):
    return predict_from_equal(equality_probabilities(a,b),(a['member_id'],b['member_id']),
                              state['day'],memory,cfg)


def update_memory(state, old, cfg):
    memory = old if isinstance(old,dict) and old.get('version') == 2 else {}
    memory.setdefault('version',2); memory.setdefault('users',{})
    memory.setdefault('snapshots',{}); memory.setdefault('seen',[])
    memory.setdefault('regime_seen',[]); memory.setdefault('regime_logweights',[0.,0.,0.])
    memory.setdefault('date_counts',[7.8,2.2]); memory.setdefault('date_lags',[0.,0.]); memory.setdefault('date_logweights',[math.log(5.),0.])
    memory.setdefault('simple_counts',[2.,6.,2.,6.,1.,9.])
    memory.setdefault('simple_funnel',[[11.7,8.3],[3.6,16.4],[2.8,17.2],[.65,19.35],[.234,19.766]])
    if not cfg.get('learning',True): return memory
    seen=set(memory['seen']); regime_seen=set(memory['regime_seen'])
    introductions={i['introduction_id']:i for i in state.get('introductions',[])}
    grouped={}
    for event in state.get('feedback',[]): grouped.setdefault(event['introduction_id'],[]).append(event)
    for mid, events in grouped.items():
        intro=introductions.get(mid)
        if not intro: continue
        ids=(intro['user_a'],intro['user_b'])
        key='|'.join(sorted(ids))+':'+str(intro['assigned_day'])
        snap=memory['snapshots'].get(key)
        for e in events:
            token=mid+':'+str(e.get('member_id'))+':'+e['event']
            if token in seen: continue
            seen.add(token)
            stage=e['event']; value=e.get('value')
            if stage=='date_happened':
                memory['date_counts'][0 if value is True else 1]+=1
                lag=e['occurred_day']-intro['assigned_day']
                memory['date_lags'][0]+=lag>21; memory['date_lags'][1]+=1
                for r in range(2): memory['date_logweights'][r]+=math.log(max(1e-12,LAG_DISTRIBUTIONS[r].get(lag,0.)))
            if stage not in ('introduction_response','second_meeting_intention'): continue
            actor=e.get('member_id'); u=memory['users'].setdefault(actor,[0.,0.,0.,1/.49,0.,4.])
            # Only explicit no-response increments failure; pending is not an event.
            u[0 if value is not None else 1]+=1
            if value is None or not snap or not cfg.get('learning',True): continue
            p=snap['pred']['accept_a' if actor==snap['users'][0] else 'accept_b'] if stage=='introduction_response' else snap['pred'].get('second_a_given_mutual' if actor==snap['users'][0] else 'second_b_given_mutual',.6)
            index=2 if stage=='introduction_response' else 4
            u[index+1]+=p*(1-p); u[index]+=((value=='yes')-p)/u[index+1]
            u[index]=max(-2.5,min(2.5,u[index]))
        responses=[e for e in events if e['event']=='introduction_response']
        if len(responses)==2 and mid not in regime_seen and snap:
            regime_seen.add(mid)
            yes=[e['value']=='yes' for e in sorted(responses,key=lambda e:ids.index(e['member_id']))]
            if all(e['value'] is not None for e in responses):
                for r in range(3):
                    vals=integrated(tuple(snap['equal']),(0.,.49,0.,.25),(0.,.49,0.,.25),snap['day'],r,True)
                    pa,pb,joint=vals[:3]
                    likelihood=joint if all(yes) else pa-joint if yes[0] else pb-joint if yes[1] else 1-pa-pb+joint
                    # Temper correlated, selected and heterogeneous observations.
                    memory['regime_logweights'][r]+=.35*math.log(max(1e-8,likelihood))
            memory['simple_counts'][0 if all(yes) else 1]+=1
        seconds=[e for e in events if e['event']=='second_meeting_intention']
        dates=[e for e in events if e['event']=='date_happened']
        finalized=(len(responses)==2 and not all(e['value']=='yes' for e in responses)) or (dates and dates[0]['value'] is False) or len(seconds)==2
        final_token=mid+':funnel_final'
        if finalized and state['day']-intro['assigned_day']>=38 and final_token not in seen:
            seen.add(final_token)
            outcomes=[all(e['value'] is not None for e in responses),all(e['value']=='yes' for e in responses),bool(dates and dates[0]['value']),len(seconds)==2 and all(e['value']=='yes' for e in seconds)]
            outcomes.append(outcomes[3] and dates[0]['occurred_day']-intro['assigned_day']<=30 and all(e.get('occurred_day') is not None and e['occurred_day']-dates[0]['occurred_day']<=3 for e in seconds))
            for counts,outcome in zip(memory['simple_funnel'],outcomes): counts[0 if outcome else 1]+=1
        terminal_token=mid+':second_joint'
        if len(seconds)==2 and terminal_token not in seen:
            seen.add(terminal_token)
            memory['simple_counts'][2 if all(e['value']=='yes' for e in seconds) else 3]+=1
    memory['seen']=sorted(seen)[-6500:];memory['regime_seen']=sorted(regime_seen)[-1500:]
    if len(memory['snapshots'])>700:
        order=sorted(memory['snapshots'],key=lambda k:memory['snapshots'][k]['day'])
        for key in order[:-700]: del memory['snapshots'][key]
    return memory
