"""Targeted and randomized soft-budget filling rules for Research 8.

Governed by research8/soft_query_trial experiment specification:
- Candidate set C: eligible soft questions (u, k) with direct comparison opportunity
  (at least one currently legal, available, nonhistorical neighbor whose field k is observed).
- Priority 1: u has >= 2 such legal neighbors with observed k, and their answers differ.
- Priority 2: remaining candidates with >= 1 such neighbor.
- Tie-breaking:
    a. Number of legal neighbors with observed k, descending
    b. Current legal degree of u, descending
    c. Field name and opaque member identifier, deterministic ascending order
- Random filling:
    Reproducible shuffle of C using SHA256(f"{salt}|{day}") seed.
"""

import hashlib
import itertools
import random
from typing import Any, Dict, List, Set, Tuple

from kit import HARD, SOFT, eligibility

SOFT_FIELDS: Tuple[str, ...] = tuple(SOFT)
RANDOM_POLICY_SALT: str = "research8_g_random_soft_v1"


def build_legal_graph(state: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]], Set[Tuple[str, str]]]:
    """Construct the currently legal, available, nonhistorical dyad graph.

    Returns:
        available_members: List of member dicts who are currently available.
        legal_neighbors: Map from member_id to list of legal neighbor member_ids.
        past_introductions: Set of historical introduced pairs (sorted tuple of two member_ids).
    """
    available_members = [m for m in state.get("members", []) if m.get("available")]
    past_introductions = {
        tuple(sorted((intro["user_a"], intro["user_b"])))
        for intro in state.get("introductions", [])
    }
    legal_neighbors: Dict[str, List[str]] = {m["member_id"]: [] for m in available_members}

    for a, b in itertools.combinations(available_members, 2):
        pair_key = tuple(sorted((a["member_id"], b["member_id"])))
        if pair_key in past_introductions:
            continue
        if eligibility(a, b)["status"] != "feasible":
            continue
        legal_neighbors[a["member_id"]].append(b["member_id"])
        legal_neighbors[b["member_id"]].append(a["member_id"])

    # Keep neighbor lists sorted by opaque identifier for deterministic graph traversal
    for u in legal_neighbors:
        legal_neighbors[u].sort()

    return available_members, legal_neighbors, past_introductions


