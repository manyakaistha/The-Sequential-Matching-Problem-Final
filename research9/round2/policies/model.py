"""Parametric expected-outcome scorer (PS) and the small adaptive drift policy (X1).

Both keep the supplied FIFO hard-bundle asks *exactly* (kit.baseline_asks), so any
difference from G comes from which legal pairs are introduced, never from asking.
Every parameter comes from an explicit prior file (theta):

* theta 'sim'  : constants transcribed from the simulator source (the R1-R8 practice)
* theta 'emp'  : estimated by fit_priors.py from observable training data only
* theta 'flat' : uninformative negative control

PS[theta]  : static model, greedy by predicted qualified probability (= X0 ablation)
X1[theta]  : PS + (a) recency-weighted MAP re-estimation of acceptance weights and
             (b) directional calibration: a windowed logit-offset MLE applied only in
             the direction the data supports and only beyond a 90% evidence margin.
Predictions for chosen pairs are written to memory['pred'] for calibration audit.
"""
import itertools
import math

from kit import SOFT, baseline_asks, eligibility

from ..oracle_value import gauss_hermite_normal, sigmoid

WEIGHTED = ('relationship_goal', 'relationship_pace', 'lifestyle', 'conversations')
GH9 = gauss_hermite_normal(9)
Z90 = 1.6448536269514722


def _pair(a, b):
    return tuple(sorted((a, b)))


def legal_edges(state):
    members = [m for m in state['members'] if m['available']]
    past = {_pair(i['user_a'], i['user_b']) for i in state['introductions']}
    out = []
    for a, b in itertools.combinations(members, 2):
        key = _pair(a['member_id'], b['member_id'])
        if key in past or eligibility(a, b)['status'] != 'feasible':
            continue
        score = sum(a['fields'].get(k) is not None and a['fields'].get(k) == b['fields'].get(k) for k in SOFT)
        out.append((key, a, b, score))
    return out


def response_moments(state, theta):
    """Beta posterior first/second moments of each member's response rate."""
    alpha0, beta0 = theta['response']['alpha'], theta['response']['beta']
    counts = {}
    for e in state['feedback']:
        if e['event'] in ('introduction_response', 'second_meeting_intention') and e['member_id']:
            c = counts.setdefault(e['member_id'], [0, 0])
            c[0 if e['value'] is not None else 1] += 1
    out = {}
    for ident, (s, f) in counts.items():
        a, b = alpha0 + s, beta0 + f
        out[ident] = (a / (a + b), a * (a + 1) / ((a + b) * (a + b + 1)))
    a, b = alpha0, beta0
    default = (a / (a + b), a * (a + 1) / ((a + b) * (a + b + 1)))
    return out, default


def features(fa, fb, theta):
    """Coded weighted-field agreement (+1 equal / -.5 unequal), expected value if unknown."""
    peq = theta['soft_equal_prob']
    phi, known_goal = [], None
    for k in WEIGHTED:
        va, vb = fa.get(k), fb.get(k)
        if va is not None and vb is not None:
            phi.append(1.0 if va == vb else -.5)
            if k == 'relationship_goal':
                known_goal = va == vb
        else:
            p = peq[k]
            phi.append(p - .5 * (1 - p))
    return phi, known_goal


class Model:
    """Marginal (attenuated) acceptance logit: eta = b0 + w.phi + offset, kappa-scaled."""

    def __init__(self, theta, b0=None, w=None, offset=0.0):
        acc = theta['accept']
        self.theta = theta
        self.kappa = math.sqrt(1 + math.pi * (acc['bias_sd'] ** 2) / 8)
        self.b0 = acc['intercept'] if b0 is None else b0
        self.w = [acc['weights'][k] for k in WEIGHTED] if w is None else list(w)
        self.offset = offset
        sec = theta['second']
        self.skappa = math.sqrt(1 + math.pi * (sec['bias_sd'] ** 2) / 8)

    def accept_logit(self, phi):
        return self.b0 + sum(w * x for w, x in zip(self.w, phi)) + self.offset

    def edge(self, fa, fb, ra, rb):
        """Return (p_mutual, p_date, p_msmi, p_accept_one) for one legal pair."""
        th = self.theta
        phi, known_goal = features(fa, fb, th)
        sec, date = th['second'], th['date']
        sd = th['accept']['shared_sd']
        p_goal = th['soft_equal_prob']['relationship_goal']
        branches = [(1.0, known_goal)] if known_goal is not None else [(p_goal, True), (1 - p_goal, False)]
        acc_pair = acc_one = both = 0.0
        for mass, goal in branches:
            phi_b = list(phi)
            phi_b[0] = 1.0 if goal else -.5
            z = self.accept_logit(phi_b)
            s = sec['intercept'] + sec['goal_coef'] * goal
            for x, wt in zip(*GH9):
                pa = sigmoid((z + sd * x) / self.kappa)
                ps = sigmoid((s + sd * x) / self.skappa)
                acc_one += mass * wt * pa
                acc_pair += mass * wt * pa * pa
                both += mass * wt * pa * pa * ps * ps
        p_mutual = ra[0] * rb[0] * acc_pair
        p_date = p_mutual * date['p_happen']
        p_msmi = ra[1] * rb[1] * date['p_happen'] * date['p_within30'] * sec['p_on_time'] ** 2 * both
        return p_mutual, p_date, p_msmi, acc_one


