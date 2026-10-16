"""Unit tests for Research 7 coordinator registry, schema validation, and delegation limits."""

import json
from pathlib import Path
import tempfile
import unittest

from research7.registry.schema import (
    RegistrationStatus,
    validate_registration_schema,
    EXPECTED_SIX_FAMILIES,
    REQUIRED_REGISTRATION_FIELDS,
)
from research7.registry.validator import RegistrationValidator
from research7.registry.decisions import DecisionLedger
from research7.registry.delegations import DelegationManager, DelegationError


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Minimal valid registration dict
        self.valid_reg = {
            "schema_version": 1,
            "program_id": "r7-20261012-test",
            "stage_id": "B0",
            "status": RegistrationStatus.FROZEN_EXECUTION.value,
            "source_manifest": {"workspace/kit.py": "0d2cb3d3b46ca2a6ee7c8b74b78c55642ef98686e59a890ec18f66f2cabc1f3e"},
            "inference_assets": {},
            "dependency_manifest": {"numpy": "2.5.3", "scipy": "1.18.1", "networkx": "3.7"},
            "governing_simulator": {
                "members_count": 200,
                "action_days": 60,
                "followup_days": 40,
                "total_days": 100,
                "max_ask_budget_per_day": 12,
                "hard_bundle_cost": 3,
                "soft_field_cost": 1,
                "kit_sha256": "0d2cb3d3b46ca2a6ee7c8b74b78c55642ef98686e59a890ec18f66f2cabc1f3e",
                "evaluate_sha256": "d09cc14bf634a741515ad9965469821cac336a0d037b4da265eb1bf5fe20e162",
            },
            "policies": {"G": {"config_hash": "abc"}},
            "seed_inventory_hash": "audit123",
            "seed_freshness_certified": True,
            "ordered_seed_list": [700001, 700002],
            "families": list(EXPECTED_SIX_FAMILIES),
            "cells": [],
            "selection_statistics": {"alpha": 0.01},
            "shard_assignments": {"mac-01": [700001], "7a": [700002]},
            "resource_forecast": {
                "max_cpu_hours": 160,
                "max_rss_gib": 10,
                "max_output_gib": 100,
                "free_reserve_gib_min": 30,
            },
            "reviews": [
                {
                    "review_id": "REV-01",
                    "reviewer": "critic",
                    "scope": "B0 freeze",
                    "status": "approved",
                }
            ],
            "predecessor_freeze_hash": "none",
            "authorized_scope": "P0_P1_scaffolding_only",
            "execution_authorized": False,
            "freshness_evidence_path": "research7/audits/test.json",
            "freshness_evidence_sha256": "unused",
            "amendment_path": "research7/audits/test.md",
            "amendment_sha256": "unused",
            "registration_design_sha256": "unused",
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_schema_valid(self):
        ok, errors = validate_registration_schema(self.valid_reg)
        self.assertTrue(ok, f"Expected valid schema, got errors: {errors}")

    def test_schema_missing_fields(self):
        bad_reg = dict(self.valid_reg)
        del bad_reg["resource_forecast"]
        ok, errors = validate_registration_schema(bad_reg)
        self.assertFalse(ok)
        self.assertTrue(any("resource_forecast" in e for e in errors))

    def test_schema_unrecognized_fields(self):
        bad_reg = dict(self.valid_reg)
        bad_reg["unexpected_field"] = "foo"
        ok, errors = validate_registration_schema(bad_reg)
        self.assertFalse(ok)
        self.assertTrue(any("unexpected_field" in e for e in errors))

    def test_validator_blocks_planning_only_status(self):
        planning_reg = dict(self.valid_reg)
        planning_reg["status"] = RegistrationStatus.PLANNING_ONLY.value
        validator = RegistrationValidator()
        ok, errors = validator.validate_executable_readiness(planning_reg)
        self.assertFalse(ok)
        self.assertTrue(any("planning_only" in e for e in errors))

    def test_validator_blocks_uncertified_seeds(self):
        uncert_reg = dict(self.valid_reg)
        uncert_reg["seed_freshness_certified"] = False
        validator = RegistrationValidator()
        ok, errors = validator.validate_executable_readiness(uncert_reg)
        self.assertFalse(ok)
        self.assertTrue(any("seed_freshness_certified is False" in e for e in errors))

    def test_decision_ledger_append(self):
        ledger_file = self.root / "decisions.jsonl"
        ledger = DecisionLedger(ledger_file)
        rec = ledger.record_decision(
            phase="P0",
            author_role="director",
            decision_type="status_change",
            summary="Initialized P0 coordinator registry scaffolding",
        )
        self.assertTrue(ledger_file.exists())
        records = ledger.list_decisions()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].decision_id, rec.decision_id)
        self.assertEqual(records[0].summary, rec.summary)

    def test_delegation_manager_limits(self):
        ledger_file = self.root / "delegations.jsonl"
        manager = DelegationManager(ledger_file)

        # Developer / reviewer separation
        errors = manager.validate_delegation(
            task_id="T01",
            developer="alice",
            named_reviewer="alice",
            effort="medium",
            exclusive_ownership=["file1.py"],
            concrete_input_hashes={"in.txt": "sha123"},
            input_paths=["in.txt"],
        )
        self.assertTrue(any("Developer/reviewer separation violation" in e for e in errors))

        # Register up to 3 children (max allowed)
        for i in range(1, 4):
            manager.register_delegation(
                task_id=f"T0{i}",
                phase="P1",
                role_profile="implementation_medium",
                task_kind="bounded_implementation",
                developer=f"dev{i}",
                named_reviewer="critic",
                exclusive_ownership=[f"file{i}.py"],
                input_paths=["in.txt"],
                concrete_input_hashes={"in.txt": "sha123"},
                provider="codex",
                model="gpt-6.1-sol",
                effort="medium",
                cpu_seconds_allowance=120,
            )

        # 4th child must be rejected (global slot limit: root + 3 children = 4)
        with self.assertRaises(DelegationError) as ctx:
            manager.register_delegation(
                task_id="T04",
                phase="P1",
                role_profile="implementation_medium",
                task_kind="bounded_implementation",
                developer="dev4",
                named_reviewer="critic",
                exclusive_ownership=["file4.py"],
                input_paths=["in.txt"],
                concrete_input_hashes={"in.txt": "sha123"},
                provider="codex",
                model="gpt-6.1-sol",
                effort="medium",
                cpu_seconds_allowance=120,
            )
        self.assertIn("Global slot limit reached", str(ctx.exception))

        # Closing one task frees a slot
        manager.close_delegation("T01", outcome="completed_ok")
        # Now 4th can be registered
        rec4 = manager.register_delegation(
            task_id="T04",
            phase="P1",
            role_profile="implementation_medium",
            task_kind="bounded_implementation",
            developer="dev4",
            named_reviewer="critic",
            exclusive_ownership=["file4.py"],
            input_paths=["in.txt"],
            concrete_input_hashes={"in.txt": "sha123"},
            provider="codex",
            model="gpt-6.1-sol",
            effort="medium",
            cpu_seconds_allowance=120,
        )
        self.assertEqual(rec4.task_id, "T04")


if __name__ == "__main__":
    unittest.main()
