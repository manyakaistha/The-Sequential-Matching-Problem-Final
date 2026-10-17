"""Typed HTTP boundary models for the public demonstration."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


PolicyName = Literal["greedy", "no_asks", "random"]
PhaseName = Literal["ask", "match", "followup", "complete"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RunCreate(StrictModel):
    preset_id: str = Field(min_length=1, max_length=80)
    policy: PolicyName = "greedy"


class AdvanceRequest(StrictModel):
    expected_revision: int = Field(ge=0)
    steps: int = Field(default=1, ge=1, le=4)
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=120)

    @field_validator("idempotency_key")
    @classmethod
    def no_control_characters(cls, value: str | None) -> str | None:
        if value is not None and any(ord(char) < 32 for char in value):
            raise ValueError("idempotency_key contains a control character")
        return value


class ConfigResponse(StrictModel):
    build_version: str
    synthetic: bool = True
    presets: list[dict[str, Any]]
    policies: list[dict[str, str]]
    limits: dict[str, int]
    metric_definitions: list[dict[str, str]]


class MetricsResponse(StrictModel):
    assignments: int = 0
    mutual_acceptances: int = 0
    dates: int = 0
    mutual_second_meeting_intention: int = 0
    missing_feedback: int = 0
    ask_cost: int = 0
    arrived_members: int = 0
    served_members: int = 0
    unserved_members: int = 0
    coverage: float = 0.0
    msmi_per_100_arrived_members: float = 0.0
    mutual_acceptances_per_100: float = 0.0
    first_introduction_wait_days: list[int] = Field(default_factory=list)
    status: str = "provisional"


class RunResponse(StrictModel):
    run_id: str
    revision: int
    status: Literal["running", "complete"]
    phase: PhaseName
    day: int
    decision_horizon: int = 60
    followup_days: int = 40
    preset_id: str
    policy: PolicyName
    synthetic: bool = True
    state: dict[str, Any]
    metrics: MetricsResponse
    recent_action: dict[str, Any] | None = None
    expires_in_seconds: int | None = None


class EventResponse(StrictModel):
    cursor: int
    day: int
    phase: str
    event_type: str
    payload: dict[str, Any]


class EventsResponse(StrictModel):
    run_id: str
    events: list[EventResponse]
    next_cursor: int
    has_more: bool


class ResearchSummaryResponse(StrictModel):
    synthetic: bool = True
    source: str
    note: str
    controls: dict[str, dict[str, Any]]


class ErrorResponse(StrictModel):
    error: dict[str, Any]