# ---------------------------------------------------------------- adaptation
def _observations(state, theta):
    """Released first responses (yes/no) with current public features."""
    members = {m['member_id']: m for m in state['members']}
    intros = {i['introduction_id']: i for i in state['introductions']}
    rows = []
    for e in state['feedback']:
        if e['event'] != 'introduction_response' or e['value'] not in ('yes', 'no'):
            continue
        intro = intros.get(e['introduction_id'])
        if intro is None:
            continue
        other = intro['user_b'] if e['member_id'] == intro['user_a'] else intro['user_a']
        if e['member_id'] not in members or other not in members:
            continue
        phi, _ = features(members[e['member_id']]['fields'], members[other]['fields'], theta)
        rows.append((intro['assigned_day'], phi, 1.0 if e['value'] == 'yes' else 0.0))
    return rows


def _solve(a, b):
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        if abs(m[c][c]) < 1e-12:
            return [0.0] * n
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                for k in range(c, n + 1):
                    m[r][k] -= f * m[c][k]
    return [m[i][n] / m[i][i] for i in range(n)]


def learn_weights(rows, today, model, half_life=14.0, prior_sd=0.5, iters=6):
    """Recency-weighted MAP logistic re-estimation of (b0, w) on the kappa scale."""
    k = model.kappa
    mu = [model.b0 / k] + [w / k for w in model.w]
    beta = mu[:]
    lam = 1 / prior_sd ** 2
    data = [(0.5 ** ((today - d) / half_life), [1.0] + phi, y) for d, phi, y in rows]
    for _ in range(iters):
        grad = [-lam * (b - m) for b, m in zip(beta, mu)]
        hess = [[(lam if i == j else 0.0) for j in range(5)] for i in range(5)]
        for wt, x, y in data:
            p = sigmoid(sum(bi * xi for bi, xi in zip(beta, x)))
            g = wt * (y - p)
            h = wt * p * (1 - p)
            for i in range(5):
                grad[i] += g * x[i]
                for j in range(5):
                    hess[i][j] += h * x[i] * x[j]
        step = _solve(hess, grad)
        beta = [b + s for b, s in zip(beta, step)]
    return beta[0] * k, [b * k for b in beta[1:]]


def directional_offset(rows, today, model, window=21, iters=8):
    """Windowed MLE of a common logit offset; returns (raw, se, applied)."""
    k = model.kappa
    recent = [((model.b0 + sum(w * x for w, x in zip(model.w, phi))) / k, y)
              for d, phi, y in rows if d >= today - window]
    if len(recent) < 8:
        return 0.0, float('inf'), 0.0
    delta = 0.0
    info = 1e-9
    for _ in range(iters):
        g = info = 0.0
        for l, y in recent:
            p = sigmoid(l + delta)
            g += y - p
            info += p * (1 - p)
        if info < 1e-9:
            break
        delta += max(-2.0, min(2.0, g / info))
    se = 1 / math.sqrt(max(info, 1e-9))
    applied = math.copysign(max(0.0, abs(delta) - Z90 * se), delta)
    return delta * k, se * k, applied * k


# ---------------------------------------------------------------- policies
def _rank(state, model, theta):
    moments, default = response_moments(state, theta)
    scored = []
    for key, a, b, soft in legal_edges(state):
        ra = moments.get(a['member_id'], default)
        rb = moments.get(b['member_id'], default)
        pm, pd, pq, pa = model.edge(a['fields'], b['fields'], ra, rb)
        scored.append((-pq, -soft, key, (pm, pd, pq, pa)))
    scored.sort()
    used, pairs, pred = set(), [], {}
    for _, _, key, p in scored:
        if not used.intersection(key):
            pairs.append(list(key))
            used.update(key)
            pred['|'.join(key)] = [round(v, 8) for v in p]
    return pairs, pred


def predict_pairs(state, pairs, theta):
    """Shadow predictions of a static PS[theta] for arbitrary pairs (host calibration audit)."""
    model = Model(theta)
    moments, default = response_moments(state, theta)
    by_id = {m['member_id']: m for m in state['members']}
    out = {}
    for a, b in pairs:
        key = _pair(a, b)
        p = model.edge(by_id[a]['fields'], by_id[b]['fields'], moments.get(a, default), moments.get(b, default))
        out['|'.join(key)] = [round(v, 8) for v in p]
    return out


def decide(request, config):
    """config: {'variant': 'PS'|'X1'|'X1_nocal'|'X1_nolearn'|'X1_oracle', 'theta': {...}, 'oracle_drift': [...]}"""
    state = request['state']
    memory = request.get('memory') or {}
    if request['phase'] == 'ask':
        return {'asks': baseline_asks(state), 'memory': memory}
    theta = config['theta']
    variant = config['variant']
    model = Model(theta)
    hist = memory.get('x1_hist', [])
    if variant in ('X1', 'X1_nocal', 'X1_nolearn'):
        rows = _observations(state, theta)
        if variant in ('X1', 'X1_nocal') and rows:
            b0, w = learn_weights(rows, state['day'], model)
            model = Model(theta, b0=b0, w=w)
        raw = se = applied = 0.0
        if variant in ('X1', 'X1_nolearn'):
            raw, se, applied = directional_offset(rows, state['day'], model)
            model.offset = applied
        hist = hist + [[state['day'], round(model.b0, 6), [round(x, 6) for x in model.w],
                        round(raw, 6), (round(se, 6) if math.isfinite(se) else None), round(applied, 6)]]
    elif variant == 'X1_oracle':
        offset = 0.0
        for start, value in config.get('oracle_drift', []):
            if state['day'] >= start:
                offset = value
        model.offset = offset
    elif variant != 'PS':
        raise ValueError('unknown model variant')
    pairs, pred = _rank(state, model, theta)
    memory = {'x1_hist': hist[-70:], 'pred': pred} if hist else {'pred': pred}
    return {'pairs': pairs, 'memory': memory}
