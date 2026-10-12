"""Observation-only candidate scores; no file/network/world access at inference.

The caller owns legality, querying, allocation, and resource guards. score_edges
accepts legal member-ID pairs and returns unsorted (weight, canonical_pair) rows.
None of the scores claims full dynamic optimality.
"""
import collections
import math
from research.terminal_model import (FEATURES, equality_probabilities, integrated,
                                     PRIOR_RESPONSE)

CANDIDATES = {
    'public_weight': {'objective': 'regime-robust soft ranking', 'learning': 'none', 'complexity': 'O(E)', 'fallback': 'canonical'},
    'population': {'objective': 'public-prior terminal probability', 'learning': 'none', 'complexity': 'O(E), cached finite equality states', 'fallback': 'canonical'},
    'scarce': {'objective': 'match low-degree endpoints first', 'learning': 'none', 'complexity': 'O(E)', 'fallback': 'canonical'},
    'response': {'objective': 'population terminal times actor response second moments', 'learning': 'Beta shrinkage from resolved public response events', 'complexity': 'O(E+H)', 'fallback': 'canonical'},
    'throughput': {'objective': 'population expected terminal reward / expected busy duration', 'learning': 'none', 'complexity': 'O(E)', 'fallback': 'canonical'},
    'offline': {'objective': 'regularized direct terminal score fitted only on old seed-separated snapshots', 'learning': 'offline fixed coefficients', 'complexity': 'O(E)', 'fallback': 'canonical'},
}

# Populated by tiny_models.py from previously examined seeds 1001--1005 only.
# Features: intercept, four equality probabilities centered at generator priors,
# post-day35 indicator. Validation seeds 1006--1008 never fit coefficients.
OFFLINE_WEIGHTS = (-4.4951144034601525, 0.06971259815380544, 0.08371633600294244, -0.0454263648284883, -0.013228700815476958, -0.04053548205036358)

def sigmoid(x):
    return 1 / (1 + math.exp(-max(-35., min(35., x))))

def features(a, b, day):
    eq = equality_probabilities(a, b)
    return (1., eq[0]-.5, eq[1]-1/3, eq[2]-1/3, eq[3]-.25, float(day >= 35))

def population(a, b, day):
    """Known population prior, unknown regime and actor effects integrated.

    Regime mixture is 5/6 development weights, 1/6 shifted weights. Only one
    of six families drifts; mixture split places 1/6 on the drifting regime.
    Missing equality indicators are enumerated, and common S is retained.
    Five-point Gaussian quadrature is inherited, numerically approximate.
    """
    eq = equality_probabilities(a, b)
    vals = [integrated(eq, (0., .49, 0., .25), (0., .49, 0., .25), day, r)
            for r in range(3)]
    # Delayed family uses normal preferences; couple its deadline factor to
    # that normal-regime joint instead of multiplying marginal mixtures.
    joint = ((3+671/686)/6)*vals[0][4] + vals[1][4]/6 + vals[2][4]/6
    mutual = .765**2*sum(w*v[2] for w,v in zip((4/6, 1/6, 1/6), vals))
    second_moment = (.55**2+.55*.98+.98**2)/3
    q = .78*.36*second_moment**2*joint
    return q, mutual

def response_counts(state):
    counts = collections.defaultdict(lambda: [0, 0])
    for event in state.get('feedback', ()):
        if event.get('event') in ('introduction_response', 'second_meeting_intention'):
            ident = event.get('member_id')
            if ident:
                counts[ident][0 if event.get('value') is not None else 1] += 1
    return counts

def response_second(counts):
    a, b = PRIOR_RESPONSE[0]+counts[0], PRIOR_RESPONSE[1]+counts[1]
    return a*(a+1)/((a+b)*(a+b+1))

def score_edge(a, b, state, mode='public_weight', memory=None):
    if mode == 'public_weight':
        eq = equality_probabilities(a, b)
        # Three features have strictly positive weights in every public regime;
        # lifestyle is omitted because its sign changes. Extra goal weight also
        # reflects its positive effect on second intentions.
        return 1.0*eq[0]+.55*eq[1]+.25*eq[3]
    if mode == 'offline':
        if len(OFFLINE_WEIGHTS) != 6:
            raise ValueError('offline coefficients not frozen')
        return sigmoid(sum(w*x for w,x in zip(OFFLINE_WEIGHTS,features(a,b,state['day']))))
    q, mutual = population(a,b,state['day'])
    if mode == 'population':
        return q
    if mode == 'response':
        counts = (memory or {}).get('response_counts')
        if counts is None:
            counts = response_counts(state)
        second = (.55**2+.55*.98+.98**2)/3
        return q * response_second(counts.get(a['member_id'],(0,0))) * response_second(counts.get(b['member_id'],(0,0))) / second**2
    if mode == 'throughput':
        # Failed introductions occupy 8 days; mutual accepts occupy lag+6.
        # Expected delay mixture is public prior; family remains unobserved.
        normal = integrated(equality_probabilities(a,b), (0.,.49,0.,.25),
                            (0.,.49,0.,.25),state['day'],0)[2]*.765**2
        duration = 8 + mutual*10.642857142857142 + normal*8.5/6
        return q/duration
    raise ValueError('unknown score mode: '+str(mode))

def score_edges(state, edges, mode='public_weight', memory=None):
    by_id = {m['member_id']: m for m in state.get('members', ())}
    pairs = sorted(set(tuple(sorted(pair)) for pair in edges))
    if mode == 'scarce':
        degree = collections.Counter(i for pair in pairs for i in pair)
        # Prefer an edge involving a scarce node; degree sum resolves equal min.
        # These scales are integer lexicographic encodings on <=200 members.
        n = max(1, len(by_id))
        return [(1+(n-min(degree[i] for i in pair))*(2*n+1)+(2*n-sum(degree[i] for i in pair)), pair) for pair in pairs]
    if mode == 'response':
        memory = dict(memory or {}, response_counts=response_counts(state))
    return [(score_edge(by_id[pair[0]],by_id[pair[1]],state,mode,memory),pair) for pair in pairs]
