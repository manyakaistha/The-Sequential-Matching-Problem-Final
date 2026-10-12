"""Prepare model-specific Antigravity subagent arguments; never spawn by shell.

The live director submits the returned payload to Antigravity's invoke_subagent.
No API credentials, simulations or experiment scheduling are performed here.
"""
import argparse
import json
import re
from pathlib import Path

ROUTING_PATH = Path(__file__).with_name("agent_routing.json")
PROFILE_CONTRACT = {
    "luna_low": ("flash_lite", "low"),
    "luna_medium": ("flash_lite", "medium"),
    "sol_medium": ("flash", "medium"),
    "sol_high": ("pro", "high"),
    "astra_high": ("pro", "high"),
}
TASK_GROUPS = {
    "luna_low": {"file_discovery", "bounded_read", "mechanical_checks"},
    "luna_medium": {"structured_extraction", "artifact_indexing"},
    "sol_medium": {"bounded_implementation", "implementation_review"},
    "sol_high": {"simulator_forensics", "algorithm_design", "predictive_research",
                 "statistical_design", "independent_statistics", "production_review",
                 "adversarial_review"},
    "astra_high": {"mathematical_proof", "dynamic_planning"},
}


def load_routing():
    routing = json.loads(ROUTING_PATH.read_text())
    allowed = {"low", "medium", "high"}
    if set(routing["allowed_reasoning_efforts"]) != allowed:
        raise ValueError("Routing must restrict efforts to low/medium/high")
    if routing["global_active_agent_limit"] != 4 or routing["child_active_agent_limit"] != 3:
        raise ValueError("Routing must respect four global slots including root")
    if routing["spawn_fork_turns"] != "none":
        raise ValueError("Explicit model overrides require a bounded context fork")
    if routing["silent_model_substitution"] or routing["child_spawning_allowed"]:
        raise ValueError("Silent substitution and nested spawning are disabled")
    director = routing["director"]
    if (director["model"], director["reasoning_effort"]) != PROFILE_CONTRACT["sol_medium"]:
        raise ValueError("Director model/effort must match the requested Flash/medium director policy")
    if set(routing["profiles"]) != set(PROFILE_CONTRACT):
        raise ValueError("Unexpected profile set; amend the routing contract explicitly")
    for name, profile in routing["profiles"].items():
        if (profile["model"], profile["reasoning_effort"]) != PROFILE_CONTRACT[name]:
            raise ValueError(f"Invalid profile {name}")
    expected_tasks = set().union(*TASK_GROUPS.values())
    if set(routing["tasks"]) != expected_tasks:
        raise ValueError("Unexpected task kinds; amend the routing contract explicitly")
    for profile_name, kinds in TASK_GROUPS.items():
        for kind in kinds:
            if routing["tasks"][kind]["profile"] != profile_name:
                raise ValueError(f"Task {kind} must use profile {profile_name}")
    expected_escalation = {
        "luna_low": ["luna_medium", "sol_medium"],
        "luna_medium": ["sol_medium"],
        "sol_medium": ["sol_high"],
        "sol_high": ["astra_high"],
        "astra_high": [],
    }
    if routing["escalation"] != expected_escalation or routing["escalations_per_task_max"] != 1:
        raise ValueError("Escalation policy must match the single-escalation contract")
    return routing


def build_spawn_args(task_kind, task_name, question, hypothesis, deliverable,
                     ownership, reviewer, *, active_agents, cpu_seconds=None,
                     escalation_profile=None, escalation_reason=None):
    """Construct a validated payload; caller must check live slots again at spawn."""
    routing = load_routing()
    if task_kind not in routing["tasks"]:
        raise ValueError(f"Unknown task kind: {task_kind}")
    if not isinstance(active_agents, int) or isinstance(active_agents, bool) or active_agents < 1:
        raise ValueError("active_agents must count the root and all live workers")
    if active_agents >= routing["global_active_agent_limit"]:
        raise ValueError("All global slots occupied; queue the task instead of spawning")
    if not isinstance(task_name, str) or not re.fullmatch(r"[a-z0-9_]+", task_name):
        raise ValueError("task_name must contain lowercase letters, digits or underscores")
    fields = {"question": question, "hypothesis": hypothesis, "deliverable": deliverable,
              "ownership": ownership, "reviewer": reviewer}
    if any(not isinstance(v, str) or not v.strip() for v in fields.values()):
        raise ValueError("Question, hypothesis, deliverable, ownership and reviewer are required")
    profile_name = routing["tasks"][task_kind]["profile"]
    escalation_note = ""
    if escalation_profile is not None:
        if escalation_profile not in routing["escalation"][profile_name]:
            raise ValueError("Unapproved escalation route")
        if not isinstance(escalation_reason, str) or not escalation_reason.strip():
            raise ValueError("Escalation needs a written reason")
        escalation_note = f"\nDirector-recorded single escalation: {profile_name} -> {escalation_profile}; {escalation_reason.strip()}"
        profile_name = escalation_profile
    elif escalation_reason is not None:
        raise ValueError("Escalation reason supplied without an escalation profile")
    profile = routing["profiles"][profile_name]
    budget = profile["suggested_cpu_seconds"] if cpu_seconds is None else cpu_seconds
    if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0:
        raise ValueError("CPU allowance must be a positive integer")
    message = (
        f"Task kind: {task_kind}.\nConcrete question: {question.strip()}\n"
        f"Falsifiable hypothesis: {hypothesis.strip()}\nDeliverable: {deliverable.strip()}\n"
        f"Exclusive ownership/read-only scope: {ownership.strip()}\nNamed reviewer: {reviewer.strip()}\n"
        f"Compute allowance: {budget} CPU seconds (work allowance; this helper does not enforce a timer).\n"
        f"Keep the response within about {profile['suggested_response_words_max']} words unless evidence requires more.\n"
        "Use only permitted observations; no new seed worlds, simulations, training or confirmation unless explicitly included in this work order.\n"
        "Preserve prior sealed packages and other owners' files. Distinguish observed evidence, deductions, approximations and unknowns.\n"
        "Do not spawn subagents; request additional delegation from the director. Report ambiguity or failure rather than silently changing model, effort or scope."
        + escalation_note
    )
    return {
        "task_name": task_name,
        "message": message,
        "fork_turns": routing["spawn_fork_turns"],
        "model": profile["model"],
        "reasoning_effort": profile["reasoning_effort"],
        "subagent_type": profile.get("subagent_type", "self"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-kind", required=True)
    parser.add_argument("--task-name", required=True)
    for name in ("question", "hypothesis", "deliverable", "ownership", "reviewer"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--active-agents", type=int, required=True)
    parser.add_argument("--cpu-seconds", type=int)
    parser.add_argument("--escalation-profile")
    parser.add_argument("--escalation-reason")
    args = parser.parse_args()
    try:
        payload = build_spawn_args(**vars(args))
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
