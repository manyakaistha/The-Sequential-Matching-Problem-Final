"""Deterministically freeze registrations for Research 8 soft query trial."""

import hashlib
import json
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_cells(stage_id: str, seeds: list, families: list, policies: list) -> list:
    cells = []
    for s in seeds:
        for f in families:
            for p in policies:
                ck = f"{stage_id}_{s}_{f}_{p}"
                cells.append({
                    "stage_id": stage_id,
                    "seed": s,
                    "family": f,
                    "policy_id": p,
                    "cell_key": ck,
                })
    return cells


def build_registration(stage_id: str, seeds: list):
    families = ["development", "sparse", "cold_start", "delayed", "shift", "drift"]
    policy_ids = ["G", "G_random_soft", "G_targeted_soft"]

    tracked_sources = [
        "kit.py",
        "policy.py",
        "research8/soft_query_trial/policies/targeting.py",
        "research8/soft_query_trial/policies/g.py",
        "research8/soft_query_trial/policies/g_random_soft.py",
        "research8/soft_query_trial/policies/g_targeted_soft.py",
        "research8/soft_query_trial/policies/cli_adapter.py",
        "research8/soft_query_trial/runtime/metrics.py",
        "research8/soft_query_trial/runtime/runner.py",
        "research8/soft_query_trial/runtime/launcher.py",
        "research8/soft_query_trial/audits/seed_freshness_audit.json",
    ]

    source_manifest = {}
    for rel in tracked_sources:
        p = WORKSPACE_ROOT / rel
        if not p.is_file():
            raise FileNotFoundError(f"Missing tracked file: {rel}")
        source_manifest[rel] = file_sha256(p)

    cells = make_cells(stage_id, seeds, families, policy_ids)

    reg = {
        "schema_version": "1.0.0",
        "stage_id": stage_id,
        "status": "frozen_execution_registration",
        "execution_authorized": True,
        "seed_freshness_certified": True,
        "authorized_scope": stage_id,
        "ordered_seed_list": seeds,
        "families": families,
        "policy_ids": policy_ids,
        "cells": cells,
        "total_cells": len(cells),
        "source_manifest": source_manifest,
        "governing_simulator": {
            "kit_sha256": source_manifest["kit.py"],
            "version": "1.0.0",
        },
        "policies": {
            "G": {
                "entrypoint": "research8.soft_query_trial.policies.g:decide",
                "config": {"id": "G"},
                "description": "Frozen greedy hard query batch + greedy matching, no soft queries",
            },
            "G_random_soft": {
                "entrypoint": "research8.soft_query_trial.policies.g_random_soft:decide",
                "config": {"id": "G_random_soft", "salt": "research8_g_random_soft_v1"},
                "description": "Greedy hard batch + random eligible soft questions from candidate set C",
            },
            "G_targeted_soft": {
                "entrypoint": "research8.soft_query_trial.policies.g_targeted_soft:decide",
                "config": {"id": "G_targeted_soft"},
                "description": "Greedy hard batch + targeted eligible soft questions from candidate set C",
            },
        },
        "hypotheses": {
            "H1": "Soft-budget filling improves reward vs no soft-budget filling (G_targeted_soft vs G, G_random_soft vs G)",
            "H2": "Targeted soft-budget filling improves reward vs random eligible soft-budget filling (G_targeted_soft vs G_random_soft)",
        },
        "resource_forecast": {
            "max_workers": 3,
            "max_attempt_cpu_seconds": 90,
            "max_attempt_wall_seconds": 180,
            "max_rss_gib": 4.0,
            "free_reserve_gib_min": 10.0,
        },
    }

    reg_bytes = json.dumps(reg, sort_keys=True, indent=2).encode("utf-8")
    reg["registration_sha256"] = hashlib.sha256(reg_bytes).hexdigest()
    return reg


def main():
    reg_dir = Path(__file__).resolve().parent

    # Smoke: 4 seeds x 6 families x 3 arms = 72 cells
    smoke_seeds = [810001, 810002, 810003, 810004]
    smoke_reg = build_registration("R8_smoke", smoke_seeds)
    (reg_dir / "smoke.json").write_text(json.dumps(smoke_reg, indent=2, sort_keys=True) + "\n")
    print(f"Generated smoke.json: {len(smoke_reg['cells'])} cells, SHA256: {smoke_reg['registration_sha256']}")

    # Primary: 24 seeds x 6 families x 3 arms = 432 cells
    primary_seeds = list(range(820001, 820025))
    primary_reg = build_registration("R8_primary", primary_seeds)
    (reg_dir / "primary.json").write_text(json.dumps(primary_reg, indent=2, sort_keys=True) + "\n")
    print(f"Generated primary.json: {len(primary_reg['cells'])} cells, SHA256: {primary_reg['registration_sha256']}")


if __name__ == "__main__":
    main()
