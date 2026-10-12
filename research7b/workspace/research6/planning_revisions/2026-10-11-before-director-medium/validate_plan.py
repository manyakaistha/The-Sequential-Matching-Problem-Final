"""Read-only planning checks; never imports the simulator or evaluates policies.

Usage: .venv/bin/python research6/validate_plan.py
This is not the future research orchestrator or a completed policy test suite.
"""
import json
import math
import re
import sys
from pathlib import Path


def main():
    folder = Path(__file__).resolve().parent
    plan = json.loads((folder / "plan.json").read_text())
    checks = []

    def check(name, passed):
        checks.append({"name": name, "passed": bool(passed)})
        print(f"[{'PASS' if passed else 'FAIL'}] {name}", flush=True)

    check("planning only; zero new episodes", plan["status"] == "planning_not_execution_registration" and plan["new_policy_episodes_executed"] == 0)
    check("freshness remains an execution prerequisite", plan["seed_freshness_verified"] is False)
    ids = [c["id"] for c in plan["candidates"]]
    check("12 unique candidate/control IDs", len(ids) == len(set(ids)) == 12)
    check("two learning representatives", sum(c["kind"] == "learning" for c in plan["candidates"]) == 2)
    check("all six distinct shipped families", set(plan["families"]) == {"development", "sparse", "cold_start", "delayed", "shift", "drift"})
    partitions = plan["partitions"]
    seen = set()
    total = 0
    for name, spec in partitions.items():
        seeds = set(range(spec["first"], spec["last"] + 1))
        check(f"{name} proposed range is disjoint", bool(seeds) and not seeds & seen)
        seen.update(seeds)
        if name != "E_reserve":
            count = len(seeds) * len(plan["families"]) * spec["policies_max"]
            check(f"{name} maximum grid = {count}", count == spec["episodes_max"])
            total += count
    reserve = partitions["E_reserve"]
    check("E cap fits proposed reserve", reserve["used_n_max"] <= reserve["last"] - reserve["first"] + 1)
    e_count = reserve["illustrative_n"] * len(plan["families"]) * reserve["policies_max"]
    total += e_count
    check("E illustrative count = 5364", e_count == reserve["illustrative_episodes"] == 5364)
    check("illustrative whole grid = 17364", total == plan["illustrative_main_episodes_max"] == 17364)
    conf = plan["confirmation"]
    check("finite five-test alpha = .01", math.isclose(conf["program_alpha"] / conf["finite_program_comparisons"], conf["two_sided_alpha"]))
    check("registered primary confidence = .99", math.isclose(1 - conf["two_sided_alpha"], conf["ci_confidence"]))
    check("no repeated/extended confirmation", conf["comparisons_this_round_max"] == 1 and not conf["extend_after_results"])
    check("baseline/no-gain stopping", plan["selection"]["baseline_if_none"] and not plan["selection"]["unchanged_P_can_be_confirmed"])
    check("3 research workers / 4 total agent slots", plan["offline_workers"] == 3 and plan["global_agent_slots_including_director"] == 4)
    check("60 action + 40 follow-up days", plan["action_days"] == 60 and plan["follow_up_days"] == 40)
    check("full logging without privileged policy access", plan["logging"]["lossless_all_public_io"] and plan["logging"]["preserve_all_attempts"] and not plan["logging"]["privileged_policy_access"])
    sys.path.insert(0, str(folder.parent))
    from research6.agent_router import build_spawn_args, load_routing
    routing = load_routing()
    check("routing caps efforts at high", set(routing["allowed_reasoning_efforts"]) == {"low", "medium", "high"})
    examples = {
        "file_discovery": ("gpt-6-luna", "low"),
        "structured_extraction": ("gpt-6-luna", "medium"),
        "bounded_implementation": ("gpt-6.1-sol", "medium"),
        "statistical_design": ("gpt-6.1-sol", "high"),
        "mathematical_proof": ("gpt-6-astra", "high"),
    }
    for kind, expected in examples.items():
        payload = build_spawn_args(kind, "planning_check", "Bounded check?", "Check is possible.",
                                   "Evidence", "Read only", "/root", active_agents=1)
        check(f"{kind} model/effort and bounded context", (payload["model"], payload["reasoning_effort"]) == expected and payload["fork_turns"] == "none")
    rejected_full = False
    try:
        build_spawn_args("file_discovery", "planning_check", "Check?", "Test", "Evidence", "Read only", "/root", active_agents=4)
    except ValueError:
        rejected_full = True
    check("router rejects fifth active agent", rejected_full)
    check("live routing is separate from experiment runner", plan["agent_routing"]["live_delegation_configured"] and not plan["agent_routing"]["research_experiment_runner_implemented"])
    try:
        from scipy.stats import nct, t
    except ImportError:
        print("[UNVERIFIED] exact noncentral-t arithmetic: SciPy unavailable", flush=True)
        check("power arithmetic dependency available", False)
    else:
        sigma = conf["sd_floor"]
        minimum = next(n for n in range(2, reserve["used_n_max"] + 1)
                       if nct.sf(t.ppf(1 - conf["two_sided_alpha"] / 2, n - 1), n - 1,
                                 conf["planning_effect"] * math.sqrt(n) / sigma) >= conf["desired_power"])
        inflated = math.ceil(conf["sample_multiplier"] * minimum)
        check(f"normal-model power minimum {minimum}, inflated {inflated}", minimum == 406 and inflated == reserve["illustrative_n"])
    missing = []
    for document in folder.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            path = target.split("#", 1)[0].strip("<>")
            if path and not (document.parent / path).exists():
                missing.append({"document": document.name, "target": target})
    check("local document links exist", not missing)
    if missing:
        print(json.dumps(missing, indent=2))
    passed = all(c["passed"] for c in checks)
    print(json.dumps({"planning_checks_passed": passed, "checks": len(checks),
                      "policy_tests_executed": 0, "research_orchestrator_implemented": False,
                      "seed_freshness_certified": False}, indent=2), flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
