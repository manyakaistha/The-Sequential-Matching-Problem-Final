"""Candidate H1: Released-history actor scorer (light).

Uses an explicit Beta shrinkage surrogate for each actor's probability of
recorded first-stage Yes by day 7.
- Prior: Beta(1, 1), prior_mean = 0.5.
- Target event: recorded first-stage Yes by day 7.
  Yes = 1; No or mature no-response = 0.
  Unresolved = not a trial.
- Deduplication: tracked by (introduction_id, member_id).
- Memory bounds: at most 10 mature first trials per actor, bounded aggregate totals.
- Episode reset: fully resets every episode (no cross-episode learning).
- Base dyad score from frozen P population scorer times (a_i * a_j) / (prior_mean^2),
  clipped to [0, 1].
- Allocation: descending modified weights greedily.
- Asks: baseline FIFO asks.
"""

from collections import defaultdict
import copy
import itertools
from typing import Any, Dict, List, Optional, Set, Tuple

from kit import SOFT, baseline_asks, eligibility

LAST_STATUS = {"fallback": False, "reason": None, "non_prior_actors": 0}


def extract_actor_trials(state: Dict[str, Any]) -> Dict[str, Tuple[int, int]]:
    """Extracts deduplicated mature first-response trials per actor.

    Returns dict mapping member_id -> (y_i, n_i) where:
      y_i = number of Yes outcomes
      n_i = total mature trials (Yes, No, or mature no_response)
    """
    feedback = state.get("feedback", [])
    # Track unique outcomes by (introduction_id, member_id)
    seen_trials = {}

    for event in feedback:
        if event.get("event") != "introduction_response":
            continue
        intro_id = event.get("introduction_id")
        member_id = event.get("member_id")
        if not intro_id or member_id is None:
            continue
        key = (intro_id, member_id)
        if key in seen_trials:
            continue

        val = event.get("value")
        missing = event.get("missing_reason")

        if val == "yes":
            seen_trials[key] = 1
        elif val == "no" or missing == "no_response":
            seen_trials[key] = 0
        # Otherwise unresolved: not a mature trial

    # Aggregate per member with cap of at most 10 trials per actor
    actor_trials = defaultdict(list)
    for (intro_id, member_id), outcome in seen_trials.items():
        if len(actor_trials[member_id]) < 10:
            actor_trials[member_id].append(outcome)

    summary = {}
    for member_id, outcomes in actor_trials.items():
        summary[member_id] = (sum(outcomes), len(outcomes))

    return summary


def get_actor_posterior_predictive(
    y_i: int,
    n_i: int,
    alpha: float = 1.0,
    beta: float = 1.0,
) -> float:
    """Computes posterior predictive probability: (alpha + y_i) / (alpha + beta + n_i)."""
    return (alpha + y_i) / (alpha + beta + n_i)


def compute_pair_score_h1(
    a: Dict[str, Any],
    b: Dict[str, Any],
    day: int,
    actor_trials: Dict[Any, Tuple[int, int]],
    alpha: float = 1.0,
    beta: float = 1.0,
) -> float:
    """Computes H1 surrogate score modifying P population score by actor history."""
    # 1. Base P score
    try:
        from research3.model_candidates import population
        base_q, _ = population(a, b, day)
        base_score = float(base_q)
    except Exception:
        # Fallback to soft matching count
        base_score = float(sum(
            a.get('fields', {}).get(k) is not None and
            a.get('fields', {}).get(k) == b.get('fields', {}).get(k)
            for k in SOFT
        ))

    # 2. Actor shrinkage predictions
    prior_mean = alpha / (alpha + beta)
    y_a, n_a = actor_trials.get(a.get("member_id"), (0, 0))
    y_b, n_b = actor_trials.get(b.get("member_id"), (0, 0))

    pred_a = get_actor_posterior_predictive(y_a, n_a, alpha, beta)
    pred_b = get_actor_posterior_predictive(y_b, n_b, alpha, beta)

    multiplier = (pred_a * pred_b) / (prior_mean * prior_mean)
    modified = base_score * multiplier

    # Clip to [0, 1] if base_score is a probability in [0, 1]
    if 0.0 <= base_score <= 1.0:
        return max(0.0, min(1.0, modified))
    return max(0.0, modified)


def decide_h1_match(
    state: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> Tuple[List[List[Any]], Dict[str, Any]]:
    """Greedy matching using H1 history-adjusted weights."""
    alpha = float(config.get("alpha", 1.0)) if config else 1.0
    beta = float(config.get("beta", 1.0)) if config else 1.0

    actor_trials = extract_actor_trials(state)
    active = [m for m in state.get('members', []) if m.get('available')]
    past = {
        tuple(sorted((i['user_a'], i['user_b'])))
        for i in state.get('introductions', [])
    }
    day = state.get('day', 0)

    scores = {}
    for a, b in itertools.combinations(active, 2):
        pair = tuple(sorted((a['member_id'], b['member_id'])))
        if pair not in past and eligibility(a, b).get('status') == 'feasible':
            scores[pair] = compute_pair_score_h1(a, b, day, actor_trials, alpha, beta)

    if not scores:
        return [], {"edges": 0, "non_prior_actors": len(actor_trials)}

    # Greedy allocation descending by modified score, breaking ties by canonical pair
    sorted_pairs = sorted(scores.keys(), key=lambda p: (-scores[p], p[0], p[1]))
    used = set()
    pairs = []
    for u, v in sorted_pairs:
        if u not in used and v not in used:
            used.add(u)
            used.add(v)
            pairs.append([u, v])

    return sorted(pairs), {"edges": len(scores), "non_prior_actors": len(actor_trials)}


def decide(request: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    global LAST_STATUS
    LAST_STATUS = {"fallback": False, "reason": None, "non_prior_actors": 0}

    phase = request.get("phase", "ask")
    state = request.get("state", {})
    memory = request.get("memory")

    # Reset memory on day 0 or if None
    if memory is None or state.get("day", 0) == 0:
        memory = {}

    if phase == "ask":
        asks = baseline_asks(state)
        return {"asks": asks, "memory": memory}
    else:
        try:
            pairs, info = decide_h1_match(state, config)
            LAST_STATUS = {
                "fallback": False,
                "reason": None,
                "non_prior_actors": info.get("non_prior_actors", 0),
            }
            return {"pairs": pairs, "memory": memory}
        except Exception as exc:
            LAST_STATUS = {"fallback": True, "reason": str(exc), "non_prior_actors": 0}
            from kit import baseline_match
            return {"pairs": baseline_match(state), "memory": memory}
