"""Trusted in-process adapter around the supplied simulator and policy."""

from __future__ import annotations

import copy
import json
import time
from dataclasses import dataclass, field
from typing import Any

from evaluate import validate_response
from kit import Simulator, generate
from policy import decide

from .metrics import action_payload, metrics_snapshot, outcome_funnel, pair_inspection, public_state
from .settings import SETTINGS


DECISION_HORIZON = 60
FOLLOWUP_DAYS = 40
SUPPORTED_POLICIES = ("greedy", "no_asks", "random")

PRESETS: dict[str, dict[str, Any]] = {
    "public-101-development": {
        "id": "public-101-development",
        "seed": 101,
        "variant": "development",
        "label": "Development / seed 101",
        "description": "The documented public preset used for the core walkthrough.",
    },
    "public-101-sparse": {
        "id": "public-101-sparse",
        "seed": 101,
        "variant": "sparse",
        "label": "Sparse zones / seed 101",
        "description": "A harder geography variant with more distinct zones.",
    },
    "public-101-cold-start": {
        "id": "public-101-cold-start",
        "seed": 101,
        "variant": "cold_start",
        "label": "Cold start / seed 101",
        "description": "Fewer hard fields are initially observable.",
    },
    "public-101-delayed": {
        "id": "public-101-delayed",
        "seed": 101,
        "variant": "delayed",
        "label": "Delayed dates / seed 101",
        "description": "Date events arrive later in the supplied simulator variant.",
    },
    "public-101-shift": {
        "id": "public-101-shift",
        "seed": 101,
        "variant": "shift",
        "label": "Preference shift / seed 101",
        "description": "The simulator changes soft-fit weights after generation.",
    },
    "public-101-drift": {
        "id": "public-101-drift",
        "seed": 101,
        "variant": "drift",
        "label": "Outcome drift / seed 101",
        "description": "The supplied acceptance process drifts after day 35.",
    },
}


def _feedback_key(item: dict[str, Any]) -> str:
    return json.dumps(item, sort_keys=True, separators=(",", ":"))


