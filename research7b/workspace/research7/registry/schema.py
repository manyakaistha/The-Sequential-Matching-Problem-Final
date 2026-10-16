"""Registration schema definitions and validation for Research 7."""

from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple


class RegistrationStatus(str, Enum):
    PLANNING_ONLY = "planning_only"
    FROZEN_EXECUTION = "frozen_execution_registration"
    CLOSED = "closed"


@dataclass(frozen=True)
class CellKey:
    program_id: str
    stage_id: str
    seed: int
    family: str
    policy_id: str
    config_sha256: str
    source_tree_sha256: str
    inference_assets_sha256: str

    def as_tuple(self) -> Tuple[str, str, int, str, str, str, str, str]:
        return (
            self.program_id,
            self.stage_id,
            self.seed,
            self.family,
            self.policy_id,
            self.config_sha256,
            self.source_tree_sha256,
            self.inference_assets_sha256,
        )

    def canonical_string(self) -> str:
        return json.dumps(self.as_tuple(), separators=(",", ":"), allow_nan=False)

    def cell_hash(self) -> str:
        return hashlib.sha256(self.canonical_string().encode("utf-8")).hexdigest()


REQUIRED_REGISTRATION_FIELDS = {
    "schema_version",
    "program_id",
    "stage_id",
    "status",
    "source_manifest",
    "inference_assets",
    "dependency_manifest",
    "governing_simulator",
    "policies",
    "seed_inventory_hash",
    "seed_freshness_certified",
    "ordered_seed_list",
    "families",
    "cells",
    "selection_statistics",
    "shard_assignments",
    "resource_forecast",
    "reviews",
    "predecessor_freeze_hash",
    "authorized_scope",
    "execution_authorized",
    "freshness_evidence_path",
    "freshness_evidence_sha256",
    "amendment_path",
    "amendment_sha256",
    "registration_design_sha256",
}

EXPECTED_SIMULATOR_PARAMS = {
    "members_count": 200,
    "action_days": 60,
    "followup_days": 40,
    "total_days": 100,
    "max_ask_budget_per_day": 12,
    "hard_bundle_cost": 3,
    "soft_field_cost": 1,
}

EXPECTED_SIX_FAMILIES = [
    "development", "sparse", "cold_start", "delayed", "shift", "drift",
]

EXPECTED_SIX_BASELINES = [
    "G",
    "N",
    "R",
    "P",
    "K",
    "Q6",
]


@dataclass
class ExperimentRegistration:
    schema_version: int
    program_id: str
    stage_id: str
    status: str
    source_manifest: Dict[str, Any]
    inference_assets: Dict[str, Any]
    dependency_manifest: Dict[str, Any]
    governing_simulator: Dict[str, Any]
    policies: Dict[str, Any]
    seed_inventory_hash: str
    seed_freshness_certified: bool
    ordered_seed_list: List[int]
    families: List[str]
    cells: List[Dict[str, Any]]
    selection_statistics: Dict[str, Any]
    shard_assignments: Dict[str, Any]
    resource_forecast: Dict[str, Any]
    reviews: List[Dict[str, Any]]
    predecessor_freeze_hash: str
    authorized_scope: str
    execution_authorized: bool
    freshness_evidence_path: str
    freshness_evidence_sha256: str
    amendment_path: str
    amendment_sha256: str
    registration_design_sha256: str
    detached_signature: Optional[str] = None

    def canonical_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data.pop("detached_signature", None)
        return data

    def canonical_json(self) -> str:
        return json.dumps(self.canonical_dict(), sort_keys=True, allow_nan=False)

    def canonical_digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def validate_registration_schema(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Strictly validates a registration dictionary against Research 7 specifications."""
    errors = []

    # Check for missing required fields
    missing = REQUIRED_REGISTRATION_FIELDS - set(data.keys())
    if missing:
        errors.append(f"Missing required registration fields: {sorted(list(missing))}")

    # Check for unrecognized fields (excluding optional detached_signature)
    unrecognized = set(data.keys()) - REQUIRED_REGISTRATION_FIELDS - {"detached_signature"}
    if unrecognized:
        errors.append(f"Unrecognized fields in registration: {sorted(list(unrecognized))}")

    if errors:
        return False, errors

    # Check schema_version
    if data["schema_version"] != 1:
        errors.append(f"Unsupported schema_version: {data['schema_version']} (expected 1)")

    # Check status
    valid_statuses = [s.value for s in RegistrationStatus]
    if data["status"] not in valid_statuses:
        errors.append(f"Invalid status '{data['status']}', expected one of {valid_statuses}")

    # Governing simulator check
    sim = data.get("governing_simulator", {})
    if not isinstance(sim, dict):
        errors.append("governing_simulator must be a dictionary")
    else:
        for k, v in EXPECTED_SIMULATOR_PARAMS.items():
            if sim.get(k) != v:
                errors.append(f"governing_simulator[{k}] = {sim.get(k)}, expected {v}")
        if "kit_sha256" not in sim or not sim["kit_sha256"]:
            errors.append("governing_simulator missing kit_sha256")
        if "evaluate_sha256" not in sim or not sim["evaluate_sha256"]:
            errors.append("governing_simulator missing evaluate_sha256")

    # Families check
    fams = data.get("families", [])
    if fams != EXPECTED_SIX_FAMILIES:
        errors.append(f"families must match expected six benchmark families: {EXPECTED_SIX_FAMILIES}, got {fams}")

    # Seed freshness check
    if not isinstance(data.get("seed_freshness_certified"), bool):
        errors.append("seed_freshness_certified must be boolean")

    if type(data.get("execution_authorized")) is not bool:
        errors.append("execution_authorized must be boolean")

    # Resource forecast check
    rf = data.get("resource_forecast", {})
    if not isinstance(rf, dict):
        errors.append("resource_forecast must be a dictionary")
    else:
        req_rf = {"max_cpu_hours", "max_rss_gib", "max_output_gib", "free_reserve_gib_min"}
        if not req_rf.issubset(rf.keys()):
            errors.append(f"resource_forecast missing required fields: {req_rf - set(rf.keys())}")

    # Shard assignments check
    sa = data.get("shard_assignments", {})
    if not isinstance(sa, dict):
        errors.append("shard_assignments must be a dictionary")

    # Reviews check
    reviews = data.get("reviews", [])
    if not isinstance(reviews, list):
        errors.append("reviews must be a list of review objects")
    else:
        for idx, rev in enumerate(reviews):
            if not isinstance(rev, dict) or not {"review_id", "reviewer", "scope", "status"}.issubset(rev.keys()):
                errors.append(f"reviews[{idx}] missing required fields (review_id, reviewer, scope, status)")

    return len(errors) == 0, errors
