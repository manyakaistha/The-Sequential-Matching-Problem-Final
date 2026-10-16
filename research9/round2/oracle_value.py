"""Deterministic stdlib quadrature and the host-only Rao-Blackwellised outcome oracle.

oracle_expectations(...) returns, for one realised introduction, the exact
conditional expectations of mutual acceptance, completed date and qualified MSMI
given the hidden world truth and the assignment day. Because every introduction
decision is measurable before its outcome stream is drawn (kit.rand_for keyed on
seed|a|b|day), summing these expectations over the realised introductions is an
unbiased estimator of expected realised counts (tower property), with far lower
variance. It is a host-side evaluation device only and is never shown to policies.
"""
import math
from functools import lru_cache


@lru_cache(maxsize=8)
def gauss_hermite_normal(n=40):
    """Nodes/weights for E[f(Z)], Z~N(0,1); Newton on physicists' Hermite roots."""
    x = [0.0] * n
    w = [0.0] * n
    m = (n + 1) // 2
    z = 0.0
    pim4 = math.pi ** -0.25
    for i in range(m):
        if i == 0:
            z = math.sqrt(2 * n + 1) - 1.85575 * (2 * n + 1) ** (-1 / 6)
        elif i == 1:
            z -= 1.14 * n ** 0.426 / z
        elif i == 2:
            z = 1.86 * z - 0.86 * x[0]
        elif i == 3:
            z = 1.91 * z - 0.91 * x[1]
        else:
            z = 2.0 * z - x[i - 2]
        for _ in range(100):
            p1, p2 = pim4, 0.0
            for j in range(1, n + 1):
                p3 = p2
                p2 = p1
                p1 = z * math.sqrt(2.0 / j) * p2 - math.sqrt((j - 1) / j) * p3
            pp = math.sqrt(2.0 * n) * p2
            z1 = z
            z = z1 - p1 / pp
            if abs(z - z1) <= 1e-14:
                break
        x[i], x[n - 1 - i] = z, -z
        w[i] = w[n - 1 - i] = 2.0 / (pp * pp)
    nodes = tuple(xi * math.sqrt(2.0) for xi in x)
    weights = tuple(wi / math.sqrt(math.pi) for wi in w)
    return nodes, weights


def sigmoid(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


@lru_cache(maxsize=64)
def date_within_probability(delayed, extra_lo, extra_hi, window=30):
    """P(max(d1,d2)+U[1,14](+U[5,12] delayed)(+U[extra]) <= window), d~U[1,7]."""
    dist = {}
    for d1 in range(1, 8):
        for d2 in range(1, 8):
            k = max(d1, d2)
            dist[k] = dist.get(k, 0) + 1 / 49
    def convolve(dist, lo, hi):
        out = {}
        span = hi - lo + 1
        for k, p in dist.items():
            for u in range(lo, hi + 1):
                out[k + u] = out.get(k + u, 0) + p / span
        return out
    dist = convolve(dist, 1, 14)
    if delayed:
        dist = convolve(dist, 5, 12)
    if extra_lo is not None:
        dist = convolve(dist, extra_lo, extra_hi)
    return sum(p for k, p in dist.items() if k <= window)


def oracle_expectations(ma, mb, day, *, weights, drift_offset, rate_factor, date_prob,
                        second_delay_max, delayed, extra_delay):
    fa, fb = ma['truth'], mb['truth']
    fit = sum(w * (1 if fa[k] == fb[k] else -.5) for k, w in weights.items())
    za = -.25 + ma['bias'] + fit + drift_offset
    zb = -.25 + mb['bias'] + fit + drift_offset
    goal = .4 * (fa['relationship_goal'] == fb['relationship_goal'])
    sa = .15 + ma['second_bias'] + goal
    sb = .15 + mb['second_bias'] + goal
    ra = ma['response_rate'] * rate_factor
    rb = mb['response_rate'] * rate_factor
    nodes, wts = gauss_hermite_normal()
    acc = both = 0.0
    for x, w in zip(nodes, wts):
        s = .45 * x
        pa = sigmoid(za + s) * sigmoid(zb + s)
        acc += w * pa
        both += w * pa * sigmoid(sa + s) * sigmoid(sb + s)
    lo, hi = (extra_delay if extra_delay is not None else (None, None))
    h = date_within_probability(bool(delayed), lo, hi)
    on_time = min(1.0, 3 / second_delay_max)
    mutual = ra * rb * acc
    date = mutual * date_prob
    msmi = ra * rb * date_prob * h * (ra * rb) * on_time ** 2 * both
    return mutual, date, msmi