@dataclass(slots=True)
class DemoEngine:
    preset: dict[str, Any]
    policy: str
    sim: Simulator = field(init=False)
    phase: str = field(default="ask", init=False)
    memory: Any = field(default=None, init=False)
    events: list[dict[str, Any]] = field(default_factory=list, init=False)
    revision: int = field(default=0, init=False)
    recent_action: dict[str, Any] | None = field(default=None, init=False)
    created_at: float = field(default_factory=time.monotonic, init=False)
    last_used_at: float = field(default_factory=time.monotonic, init=False)
    retained_advance_results: dict[str, dict[str, Any]] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.sim = Simulator(generate(self.preset["seed"], 200, self.preset["id"], self.preset["variant"]))

    @property
    def complete(self) -> bool:
        return self.phase == "complete"

    def touch(self) -> None:
        self.last_used_at = time.monotonic()

    def _record(self, phase: str, day: int, event_type: str, payload: dict[str, Any]) -> None:
        self.events.append({
            "cursor": len(self.events) + 1,
            "day": day,
            "phase": phase,
            "event_type": event_type,
            "payload": copy.deepcopy(payload),
        })
        if len(self.events) > SETTINGS.max_events:
            overflow = len(self.events) - SETTINGS.max_events
            self.events = self.events[overflow:]
            for index, event in enumerate(self.events, start=1):
                event["cursor"] = index

    def _release_feedback(self, before: list[dict[str, Any]], phase: str, day: int) -> None:
        known = {_feedback_key(item) for item in before}
        for feedback in self.sim.receive_feedback():
            if _feedback_key(feedback) not in known:
                self._record(phase, day, "feedback_released", {"feedback": feedback})

    def _policy_request(self, phase: str) -> dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "phase": phase,
            "state": public_state(self.sim),
            "memory": copy.deepcopy(self.memory),
        }

    def _step_ask(self) -> dict[str, Any]:
        day = self.sim.day
        response = decide(copy.deepcopy(self._policy_request("ask")), self.policy)
        validate_response(response, "ask")
        asks = response["asks"]
        ask_results = self.sim.resolve_asks(copy.deepcopy(asks))
        self.memory = copy.deepcopy(response["memory"])
        self.phase = "match"
        payload = action_payload("ask", day, asks=asks, ask_results=ask_results)
        self.recent_action = payload
        self._record("ask", day, "policy_action", payload)
        return payload

    def _step_match(self) -> dict[str, Any]:
        day = self.sim.day
        before_feedback = self.sim.receive_feedback()
        response = decide(copy.deepcopy(self._policy_request("match")), self.policy)
        validate_response(response, "match")
        pairs = response["pairs"]
        self.sim.advance(copy.deepcopy(pairs))
        self.memory = copy.deepcopy(response["memory"])
        payload = action_payload("match", day, pairs=pairs)
        self.recent_action = payload
        self._record("match", day, "policy_action", payload)
        self._release_feedback(before_feedback, "match", self.sim.day)
        self.phase = "ask" if self.sim.day < DECISION_HORIZON else "followup"
        return payload

    def _step_followup(self) -> dict[str, Any]:
        before_feedback = self.sim.receive_feedback()
        day = self.sim.day
        self.sim.advance([])
        payload = action_payload("followup", day, pairs=[])
        self.recent_action = payload
        self._record("followup", day, "followup_advance", payload)
        self._release_feedback(before_feedback, "followup", self.sim.day)
        if self.sim.day >= DECISION_HORIZON + FOLLOWUP_DAYS:
            self.phase = "complete"
        return payload

    def step_once(self) -> dict[str, Any]:
        if self.complete:
            return self.recent_action or action_payload("complete", self.sim.day, pairs=[])
        backup = (copy.deepcopy(self.sim), self.phase, copy.deepcopy(self.memory), copy.deepcopy(self.events),
                  self.revision, copy.deepcopy(self.recent_action))
        try:
            if self.phase == "ask":
                payload = self._step_ask()
            elif self.phase == "match":
                payload = self._step_match()
            else:
                payload = self._step_followup()
        except Exception:
            self.sim, self.phase, self.memory, self.events, self.revision, self.recent_action = backup
            raise
        return payload

    def advance_steps(self, steps: int) -> dict[str, Any]:
        backup = (copy.deepcopy(self.sim), self.phase, copy.deepcopy(self.memory), copy.deepcopy(self.events),
                  self.revision, copy.deepcopy(self.recent_action))
        try:
            for _ in range(steps):
                self.step_once()
                self.revision += 1
        except Exception:
            self.sim, self.phase, self.memory, self.events, self.revision, self.recent_action = backup
            raise
        self.touch()
        return self.view()

    def view(self, run_id: str = "") -> dict[str, Any]:
        state = public_state(self.sim)
        state["demo_phase"] = self.phase
        state["outcome_funnel"] = outcome_funnel(self.sim)
        state["selected_pairs"] = [
            [intro["user_a"], intro["user_b"]]
            for intro in self.sim.introductions
            if intro["assigned_day"] == max(0, self.sim.day - 1)
        ]
        state["member_count"] = len(state["members"])
        metrics = metrics_snapshot(self.sim)
        return {
            "run_id": run_id,
            "revision": self.revision,
            "status": "complete" if self.complete else "running",
            "phase": self.phase,
            "day": self.sim.day,
            "decision_horizon": DECISION_HORIZON,
            "followup_days": FOLLOWUP_DAYS,
            "preset_id": self.preset["id"],
            "policy": self.policy,
            "synthetic": True,
            "state": state,
            "metrics": metrics,
            "recent_action": copy.deepcopy(self.recent_action),
        }

    def events_after(self, after: int, limit: int) -> tuple[list[dict[str, Any]], int, bool]:
        selected = [event for event in self.events if event["cursor"] > after][:limit]
        next_cursor = selected[-1]["cursor"] if selected else after
        has_more = any(event["cursor"] > next_cursor for event in self.events)
        return copy.deepcopy(selected), next_cursor, has_more

    def export(self, run_id: str) -> dict[str, Any]:
        view = self.view(run_id)
        return {
            "schema_version": "1.0.0",
            "synthetic": True,
            "run": {
                "run_id": run_id,
                "preset_id": self.preset["id"],
                "policy": self.policy,
                "revision": self.revision,
                "phase": self.phase,
                "day": self.sim.day,
                "decision_horizon": DECISION_HORIZON,
                "followup_days": FOLLOWUP_DAYS,
            },
            "public_settings": {
                "seed": self.preset["seed"],
                "variant": self.preset["variant"],
                "population_size": 200,
                "clarification_budget_units": 12,
                "hard_bundle_cost": 3,
                "soft_field_cost": 1,
            },
            "events": copy.deepcopy(self.events),
            "metrics": copy.deepcopy(view["metrics"]),
        }

    def inspect_member(self, member_id: str) -> dict[str, Any] | None:
        self.touch()
        return pair_inspection(self.sim, member_id)


def preset_config() -> list[dict[str, Any]]:
    return [copy.deepcopy(item) for item in PRESETS.values()]


def config_payload() -> dict[str, Any]:
    return {
        "build_version": SETTINGS.build_version,
        "synthetic": True,
        "presets": preset_config(),
        "policies": [
            {"id": "greedy", "label": "Greedy", "description": "Supplied retained baseline: clarify missing hard fields, then use shared soft answers."},
            {"id": "no_asks", "label": "No clarification", "description": "Supplied control that never spends the clarification budget."},
            {"id": "random", "label": "Random feasible", "description": "Supplied control that shuffles feasible edges on the same preset."},
        ],
        "limits": {
            "max_active_runs": SETTINGS.max_runs,
            "steps_per_advance": 4,
            "decision_horizon_days": DECISION_HORIZON,
            "followup_days": FOLLOWUP_DAYS,
            "population_size": 200,
        },
        "metric_definitions": [
            {"key": "assignments", "label": "Introductions assigned", "definition": "Valid introductions selected by the policy."},
            {"key": "mutual_acceptances", "label": "Mutual acceptances", "definition": "Both directional responses are yes."},
            {"key": "dates", "label": "Dates occurred", "definition": "The simulator records a first date."},
            {"key": "mutual_second_meeting_intention", "label": "Qualified MSMI", "definition": "Date within 30 days plus two yes responses within three days."},
            {"key": "coverage", "label": "Coverage", "definition": "Distinct served members divided by members arrived by decision day 59."},
        ],
    }
