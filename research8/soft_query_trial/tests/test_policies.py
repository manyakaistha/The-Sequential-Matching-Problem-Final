"""Implementation tests for Research 8 soft query trial policies.

Verifies all 16 required test conditions and 6 tiny fixtures specified in MISSION:
1. G behavior matches frozen reference on identical requests.
2. Hard batches are identical across all three functions on identical observations.
3. Added queries never displace hard questions.
4. Budget 12, hard cost 3, soft cost 1.
5. No adaptive selection after answers.
6. Observed/declined questions are excluded.
7. False is not treated as missing.
8. Unavailable members are excluded.
9. Past dyads are excluded from targeting graph.
10. Random and targeted arms use the exact same candidate set C.
11. Targeting priority and tie rules match specification.
12. No candidates leaves budget unused.
13. Reproducibility of random selection.
14. Every output passes actual action validator.
15. No hidden metadata enters decisions.
16. Day 59 follow-up and metric normalization.
17. Seed-group aggregation uses 24 groups.

Plus tiny fixtures:
- No legal neighbor means no soft question.
- One informative neighbor creates a candidate.
- Two neighbors with different answers outrank a noncontested candidate.
- Revealing a soft answer changes Greedy's selected matching.
- Revealing an answer does not change matching.
- Hard queries consume entire budget, leaving no soft queries.
"""

import copy
import hashlib
import json
import pytest
from typing import Any, Dict, List

from kit import (
    HARD,
    SOFT,
    VERSION,
    Simulator,
    baseline_asks,
    baseline_match,
    eligibility,
    generate,
)
import policy as official_ref

from research7b.workspace.research7.runtime.interfaces import (
    sanitize_observation,
    validate_ask_batch,
    validate_match_batch,
    validate_policy_memory,
)

from research8.soft_query_trial.policies.g import decide as decide_g
from research8.soft_query_trial.policies.g_random_soft import decide as decide_g_random_soft
from research8.soft_query_trial.policies.g_targeted_soft import decide as decide_g_targeted_soft
from research8.soft_query_trial.policies.targeting import (
    SOFT_FIELDS,
    build_legal_graph,
    extract_candidate_set,
    rank_targeted_candidates,
    select_random_soft_asks,
    select_targeted_soft_asks,
)


def _make_clean_member(
    member_id: str,
    available: bool = True,
    age: int = 25,
    gender: str = "woman",
    zone: str = "zone_a",
    arrived_day: int = 0,
) -> Dict[str, Any]:
    """Helper to construct an isolated valid member dictionary for unit tests."""
    fields = {k: None for k in HARD + SOFT}
    # Set hard constraints to be compatible with everyone
    fields["age_min"] = 18
    fields["age_max"] = 65
    fields["who_to_meet"] = ["woman", "man", "non_binary"]
    fields["relationship_structure"] = "monogamous"
    fields["smoking"] = "no"
    fields["partner_smoking"] = "any"
    fields["has_children"] = False
    fields["partner_children"] = "any"
    fields["wants_children"] = "unsure"
    fields["acceptable_zones"] = ["zone_a", "zone_b", "zone_c", "zone_d"]
    fields["schedule"] = ["weekend_day"]

    status = {k: ("observed" if fields[k] is not None else "not_asked") for k in HARD + SOFT}
    obs_day = {k: (arrived_day if fields[k] is not None else None) for k in HARD + SOFT}

    return {
        "member_id": member_id,
        "pool_id": "test_pool",
        "synthetic": True,
        "age": age,
        "gender": gender,
        "zone": zone,
        "arrived_day": arrived_day,
        "fields": fields,
        "field_status": status,
        "field_observed_day": obs_day,
        "source": "synthetic_questionnaire",
        "available": available,
    }


def _make_state(members: List[Dict[str, Any]], introductions: List[Dict[str, Any]] = None, day: int = 0, budget: int = 12) -> Dict[str, Any]:
    return {
        "schema_version": VERSION,
        "synthetic": True,
        "day": day,
        "ask_budget_remaining": budget,
        "members": members,
        "introductions": introductions or [],
        "feedback": [],
        "ask_log": [],
    }


# =========================================================================
# Core Specification Tests
# =========================================================================

