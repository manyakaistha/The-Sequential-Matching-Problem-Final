"""Build a frozen candidate stage registration for Research 7."""

import argparse
import importlib.metadata
import json
from pathlib import Path
import sys

from .fingerprints import digest, file_digest, registration_design
from .schema import CellKey, EXPECTED_SIX_FAMILIES, EXPECTED_SIMULATOR_PARAMS


def build_candidate_registration(
    workspace: Path,
    stage_id: str = "P1_smoke",
    candidate_ids: list = None,
    seeds: list = None,
    program_id: str = "research7_20261012",
    freshness_rel: str = None,
    amendment_rel: str = None,
    max_cpu_hours: float = 4,
    max_output_gib: float = 3,
    workers: int = 6,
) -> dict:
    workspace = Path(workspace).resolve()
    candidate_ids = candidate_ids or ["Q1", "A1", "H1"]
    if seeds is None:
        if stage_id == "P2a_pilot":
            seeds = list(range(710001, 710013))
        else:
            seeds = list(range(700001, 700005))

    if freshness_rel is None:
        if stage_id == "P1_smoke":
            freshness_rel = "research7/audits/smoke_freshness_v2.json"
        else:
            freshness_rel = "research7/audits/program_freshness_audit.json"

    if amendment_rel is None:
        if stage_id == "P1_smoke":
            amendment_rel = "research7/audits/SMOKE_SCOPE.md"
        else:
            amendment_rel = "research7/audits/P2A_SCOPE.md"

    sources = {}
    paths = set(workspace.glob("*.py"))
    for d in ("research", "research2", "research3", "research4", "research5", "research6"):
        paths.update((workspace / d).rglob("*.py"))
    for d in ("research7/runtime", "research7/registry", "research7/policies"):
        paths.update((workspace / d).rglob("*.py"))
    for path in sorted(paths):
        if "__pycache__" in path.parts:
            continue
        sources[str(path.relative_to(workspace))] = file_digest(path)

    for name in ("requirements-research.lock.txt", "../requirements-research.lock.txt"):
        p = workspace / name
        if p.is_file() and not name.startswith("../"):
            sources[name] = file_digest(p)

    policies = {}
    for cid in candidate_ids:
        cfg = {"id": cid}
        if cid in ("G", "N", "R", "P", "K", "Q6"):
            entrypoint = "research7.policies.references:decide"
        else:
            entrypoint = f"research7.policies.{cid.lower()}:decide"
        policies[cid] = {
            "config": cfg,
            "config_sha256": digest(cfg),
            "entrypoint": entrypoint,
            "execution_mode": "subprocess_json",
            "command": [
                sys.executable,
                "-m",
                "research7.policies.cli_adapter",
                "--entrypoint",
                entrypoint,
                "--config",
                json.dumps(cfg, separators=(",", ":")),
            ],
        }

    assets = {}
    cells = []
    source_tree_sha256 = digest(sources)
    assets_sha256 = digest(assets)

    for seed in seeds:
        for family in EXPECTED_SIX_FAMILIES:
            for cid in candidate_ids:
                cfg_sha = policies[cid]["config_sha256"]
                key = CellKey(
                    program_id,
                    stage_id,
                    seed,
                    family,
                    cid,
                    cfg_sha,
                    source_tree_sha256,
                    assets_sha256,
                )
                cell_row = {
                    "program_id": program_id,
                    "stage_id": stage_id,
                    "seed": seed,
                    "family": family,
                    "policy_id": cid,
                    "config_sha256": cfg_sha,
                    "source_tree_sha256": source_tree_sha256,
                    "inference_assets_sha256": assets_sha256,
                    "cell_key": key.cell_hash(),
                }
                cells.append(cell_row)

    freshness_path = workspace / freshness_rel
    amendment_path = workspace / amendment_rel
    predecessor_path = workspace / "research7/PLANNING_MANIFEST.json"

    reg = {
        "schema_version": 1,
        "program_id": program_id,
        "stage_id": stage_id,
        "status": "frozen_execution_registration",
        "source_manifest": sources,
        "inference_assets": assets,
        "dependency_manifest": {
            name: importlib.metadata.version(name)
            for name in ("numpy", "scipy", "networkx")
        },
        "governing_simulator": dict(
            EXPECTED_SIMULATOR_PARAMS,
            kit_sha256=sources["kit.py"],
            evaluate_sha256=sources["evaluate.py"],
            python_version=sys.version,
            world_pool_id="evaluation",
            policy_execution_mode="subprocess_json_isolated",
        ),
        "policies": policies,
        "seed_inventory_hash": file_digest(freshness_path),
        "seed_freshness_certified": True,
        "ordered_seed_list": seeds,
        "families": list(EXPECTED_SIX_FAMILIES),
        "cells": cells,
        "selection_statistics": {
            "inferential": False,
            "scope": f"{stage_id}_candidate_integration",
            "primary": "qualified_MSMI_per100_arrived_by59",
            "allow_selection": False,
        },
        "shard_assignments": {"mac-01": seeds},
        "resource_forecast": {
            "max_cpu_hours": max_cpu_hours,
            "max_rss_gib": 10,
            "max_output_gib": max_output_gib,
            "free_reserve_gib_min": 30,
            "max_attempt_cpu_seconds": 90,
            "max_attempt_wall_seconds": 180,
            "max_physical_attempts": len(cells),
            "max_attempt_output_bytes": 32 * 1024**2,
            "workers": workers,
            "numerical_threads": 1,
        },
        "reviews": [],
        "predecessor_freeze_hash": file_digest(predecessor_path),
        "authorized_scope": stage_id,
        "execution_authorized": True,
        "freshness_evidence_path": freshness_rel,
        "freshness_evidence_sha256": file_digest(freshness_path),
        "amendment_path": amendment_rel,
        "amendment_sha256": file_digest(amendment_path),
        "registration_design_sha256": "",
    }
    reg["registration_design_sha256"] = digest(registration_design(reg))
    return reg


