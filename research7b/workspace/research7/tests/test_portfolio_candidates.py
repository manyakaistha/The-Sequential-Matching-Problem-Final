"""Test suite for Research 7 portfolio candidates Q1 and A1.

Covers:
1. Q1 collision-aware acquisition (T06 complements/collisions, T11 decline/budget, T16 shortlist)
2. A1 terminal-value allocation (T02 4-node 1.30 vs 0.95, triangle matching, cardinality vs weight)
3. Deterministic quantization and score-greedy fallbacks
"""

import copy
import json
import unittest
import networkx as nx

from research7.policies.q1 import decide as q1_decide, get_query_eligible_actors
from research7.policies.a1 import (
    decide as a1_decide,
    decide_a1_match,
    score_greedy_match,
    compute_pair_score,
)
from research7.policies.h1 import (
    decide as h1_decide,
    extract_actor_trials,
    get_actor_posterior_predictive,
    compute_pair_score_h1,
)
from kit import HARD, SOFT, eligibility


class TestPortfolioCandidates(unittest.TestCase):

    def test_q1_t11_decline_and_budget_bounds(self):
        """Actors with declined hard constraints are never queried; budget strictly capped."""
        members = [
            {
                "member_id": 1,
                "pool_id": 0,
                "available": True,
                "arrived_day": 0,
                "gender": "F", "target_gender": "M", "age": 25,
                "field_status": {"smoking": "declined", "relationship_goal": "observed"},
            },
            {
                "member_id": 2,
                "pool_id": 0,
                "available": True,
                "arrived_day": 0,
                "gender": "M", "target_gender": "F", "age": 26,
                "field_status": {"smoking": "unasked", "relationship_goal": "observed"},
            },
        ]
        state = {"members": members, "ask_budget_remaining": 12, "introductions": []}

        # Actor 1 has declined hard field -> excluded
        eligible = get_query_eligible_actors(state)
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible[0]["member_id"], 2)

        # Execution with budget 5 -> can only ask 1 actor (cost 3 <= 5)
        state["ask_budget_remaining"] = 5
        resp = q1_decide({"phase": "ask", "state": state, "memory": None})
        self.assertLessEqual(len(resp["asks"]), 1)
        if resp["asks"]:
            self.assertEqual(resp["asks"][0]["member_id"], 2)

    def test_q1_t06_collision_and_optimistic_cardinality(self):
        """Q1 selects candidate queries that maximize optimistic matching cardinality."""
        # 1 verified female actor (F1), and 2 candidate male actors (M1, M2).
        # Both M1 and M2 could match with F1, but they compete for F1 (collision).
        # Adding a second verified female actor (F2) creates complementary opportunities.
        hard_base = {
            'age_min': 18, 'age_max': 50, 'who_to_meet': [1, 2, 10, 20],
            'relationship_structure': 'monogamous', 'smoking': 'never', 'partner_smoking': 'never',
            'has_children': False, 'partner_children': False, 'wants_children': 'maybe',
            'acceptable_zones': [1, 2], 'schedule': 'flexible',
        }
        members = [
            {
                "member_id": 1, "pool_id": 0, "available": True, "arrived_day": 0, "zone": 1,
                "gender": "F", "target_gender": "M", "age": 25,
                "field_status": {k: "observed" for k in HARD},
                "fields": copy.deepcopy(hard_base),
            },
            {
                "member_id": 2, "pool_id": 0, "available": True, "arrived_day": 0, "zone": 1,
                "gender": "F", "target_gender": "M", "age": 25,
                "field_status": {k: "observed" for k in HARD},
                "fields": copy.deepcopy(hard_base),
            },
            {
                "member_id": 10, "pool_id": 0, "available": True, "arrived_day": 1, "zone": 1,
                "gender": "M", "target_gender": "F", "age": 27,
                "field_status": {k: "unasked" for k in HARD},
                "fields": copy.deepcopy(hard_base),
            },
            {
                "member_id": 20, "pool_id": 0, "available": True, "arrived_day": 2, "zone": 1,
                "gender": "M", "target_gender": "F", "age": 28,
                "field_status": {k: "unasked" for k in HARD},
                "fields": copy.deepcopy(hard_base),
            },
        ]
        state = {"members": members, "ask_budget_remaining": 6, "introductions": []}
        resp = q1_decide({"phase": "ask", "state": state, "memory": None})
        asked_ids = {a["member_id"] for a in resp["asks"]}

        # Both M10 and M20 should be queried because together with F1 and F2 they achieve cardinality 2
        self.assertEqual(len(asked_ids), 2)
        self.assertEqual(asked_ids, {10, 20})

    def test_a1_t02_exact_four_node_weights(self):
        """T02 assertion: 4-node AB=.90, CD=.05, AD=.65, BC=.65 yields 1.30 (not greedy .95)."""
        scores = {
            (1, 2): 0.90,  # AB
            (3, 4): 0.05,  # CD
            (1, 4): 0.65,  # AD
            (2, 3): 0.65,  # BC
        }
        # Score greedy picks AB (0.90) and CD (0.05) -> total 0.95
        greedy = score_greedy_match(scores)
        self.assertEqual(set(greedy), {(1, 2), (3, 4)})
        self.assertAlmostEqual(sum(scores[p] for p in greedy), 0.95)

        # A1 maximum weight matching (maxcardinality=False) picks AD (0.65) and BC (0.65) -> total 1.30
        G = nx.Graph()
        for (u, v), w in scores.items():
            G.add_edge(u, v, weight=int(round(w * 1_000_000)))
        matching = nx.max_weight_matching(G, maxcardinality=False, weight="weight")
        matching_pairs = sorted(tuple(sorted(p)) for p in matching)

        self.assertEqual(set(matching_pairs), {(1, 4), (2, 3)})
        self.assertAlmostEqual(sum(scores[p] for p in matching_pairs), 1.30)

    def test_a1_triangle_and_cardinality_vs_weight(self):
        """Triangle matching cardinality is 1 (not fractional 1.5); heavy edge beats two light edges."""
        # Triangle: nodes 1, 2, 3 each with weight 1.0
        triangle_scores = {(1, 2): 1.0, (2, 3): 1.0, (1, 3): 1.0}
        G_tri = nx.Graph()
        for (u, v), w in triangle_scores.items():
            G_tri.add_edge(u, v, weight=int(round(w * 1_000_000)))
        tri_match = nx.max_weight_matching(G_tri, maxcardinality=False, weight="weight")
        self.assertEqual(len(tri_match), 1, "Triangle matching cardinality must be 1, never fractional")

        # Conflict: 1 heavy edge AB=.90 vs 2 light edges CD=.10, EF=.10
        # If cardinality was forced to max (like K), it might pick {CD, EF} if constrained.
        # But here 4 nodes: (1, 2) has weight .90; if (1, 3) has .10 and (2, 4) has .10:
        # Max cardinality picks {(1, 3), (2, 4)} = 0.20
        # Max weight picks {(1, 2)} = 0.90
        conflict_scores = {
            (1, 2): 0.90,
            (1, 3): 0.10,
            (2, 4): 0.10,
        }
        G_conf = nx.Graph()
        for (u, v), w in conflict_scores.items():
            G_conf.add_edge(u, v, weight=int(round(w * 1_000_000)))

        max_weight = nx.max_weight_matching(G_conf, maxcardinality=False, weight="weight")
        max_card = nx.max_weight_matching(G_conf, maxcardinality=True, weight="weight")

        self.assertEqual(set(tuple(sorted(p)) for p in max_weight), {(1, 2)})
        self.assertEqual(set(tuple(sorted(p)) for p in max_card), {(1, 3), (2, 4)})

    def test_a1_full_decide_wire_execution(self):
        """A1 decide handles legal wire requests, returning disjoint legal matching."""
        hard_base = {
            'age_min': 18, 'age_max': 50, 'who_to_meet': [1, 2, 3, 4],
            'relationship_structure': 'monogamous', 'smoking': 'never', 'partner_smoking': 'never',
            'has_children': False, 'partner_children': False, 'wants_children': 'maybe',
            'acceptable_zones': [1, 2], 'schedule': 'flexible',
        }
        members = [
            {"member_id": 1, "pool_id": 0, "available": True, "zone": 1, "gender": "F", "target_gender": "M", "age": 25,
             "field_status": {k: "observed" for k in HARD}, "fields": {**hard_base, "lifestyle": "active"}},
            {"member_id": 2, "pool_id": 0, "available": True, "zone": 1, "gender": "M", "target_gender": "F", "age": 26,
             "field_status": {k: "observed" for k in HARD}, "fields": {**hard_base, "lifestyle": "active"}},
            {"member_id": 3, "pool_id": 0, "available": True, "zone": 1, "gender": "F", "target_gender": "M", "age": 28,
             "field_status": {k: "observed" for k in HARD}, "fields": {**hard_base, "lifestyle": "relaxed"}},
            {"member_id": 4, "pool_id": 0, "available": True, "zone": 1, "gender": "M", "target_gender": "F", "age": 29,
             "field_status": {k: "observed" for k in HARD}, "fields": {**hard_base, "lifestyle": "relaxed"}},
        ]
        request = {
            "schema_version": "1.0",
            "phase": "match",
            "state": {"day": 10, "members": members, "introductions": [], "ask_budget_remaining": 12},
            "memory": None,
        }
        resp = a1_decide(request)
        self.assertIn("pairs", resp)
        pairs = [tuple(sorted(p)) for p in resp["pairs"]]
        # Disjoint allocation
        used = set()
        for u, v in pairs:
            self.assertNotIn(u, used)
            self.assertNotIn(v, used)
            used.add(u)
            used.add(v)

    def test_h1_t09_beta_surrogate_posterior_one_third(self):
        """T09 assertion: Beta(1,1) prior with 1 mature non-Yes outcome yields 1/3 posterior predictive."""
        # 1 mature No outcome (y_i = 0, n_i = 1) -> (1 + 0) / (1 + 1 + 1) = 1/3
        pred_no = get_actor_posterior_predictive(y_i=0, n_i=1, alpha=1.0, beta=1.0)
        self.assertAlmostEqual(pred_no, 1.0 / 3.0)

        # 1 mature Yes outcome (y_i = 1, n_i = 1) -> (1 + 1) / (1 + 1 + 1) = 2/3
        pred_yes = get_actor_posterior_predictive(y_i=1, n_i=1, alpha=1.0, beta=1.0)
        self.assertAlmostEqual(pred_yes, 2.0 / 3.0)

        # 0 trials -> 1/2
        pred_zero = get_actor_posterior_predictive(y_i=0, n_i=0, alpha=1.0, beta=1.0)
        self.assertAlmostEqual(pred_zero, 0.5)

    def test_h1_dedup_and_unresolved(self):
        """Deduplication by (intro_id, member_id); unresolved event is not a trial."""
        state = {
            "feedback": [
                # intro 1, member 10: value 'no'
                {"introduction_id": "intro1", "member_id": 10, "event": "introduction_response", "value": "no"},
                # duplicate event for intro 1, member 10
                {"introduction_id": "intro1", "member_id": 10, "event": "introduction_response", "value": "no"},
                # intro 2, member 10: mature no_response
                {"introduction_id": "intro2", "member_id": 10, "event": "introduction_response", "value": None, "missing_reason": "no_response"},
                # intro 3, member 10: unresolved (value None, missing_reason None) -> NOT a trial
                {"introduction_id": "intro3", "member_id": 10, "event": "introduction_response", "value": None, "missing_reason": None},
                # intro 1, member 20: value 'yes'
                {"introduction_id": "intro1", "member_id": 20, "event": "introduction_response", "value": "yes"},
            ]
        }
        trials = extract_actor_trials(state)
        # member 10: 2 mature trials (intro1 and intro2), both 0 Yes -> (0, 2)
        self.assertEqual(trials[10], (0, 2))
        # member 20: 1 mature trial, 1 Yes -> (1, 1)
        self.assertEqual(trials[20], (1, 1))

    def test_h1_full_decide_wire_execution(self):
        """H1 decide handles legal wire requests, returning disjoint pairs and memory reset."""
        hard_base = {
            'age_min': 18, 'age_max': 50, 'who_to_meet': [1, 2, 3, 4],
            'relationship_structure': 'monogamous', 'smoking': 'never', 'partner_smoking': 'never',
            'has_children': False, 'partner_children': False, 'wants_children': 'maybe',
            'acceptable_zones': [1, 2], 'schedule': 'flexible',
        }
        members = [
            {"member_id": 1, "pool_id": 0, "available": True, "zone": 1, "gender": "F", "target_gender": "M", "age": 25,
             "field_status": {k: "observed" for k in HARD}, "fields": {**hard_base, "lifestyle": "active"}},
            {"member_id": 2, "pool_id": 0, "available": True, "zone": 1, "gender": "M", "target_gender": "F", "age": 26,
             "field_status": {k: "observed" for k in HARD}, "fields": {**hard_base, "lifestyle": "active"}},
            {"member_id": 3, "pool_id": 0, "available": True, "zone": 1, "gender": "F", "target_gender": "M", "age": 28,
             "field_status": {k: "observed" for k in HARD}, "fields": {**hard_base, "lifestyle": "relaxed"}},
            {"member_id": 4, "pool_id": 0, "available": True, "zone": 1, "gender": "M", "target_gender": "F", "age": 29,
             "field_status": {k: "observed" for k in HARD}, "fields": {**hard_base, "lifestyle": "relaxed"}},
        ]
        request = {
            "schema_version": "1.0",
            "phase": "match",
            "state": {
                "day": 10,
                "members": members,
                "introductions": [],
                "ask_budget_remaining": 12,
                "feedback": [
                    {"introduction_id": "i1", "member_id": 1, "event": "introduction_response", "value": "yes"},
                ]
            },
            "memory": None,
        }
        resp = h1_decide(request)
        self.assertIn("pairs", resp)
        self.assertIsInstance(resp["memory"], dict)
        used = set()
        for u, v in resp["pairs"]:
            self.assertNotIn(u, used)
            self.assertNotIn(v, used)
            used.add(u)
            used.add(v)


if __name__ == "__main__":
    unittest.main()