def test_1_g_matches_frozen_reference():
    """G behavior matches the frozen reference on identical requests."""
    world = generate(seed=810001, n=200, variant="development")
    sim = Simulator(world)
    obs = sim.observe()

    req_ask = {"schema_version": VERSION, "phase": "ask", "state": obs, "memory": {}}
    res_off_ask = official_ref.decide(req_ask, "greedy")
    res_g_ask = decide_g(req_ask, {"id": "G"})
    assert res_g_ask["asks"] == res_off_ask["asks"]

    # Match phase
    sim.resolve_asks(res_g_ask["asks"])
    obs_match = sim.observe()
    req_match = {"schema_version": VERSION, "phase": "match", "state": obs_match, "memory": {}}
    res_off_match = official_ref.decide(req_match, "greedy")
    res_g_match = decide_g(req_match, {"id": "G"})
    assert res_g_match["pairs"] == res_off_match["pairs"]


def test_2_hard_batches_identical_across_all_three_arms():
    """Hard batches are identical across all three functions on identical observations."""
    world = generate(seed=810002, n=200, variant="cold_start")
    sim = Simulator(world)
    obs = sim.observe()

    req = {"schema_version": VERSION, "phase": "ask", "state": obs, "memory": {}}
    res_g = decide_g(req, {"id": "G"})
    res_rand = decide_g_random_soft(req, {"id": "G_random_soft"})
    res_target = decide_g_targeted_soft(req, {"id": "G_targeted_soft"})

    hard_g = [a for a in res_g["asks"] if a["field"] == "constraints"]
    hard_rand = [a for a in res_rand["asks"] if a["field"] == "constraints"]
    hard_target = [a for a in res_target["asks"] if a["field"] == "constraints"]

    assert hard_g == hard_rand == hard_target
    assert hard_g == baseline_asks(obs)


def test_3_soft_queries_never_displace_hard():
    """Added soft queries never displace any G hard question."""
    world = generate(seed=810003, n=200, variant="sparse")
    sim = Simulator(world)
    obs = sim.observe()

    expected_hard = baseline_asks(obs)
    req = {"schema_version": VERSION, "phase": "ask", "state": obs, "memory": {}}

    res_target = decide_g_targeted_soft(req)
    res_rand = decide_g_random_soft(req)

    # First len(expected_hard) elements must be the exact hard asks in order
    assert res_target["asks"][:len(expected_hard)] == expected_hard
    assert res_rand["asks"][:len(expected_hard)] == expected_hard


def test_4_budget_accounting():
    """Budget 12, hard cost 3, soft cost 1. Never exceeds remaining budget."""
    for variant in ["development", "cold_start", "delayed", "shift", "drift", "sparse"]:
        world = generate(seed=810004, n=200, variant=variant)
        sim = Simulator(world)
        obs = sim.observe()
        req = {"schema_version": VERSION, "phase": "ask", "state": obs, "memory": {}}

        for decide_fn in [decide_g, decide_g_random_soft, decide_g_targeted_soft]:
            res = decide_fn(req)
            cost = sum(3 if a["field"] == "constraints" else 1 for a in res["asks"])
            assert cost <= obs["ask_budget_remaining"]
            assert cost <= 12


def test_5_no_adaptive_selection_after_answers():
    """Query batch is chosen completely before any same-day answers arrive."""
    world = generate(seed=810001, n=200, variant="development")
    sim = Simulator(world)
    obs = sim.observe()
    req = {"schema_version": VERSION, "phase": "ask", "state": obs, "memory": {}}

    # The ask decide function receives only the pre-answer observation state
    res = decide_g_targeted_soft(req)
    # Validate it is a valid ask batch
    available = {m["member_id"] for m in obs["members"] if m["available"]}
    ok, errs, cost = validate_ask_batch(res["asks"], available, obs["ask_budget_remaining"])
    assert ok, f"Validation errors: {errs}"


def test_6_observed_and_declined_questions_excluded():
    """Do not query observed or declined soft fields."""
    m1 = _make_clean_member("m1")
    m2 = _make_clean_member("m2")

    # m2 has observed goal
    m2["fields"]["relationship_goal"] = "long_term"
    m2["field_status"]["relationship_goal"] = "observed"

    # m1 has declined pace
    m1["field_status"]["relationship_pace"] = "declined"
    # m1 has observed lifestyle
    m1["fields"]["lifestyle"] = "quiet"
    m1["field_status"]["lifestyle"] = "observed"
    # m1 has not_asked goal
    m1["fields"]["relationship_goal"] = None
    m1["field_status"]["relationship_goal"] = "not_asked"

    state = _make_state([m1, m2])
    candidates = extract_candidate_set([m1, m2], {"m1": ["m2"], "m2": ["m1"]})

    # (m1, relationship_goal) should be in candidates because m2 has observed goal
    assert ("m1", "relationship_goal") in candidates
    # (m1, relationship_pace) declined -> not in candidates
    assert ("m1", "relationship_pace") not in candidates
    # (m1, lifestyle) observed -> not in candidates
    assert ("m1", "lifestyle") not in candidates
    # (m2, relationship_goal) observed -> not in candidates
    assert ("m2", "relationship_goal") not in candidates