def attach_admission_review(
    reg: dict,
    review_path: Path,
    reviewer: str = "r7_live_critic",
    developers: list = None,
) -> dict:
    """Attaches an independent admission review to a pre-computed registration design."""
    developers = developers or ["coordinator", "candidate_developer"]
    review_data = json.loads(Path(review_path).read_text())

    # Verify review invariants
    if review_data.get("status") != "approved":
        raise ValueError(f"Review status is not approved: {review_data.get('status')}")
    if review_data.get("reviewed_design_sha256") != reg["registration_design_sha256"]:
        raise ValueError(
            f"Review design digest mismatch: expected {reg['registration_design_sha256']}, got {review_data.get('reviewed_design_sha256')}"
        )
    if review_data.get("scope") != reg["authorized_scope"]:
        raise ValueError(f"Review scope mismatch: {review_data.get('scope')} vs {reg['authorized_scope']}")

    workspace = Path(__file__).resolve().parents[2]
    rel_path = str(Path(review_path).resolve().relative_to(workspace))

    reg["reviews"] = [
        {
            "review_id": review_data.get("review_id", "R7-P1-CANDIDATE-SMOKE-INDEPENDENT-20261012"),
            "path": rel_path,
            "sha256": file_digest(review_path),
            "reviewer": reviewer,
            "developers": developers,
            "status": "approved",
            "scope": reg["authorized_scope"],
            "reviewed_design_sha256": reg["registration_design_sha256"],
        }
    ]
    return reg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--stage", default="P1_smoke")
    parser.add_argument("--seeds", default=None)
    parser.add_argument("--candidates", default="Q1,A1,H1")
    parser.add_argument("--freshness", default=None)
    parser.add_argument("--amendment", default=None)
    parser.add_argument("--max-cpu-hours", type=float, default=4)
    parser.add_argument("--max-output-gib", type=float, default=3)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--review", default=None)
    args = parser.parse_args()

    workspace = Path(__file__).resolve().parents[2]
    cands = [c.strip() for c in args.candidates.split(",") if c.strip()]
    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()] if args.seeds else None

    reg = build_candidate_registration(
        workspace,
        stage_id=args.stage,
        candidate_ids=cands,
        seeds=seeds,
        freshness_rel=args.freshness,
        amendment_rel=args.amendment,
        max_cpu_hours=args.max_cpu_hours,
        max_output_gib=args.max_output_gib,
        workers=args.workers,
    )

    if args.review:
        attach_admission_review(reg, Path(args.review))

    out_p = Path(args.output)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with out_p.open("w") as f:
        json.dump(reg, f, indent=2)
        f.write("\n")

    print(
        json.dumps(
            {
                "stage": reg["stage_id"],
                "cells": len(reg["cells"]),
                "candidates": cands,
                "design_sha256": reg["registration_design_sha256"],
                "reviews_attached": len(reg["reviews"]),
                "status": "approved_for_execution" if reg["reviews"] else "awaiting_independent_admission",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
