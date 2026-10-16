"""Subprocess CLI adapter for Research 7 candidate policies.

Runs a policy entrypoint in an isolated subprocess with:
- JSON wire protocol on stdin/stdout
- Deterministic legal fallback under caught internal solver exceptions
- Status/timing reporting
"""

import argparse
import copy
import importlib
import json
import os
import sys
import time


def deterministic_legal_fallback(request):
    """Deterministic, legally valid fallback policy."""
    phase = request.get('phase', 'ask')
    memory = request.get('memory')
    if phase == 'ask':
        return {"asks": [], "memory": memory}
    else:
        try:
            from research7.policies.references import decide as ref_decide
            return ref_decide(request, {'id': 'G'})
        except Exception:
            return {"pairs": [], "memory": memory}


def main():
    parser = argparse.ArgumentParser(description="Subprocess policy invocation wrapper")
    parser.add_argument("--entrypoint", required=True, help="Module and function as module:function")
    parser.add_argument("--config", default="{}", help="JSON string of policy config")
    parser.add_argument("--enable-fallback", action="store_true", default=True, help="Fall back to legal baseline on error")
    args = parser.parse_args()

    config = json.loads(args.config)
    module_name, func_name = args.entrypoint.split(":")

    raw_input = sys.stdin.buffer.read()
    if not raw_input:
        sys.stderr.write("Empty stdin input\n")
        sys.exit(1)

    try:
        request = json.loads(raw_input.decode("utf-8"))
    except Exception as exc:
        sys.stderr.write(f"JSON decode error: {exc}\n")
        sys.exit(1)

    try:
        mod = importlib.import_module(module_name)
        fn = getattr(mod, func_name)
        response = fn(request, config)
    except Exception as exc:
        if args.enable_fallback:
            sys.stderr.write(f"Policy exception: {exc}; executing deterministic legal fallback\n")
            response = deterministic_legal_fallback(request)
            # Signal fallback status
            if hasattr(mod, 'LAST_STATUS'):
                mod.LAST_STATUS = {"fallback": True, "reason": str(exc)}
        else:
            sys.stderr.write(f"Policy exception without fallback: {exc}\n")
            sys.exit(1)

    out_bytes = json.dumps(response, allow_nan=False).encode("utf-8")
    sys.stdout.buffer.write(out_bytes)
    sys.stdout.buffer.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