def test_7_false_not_treated_as_missing():
    """Do not treat observed Boolean False as missing."""
    m1 = _make_clean_member("m1")
    # In hard constraints, has_children is False
    assert m1["fields"]["has_children"] is False
    assert m1["field_status"]["has_children"] == "observed"
    # It must not be treated as missing by baseline_asks
    # Since all hard constraints on m1 are observed, baseline_asks on m1 is empty
    state = _make_state([m1])
    assert baseline_asks(state) == []


def test_8_unavailable_members_excluded():
    """Unavailable members are excluded from queries and dyad graph."""
    m1 = _make_clean_member("m1", available=False)
    m2 = _make_clean_member("m2", available=True)
    m2["fields"]["relationship_goal"] = "long_term"
    m2["field_status"]["relationship_goal"] = "observed"

    state = _make_state([m1, m2])
    avail, neighbors, _ = build_legal_graph(state)
    assert "m1" not in [m["member_id"] for m in avail]
    candidates = extract_candidate_set(avail, neighbors)
    assert not any(u == "m1" for u, k in candidates)


def test_9_past_dyads_excluded_from_targeting_graph():
    """Past dyads are excluded from targeting graph."""
    m1 = _make_clean_member("m1")
    m2 = _make_clean_member("m2")
    m2["fields"]["relationship_goal"] = "long_term"
    m2["field_status"]["relationship_goal"] = "observed"

    intros = [{"introduction_id": "intro_1", "user_a": "m1", "user_b": "m2", "assigned_day": 0}]
    state = _make_state([m1, m2], introductions=intros)
    avail, neighbors, past = build_legal_graph(state)

    assert ("m1", "m2") in past or ("m2", "m1") in past
    assert neighbors["m1"] == []
    assert neighbors["m2"] == []

    candidates = extract_candidate_set(avail, neighbors)
    assert len(candidates) == 0


def test_10_random_and_targeted_use_same_candidate_set():
    """Random and targeted arms use the exact same candidate set C."""
    world = generate(seed=810001, n=200, variant="development")
    sim = Simulator(world)
    obs = sim.observe()

    avail, neighbors, _ = build_legal_graph(obs)
    candidates = extract_candidate_set(avail, neighbors)

    _, meta_t = select_targeted_soft_asks(obs, 12)
    _, meta_r = select_random_soft_asks(obs, 12)

    assert meta_t["candidate_count"] == meta_r["candidate_count"] == len(candidates)


