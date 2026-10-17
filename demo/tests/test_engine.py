from __future__ import annotations

from copy import deepcopy

from demo.engine import DemoEngine, PRESETS
from kit import Simulator, generate
from policy import decide


def test_ask_then_match_matches_reference_policy_and_day_order():
    preset = PRESETS["public-101-development"]
    engine = DemoEngine(preset, "greedy")
    reference = Simulator(generate(101, 200, preset["id"], "development"))

    ask_request = {"schema_version": "1.0.0", "phase": "ask", "state": reference.observe(), "memory": None}
    ask_response = decide(deepcopy(ask_request), "greedy")
    reference.resolve_asks(ask_response["asks"])
    engine.step_once()
    assert engine.phase == "match"
    assert engine.sim.day == 0
    assert engine.sim.ask_log == reference.ask_log

    match_request = {"schema_version": "1.0.0", "phase": "match", "state": reference.observe(), "memory": ask_response["memory"]}
    match_response = decide(deepcopy(match_request), "greedy")
    reference.advance(match_response["pairs"])
    engine.step_once()
    assert engine.phase == "ask"
    assert engine.sim.day == 1
    assert engine.sim.introductions == reference.introductions
    assert engine.sim.metrics() == reference.metrics()


def test_full_episode_reaches_followup_completion_without_new_pairs():
    engine = DemoEngine(PRESETS["public-101-development"], "greedy")
    engine.advance_steps(160)  # 60 ask/match days plus 40 empty follow-up advances.
    assert engine.complete
    assert engine.sim.day == 100
    assert all(event["payload"].get("pairs") == [] for event in engine.events if event["event_type"] == "followup_advance")
    view = engine.view("run")
    assert view["metrics"]["status"] == "final"
    assert view["metrics"]["arrived_members"] == 200


def test_public_state_has_no_hidden_world_fields():
    engine = DemoEngine(PRESETS["public-101-development"], "greedy")
    state = engine.view("run")["state"]
    forbidden = {"truth", "bias", "response_rate", "second_bias", "exit_day"}
    serialized = repr(state)
    assert not any(name in serialized for name in forbidden)
    for member in state["members"]:
        assert "truth" not in member
        assert set(member) <= {"member_id", "pool_id", "synthetic", "age", "gender", "zone", "arrived_day", "fields", "field_status", "field_observed_day", "source", "available"}


def test_qualification_fixture_distinguishes_date_and_mature_msmi():
    sim = Simulator(generate(101, 8, "fixture", "development"))
    ids = [member["member_id"] for member in sim.world["members"][:6]]
    sim.day = 100
    for index, pair in enumerate(((ids[0], ids[1]), (ids[2], ids[3]), (ids[4], ids[5]))):
        intro_id = f"fixture-{index}"
        assigned = 1 + index
        sim.introductions.append({"introduction_id": intro_id, "user_a": pair[0], "user_b": pair[1], "assigned_day": assigned, "response_deadline_day": assigned + 7, "logging_policy": "fixture", "propensity": None})
        for member_id in pair:
            sim.events.append({"introduction_id": intro_id, "member_id": member_id, "event": "introduction_response", "value": "yes", "missing_reason": None, "occurred_day": assigned + 1, "observed_day": assigned + 1})
        sim.events.append({"introduction_id": intro_id, "member_id": None, "event": "date_happened", "value": True, "occurred_day": assigned + 4, "observed_day": assigned + 4})
        if index == 0:
            for member_id in pair:
                sim.events.append({"introduction_id": intro_id, "member_id": member_id, "event": "second_meeting_intention", "value": "yes", "missing_reason": None, "occurred_day": assigned + 5, "observed_day": assigned + 5})
        elif index == 1:
            sim.events.append({"introduction_id": intro_id, "member_id": pair[0], "event": "second_meeting_intention", "value": "yes", "missing_reason": None, "occurred_day": assigned + 8, "observed_day": assigned + 8})
            sim.events.append({"introduction_id": intro_id, "member_id": pair[1], "event": "second_meeting_intention", "value": "yes", "missing_reason": None, "occurred_day": assigned + 5, "observed_day": assigned + 5})
    metrics = sim.metrics()
    assert metrics["dates"] == 3
    assert metrics["mutual_second_meeting_intention"] == 1