def extract_candidate_set(
    available_members: List[Dict[str, Any]],
    legal_neighbors: Dict[str, List[str]],
) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Extract candidate set C of eligible soft questions with direct comparison opportunity.

    A question (u, k) is in C iff:
    1. Member u is currently available.
    2. Field k is in SOFT.
    3. u's field_status[k] == 'not_asked' and u's fields[k] is None (unknown).
    4. Direct comparison opportunity exists: u has at least one legal neighbor v in the
       current dyad graph whose field k is already observed (field_status[k] == 'observed'
       and fields[k] is not None).

    Returns:
        Map of (u, k) -> candidate_metadata:
            - member_id: u
            - field: k
            - priority: 1 if >=2 neighbors with differing answers, else 2
            - n_obs: count of legal neighbors with observed k
            - deg_u: current legal degree of u in dyad graph
            - distinct_values: tuple of distinct observed values among neighbors
    """
    members_by_id = {m["member_id"]: m for m in available_members}
    candidates: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for m in available_members:
        u = m["member_id"]
        fields = m.get("fields", {})
        status = m.get("field_status", {})
        neighbors = legal_neighbors.get(u, [])
        deg_u = len(neighbors)

        for k in SOFT_FIELDS:
            # Must be not_asked and value unknown
            if status.get(k) != "not_asked" or fields.get(k) is not None:
                continue

            # Identify legal neighbors whose field k is already observed
            observed_neighbors = [
                v
                for v in neighbors
                if members_by_id[v].get("field_status", {}).get(k) == "observed"
                and members_by_id[v].get("fields", {}).get(k) is not None
            ]

            n_obs = len(observed_neighbors)
            if n_obs < 1:
                # No direct comparison opportunity
                continue

            observed_values = {members_by_id[v]["fields"][k] for v in observed_neighbors}

            # Priority rule:
            # Priority 1: >= 2 such legal neighbors and their observed answers differ
            # Priority 2: remaining questions with >= 1 such neighbor
            if n_obs >= 2 and len(observed_values) >= 2:
                priority = 1
            else:
                priority = 2

            candidates[(u, k)] = {
                "member_id": u,
                "field": k,
                "priority": priority,
                "n_obs": n_obs,
                "deg_u": deg_u,
                "distinct_values": tuple(sorted(str(val) for val in observed_values)),
            }

    return candidates


def rank_targeted_candidates(candidates: Dict[Tuple[str, str], Dict[str, Any]]) -> List[Tuple[str, str]]:
    """Rank candidate set C using the frozen targeted selection rule.

    Order:
    1. Priority group: 1 (diff answers) before 2
    2. n_obs: descending
    3. deg_u: descending
    4. field: alphabetical ascending
    5. member_id: opaque string ascending
    """
    def sort_key(item: Tuple[Tuple[str, str], Dict[str, Any]]):
        meta = item[1]
        return (
            meta["priority"],
            -meta["n_obs"],
            -meta["deg_u"],
            meta["field"],
            meta["member_id"],
        )

    sorted_items = sorted(candidates.items(), key=sort_key)
    return [key for key, _ in sorted_items]


def select_targeted_soft_asks(
    state: Dict[str, Any],
    remaining_budget: int,
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """Select up to remaining_budget soft questions using the targeted rule.

    Returns:
        (soft_asks, telemetry)
    """
    if remaining_budget <= 0:
        return [], {"candidate_count": 0, "selected_count": 0, "remaining_budget": remaining_budget}

    available_members, legal_neighbors, _ = build_legal_graph(state)
    candidates = extract_candidate_set(available_members, legal_neighbors)
    ranked = rank_targeted_candidates(candidates)

    selected = ranked[:remaining_budget]
    soft_asks = [{"member_id": u, "field": k} for u, k in selected]

    telemetry = {
        "candidate_count": len(candidates),
        "selected_count": len(soft_asks),
        "remaining_budget": remaining_budget,
        "selected_keys": [[u, k] for u, k in selected],
    }
    return soft_asks, telemetry


def select_random_soft_asks(
    state: Dict[str, Any],
    remaining_budget: int,
    salt: str = RANDOM_POLICY_SALT,
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """Select up to remaining_budget soft questions by random sampling from candidate set C.

    Uses an explicit reproducible policy RNG recipe based on registered salt and public day.
    Sampling is without replacement from the exact same candidate set C.

    Returns:
        (soft_asks, telemetry)
    """
    if remaining_budget <= 0:
        return [], {
            "candidate_count": 0,
            "selected_count": 0,
            "remaining_budget": remaining_budget,
            "rng_recipe": "sha256(salt|day)",
        }

    available_members, legal_neighbors, _ = build_legal_graph(state)
    candidates = extract_candidate_set(available_members, legal_neighbors)

    day = int(state.get("day", 0))
    h = hashlib.sha256(f"{salt}|{day}".encode("utf-8")).digest()
    rng_seed = int.from_bytes(h[:8], "big")

    if not candidates:
        return [], {
            "candidate_count": 0,
            "selected_count": 0,
            "remaining_budget": remaining_budget,
            "rng_recipe": f"sha256({salt}|{day})",
            "rng_seed_int": rng_seed,
        }

    # Deterministic canonical sort of candidates before shuffling
    canonical_candidates = sorted(candidates.keys(), key=lambda c: (c[1], c[0]))

    rng = random.Random(rng_seed)
    shuffled = list(canonical_candidates)
    rng.shuffle(shuffled)
    selected = shuffled[:remaining_budget]
    soft_asks = [{"member_id": u, "field": k} for u, k in selected]

    telemetry = {
        "candidate_count": len(candidates),
        "selected_count": len(soft_asks),
        "remaining_budget": remaining_budget,
        "rng_recipe": f"sha256({salt}|{day})",
        "rng_seed_int": rng_seed,
        "selected_keys": [[u, k] for u, k in selected],
    }
    return soft_asks, telemetry