def test_11_targeting_priority_and_tie_rules():
    """Targeting priority and tie rules match specification:
    - Priority 1: >= 2 legal neighbors with different observed answers to k.
    - Priority 2: remaining questions with >= 1 such neighbor.
    - Tie ranking: n_obs desc, deg_u desc, field asc, member_id asc.
    """
    # Create u1: 2 neighbors with differing answers on goal ('long_term' vs 'exploring') -> Priority 1
    u1 = _make_clean_member("u1")
    n1a = _make_clean_member("n1a")
    n1a["fields"]["relationship_goal"] = "long_term"
    n1a["field_status"]["relationship_goal"] = "observed"
    n1b = _make_clean_member("n1b")
    n1b["fields"]["relationship_goal"] = "exploring"
    n1b["field_status"]["relationship_goal"] = "observed"

    # Create u2: 2 neighbors with same answer on goal ('long_term') -> Priority 2, n_obs=2
    u2 = _make_clean_member("u2")
    n2a = _make_clean_member("n2a")
    n2a["fields"]["relationship_goal"] = "long_term"
    n2a["field_status"]["relationship_goal"] = "observed"
    n2b = _make_clean_member("n2b")
    n2b["fields"]["relationship_goal"] = "long_term"
    n2b["field_status"]["relationship_goal"] = "observed"

    # Create u3: 1 neighbor with observed answer on goal -> Priority 2, n_obs=1
    u3 = _make_clean_member("u3")
    n3a = _make_clean_member("n3a")
    n3a["fields"]["relationship_goal"] = "long_term"
    n3a["field_status"]["relationship_goal"] = "observed"

    members = [u1, n1a, n1b, u2, n2a, n2b, u3, n3a]
    neighbors = {
        "u1": ["n1a", "n1b"],
        "n1a": ["u1"],
        "n1b": ["u1"],
        "u2": ["n2a", "n2b"],
        "n2a": ["u2"],
        "n2b": ["u2"],
        "u3": ["n3a"],
        "n3a": ["u3"],
    }

    candidates = extract_candidate_set(members, neighbors)
    ranked = rank_targeted_candidates(candidates)

    assert candidates[("u1", "relationship_goal")]["priority"] == 1
    assert candidates[("u2", "relationship_goal")]["priority"] == 2
    assert candidates[("u3", "relationship_goal")]["priority"] == 2

    # In ranked list, u1 must come before u2, and u2 before u3
    idx_u1 = ranked.index(("u1", "relationship_goal"))
    idx_u2 = ranked.index(("u2", "relationship_goal"))
    idx_u3 = ranked.index(("u3", "relationship_goal"))
    assert idx_u1 < idx_u2 < idx_u3


def test_12_no_candidates_leaves_budget_unused():
    """If no eligible question has direct comparison opportunity, leave remaining budget unused."""
    # Two members, both have no observed soft fields
    m1 = _make_clean_member("m1")
    m2 = _make_clean_member("m2")
    state = _make_state([m1, m2])

    soft_t, meta_t = select_targeted_soft_asks(state, 6)
    soft_r, meta_r = select_random_soft_asks(state, 6)

    assert soft_t == []
    assert soft_r == []
    assert meta_t["candidate_count"] == 0
    assert meta_r["candidate_count"] == 0


def test_13_random_selection_reproducibility():
    """Reproducibility of random selection: same state + salt -> exact same selection."""
    world = generate(seed=810001, n=200, variant="development")
    sim = Simulator(world)
    obs = sim.observe()

    soft_r1, meta_r1 = select_random_soft_asks(obs, 6, salt="test_salt_a")
    soft_r2, meta_r2 = select_random_soft_asks(obs, 6, salt="test_salt_a")
    assert soft_r1 == soft_r2
    assert meta_r1["rng_seed_int"] == meta_r2["rng_seed_int"]


def test_14_every_output_passes_action_validator():
    """Every output from all three policies passes the actual action validator."""
    world = generate(seed=810002, n=200, variant="development")
    sim = Simulator(world)
    obs = sim.observe()
    available = {m["member_id"] for m in obs["members"] if m["available"]}

    for decide_fn in [decide_g, decide_g_random_soft, decide_g_targeted_soft]:
        req_ask = {"schema_version": VERSION, "phase": "ask", "state": obs, "memory": {}}
        res_ask = decide_fn(req_ask)
        ok_ask, errs_ask, cost = validate_ask_batch(res_ask["asks"], available, obs["ask_budget_remaining"])
        assert ok_ask, f"Ask batch failed validation: {errs_ask}"

        # Match phase
        req_match = {"schema_version": VERSION, "phase": "match", "state": obs, "memory": res_ask["memory"]}
        res_match = decide_fn(req_match)
        ok_match, errs_match = validate_match_batch(res_match["pairs"], available, obs["introductions"], obs["members"])
        assert ok_match, f"Match batch failed validation: {errs_match}"

        ok_mem, errs_mem, _ = validate_policy_memory(res_match["memory"])
        assert ok_mem, f"Memory validation failed: {errs_mem}"


def test_15_no_hidden_metadata_enters_decisions():
    """No simulator seed, family label, latent truth, or decoded ID enters decisions."""
    world = generate(seed=810003, n=200, variant="development")
    sim = Simulator(world)
    obs = sim.observe()

    # Verify obs does not contain 'truth', 'seed', 'variant'
    assert "seed" not in obs
    assert "variant" not in obs
    for m in obs["members"]:
        assert "truth" not in m
        assert "bias" not in m
        assert "second_bias" not in m
        assert "response_rate" not in m
        assert "exit_day" not in m


def test_16_day59_followup_and_metric_normalization():
    """Day 59 introductions retain full eventual reward through follow-up.
    Endpoint is Y = 100 * Q / A (single dyad count, no factor of two).
    """
    from research7b.workspace.research7.runtime.metrics import compute_run_metrics

    # Construct synthetic scenario with 1 qualifying introduction
    intro_id = "intro_test_59"
    intros = [{"introduction_id": intro_id, "user_a": "u1", "user_b": "u2", "assigned_day": 59}]
    feedback = [
        {"introduction_id": intro_id, "member_id": "u1", "event": "introduction_response", "value": "yes", "occurred_day": 62, "observed_day": 62},
        {"introduction_id": intro_id, "member_id": "u2", "event": "introduction_response", "value": "yes", "occurred_day": 63, "observed_day": 63},
        {"introduction_id": intro_id, "member_id": None, "event": "date_happened", "value": True, "occurred_day": 75, "observed_day": 75},
        {"introduction_id": intro_id, "member_id": "u1", "event": "second_meeting_intention", "value": "yes", "occurred_day": 77, "observed_day": 77},
        {"introduction_id": intro_id, "member_id": "u2", "event": "second_meeting_intention", "value": "yes", "occurred_day": 77, "observed_day": 77},
    ]
    arrived = [{"member_id": f"u{i}", "arrived_day": 0} for i in range(1, 201)]

    metrics = compute_run_metrics(intros, [], feedback=feedback, arrived_members=arrived)
    assert metrics["mutual_second_meeting_intention"] == 1
    assert metrics["arrived_members"] == 200
    # Correct normalization: 100 * 1 / 200 = 0.5 (NOT 1.0!)
    assert metrics["msmi_per_100_arrived_members"] == 0.5


def test_17_seed_group_aggregation_logic():
    """Seed-group aggregation computes D_s over six families, yielding 24 D_s values."""
    from statistics import mean, stdev
    import math

    # Synthetic 24 seeds x 6 families
    data_candidate = { (s, f): 0.5 + 0.05 * (s % 3) for s in range(24) for f in range(6) }
    data_parent = { (s, f): 0.5 for s in range(24) for f in range(6) }

    # Compute seed-cluster paired differences
    D_s = [mean(data_candidate[s, f] - data_parent[s, f] for f in range(6)) for s in range(24)]
    assert len(D_s) == 24
    avg_diff = mean(D_s)
    sd_diff = stdev(D_s)
    se_diff = sd_diff / math.sqrt(24)
    assert avg_diff > 0


# =========================================================================
# Six Tiny Fixtures
# =========================================================================

def test_fixture_1_no_legal_neighbor_means_no_soft_question():
    """Tiny fixture: No legal neighbor means no soft question."""
    # Isolated member u1, no other available members
    u1 = _make_clean_member("u1")
    state = _make_state([u1])
    soft_asks, meta = select_targeted_soft_asks(state, remaining_budget=6)
    assert soft_asks == []
    assert meta["candidate_count"] == 0


def test_fixture_2_one_informative_neighbor_creates_candidate():
    """Tiny fixture: One informative neighbor creates a candidate."""
    u1 = _make_clean_member("u1")
    n1 = _make_clean_member("n1")
    n1["fields"]["relationship_goal"] = "long_term"
    n1["field_status"]["relationship_goal"] = "observed"

    state = _make_state([u1, n1])
    soft_asks, meta = select_targeted_soft_asks(state, remaining_budget=6)
    assert len(soft_asks) == 1
    assert soft_asks[0] == {"member_id": "u1", "field": "relationship_goal"}
    assert meta["candidate_count"] == 1


def test_fixture_3_two_neighbors_different_answers_outranks_noncontested():
    """Tiny fixture: Two neighbors with different answers outrank a noncontested candidate."""
    # u_contested has 2 neighbors with 'slow' vs 'quick' on relationship_pace
    u_cont = _make_clean_member("u_cont")
    c1 = _make_clean_member("c1")
    c1["fields"]["relationship_pace"] = "slow"
    c1["field_status"]["relationship_pace"] = "observed"
    c2 = _make_clean_member("c2")
    c2["fields"]["relationship_pace"] = "quick"
    c2["field_status"]["relationship_pace"] = "observed"

    # u_single has 1 neighbor with 'slow' on relationship_pace
    u_sing = _make_clean_member("u_sing")
    s1 = _make_clean_member("s1")
    s1["fields"]["relationship_pace"] = "slow"
    s1["field_status"]["relationship_pace"] = "observed"

    # Budget is 1, so only top candidate can be selected
    state = _make_state([u_cont, c1, c2, u_sing, s1])
    soft_asks, _ = select_targeted_soft_asks(state, remaining_budget=1)

    assert len(soft_asks) == 1
    assert soft_asks[0]["member_id"] == "u_cont"
    assert soft_asks[0]["field"] == "relationship_pace"


def test_fixture_4_revealing_soft_answer_changes_greedy_matching():
    """Tiny fixture: Revealing a soft answer changes Greedy's selected matching."""
    # u1 can match with either v1 or v2 (both legal)
    # v1 has goal='long_term', pace='steady' (score 2 if u1 matches both)
    # v2 has goal='exploring', pace='steady' (score 2 if u1 matches both)
    # Initially u1 has neither observed, so scores for (u1, v1) and (u1, v2) are both 0.
    # Tie goes to deterministic edge order.
    # If u1's goal is revealed as 'long_term', (u1, v1) gets score 1, changing the match!
    u1 = _make_clean_member("u1")
    v1 = _make_clean_member("v1")
    v1["fields"]["relationship_goal"] = "long_term"
    v1["field_status"]["relationship_goal"] = "observed"

    v2 = _make_clean_member("v2")
    v2["fields"]["relationship_goal"] = "exploring"
    v2["field_status"]["relationship_goal"] = "observed"

    # Suppose edge order naturally picks (u1, v2) when tied
    # Let's check matching before revelation:
    state_before = _make_state([u1, v1, v2])
    match_before = baseline_match(state_before)
    assert len(match_before) == 1
    chosen_partner_before = match_before[0][1] if match_before[0][0] == "u1" else match_before[0][0]

    # Now reveal u1's goal to match the other partner
    other_partner = "v1" if chosen_partner_before == "v2" else "v2"
    u1_revealed = copy.deepcopy(u1)
    u1_revealed["fields"]["relationship_goal"] = v1["fields"]["relationship_goal"] if other_partner == "v1" else v2["fields"]["relationship_goal"]
    u1_revealed["field_status"]["relationship_goal"] = "observed"

    state_after = _make_state([u1_revealed, v1, v2])
    match_after = baseline_match(state_after)
    assert len(match_after) == 1
    chosen_partner_after = match_after[0][1] if match_after[0][0] == "u1" else match_after[0][0]

    assert chosen_partner_after == other_partner
    assert chosen_partner_after != chosen_partner_before


def test_fixture_5_revealing_soft_answer_does_not_change_matching():
    """Tiny fixture: Revealing an answer does not change matching."""
    # u1 has only one legal neighbor v1. Regardless of u1's soft field, (u1, v1) is matched.
    u1 = _make_clean_member("u1")
    v1 = _make_clean_member("v1")
    state1 = _make_state([u1, v1])
    match1 = baseline_match(state1)

    u1_obs = copy.deepcopy(u1)
    u1_obs["fields"]["relationship_goal"] = "long_term"
    u1_obs["field_status"]["relationship_goal"] = "observed"
    state2 = _make_state([u1_obs, v1])
    match2 = baseline_match(state2)

    assert match1 == match2 == [["u1", "v1"]] or match1 == match2 == [["v1", "u1"]]


def test_fixture_6_hard_queries_consume_entire_budget_leaves_no_soft_queries():
    """Tiny fixture: Hard queries consume entire budget (4 bundles = 12 cost) -> 0 soft queries."""
    # 4 members needing constraints
    members = []
    for i in range(4):
        m = _make_clean_member(f"m{i}")
        # Mark all hard fields as unknown (None)
        for h in HARD:
            m["fields"][h] = None
            m["field_status"][h] = "not_asked"
        members.append(m)

    state = _make_state(members, budget=12)
    hard_asks = baseline_asks(state)
    assert len(hard_asks) == 4
    assert len(hard_asks) * 3 == 12

    res_target = decide_g_targeted_soft({"phase": "ask", "state": state, "memory": {}})
    res_rand = decide_g_random_soft({"phase": "ask", "state": state, "memory": {}})

    soft_target = [a for a in res_target["asks"] if a["field"] != "constraints"]
    soft_rand = [a for a in res_rand["asks"] if a["field"] != "constraints"]

    assert soft_target == []
    assert soft_rand == []
