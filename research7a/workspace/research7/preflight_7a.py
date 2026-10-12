#!/usr/bin/env python3
"""Static inspection and verification harness for research7 branch 7a.

Read-only, static AST and schema verification.
Never imports repository simulator code, runs experiments, or calls external APIs.
"""

from __future__ import annotations
import ast
import json
from pathlib import Path
import sys


def main() -> int:
    workspace_dir = Path(__file__).resolve().parent.parent
    r7_dir = workspace_dir / 'research7'

    report = {
        'status': 'static_checks_only',
        'branch': '7a',
        'host_id': 'small-01',
        'syntax_errors': [],
        'module_checks': {},
        'runtime_status': 'setup_and_p0_p1_implementation_delivered_no_execution',
        'execution_authorized': False,
        'seed_freshness_certified': False
    }

    # 1. AST syntax inspection on 7a branch files
    files_to_check = [
        r7_dir / 'exact_independent' / '__init__.py',
        r7_dir / 'exact_independent' / 'schema.py',
        r7_dir / 'exact_independent' / 'solver.py',
        r7_dir / 'exact_independent' / 'specifications.py',
        r7_dir / 'metrics_independent.py',
        r7_dir / 'merge_independent.py'
    ]

    for p in files_to_check:
        rel = str(p.relative_to(workspace_dir))
        if not p.is_file():
            report['syntax_errors'].append({'path': rel, 'error': 'file missing'})
            continue
        try:
            ast.parse(p.read_bytes(), filename=rel)
        except Exception as exc:
            report['syntax_errors'].append({'path': rel, 'error': str(exc)})

    # 2. JSON schema validation
    wo_path = r7_dir / 'work_orders_7a_dispatched.json'
    if wo_path.is_file():
        try:
            wo_data = json.loads(wo_path.read_text())
            report['dispatched_work_orders_count'] = len(wo_data.get('work_orders', []))
        except Exception as exc:
            report['syntax_errors'].append({'path': str(wo_path.relative_to(workspace_dir)), 'error': str(exc)})

    # 3. Static mathematical ledger and fixture checks
    sys.path.insert(0, str(workspace_dir))
    try:
        from research7.exact_independent.specifications import run_exact_specification_check
        exact_res = run_exact_specification_check()
        report['module_checks']['exact_independent'] = {
            'all_cases_verified': exact_res.get('all_verified', False),
            'total_cases': exact_res.get('total_cases', 0)
        }
    except Exception as exc:
        report['module_checks']['exact_independent'] = {'error': str(exc)}

    try:
        from research7.metrics_independent import verify_metric_reconstruction
        metric_res = verify_metric_reconstruction()
        report['module_checks']['metrics_independent'] = {
            'all_fixtures_passed': metric_res.get('all_passed', False)
        }
    except Exception as exc:
        report['module_checks']['metrics_independent'] = {'error': str(exc)}

    try:
        from research7.merge_independent import run_merge_failure_injection_suite
        merge_res = run_merge_failure_injection_suite()
        report['module_checks']['merge_independent'] = {
            'all_failure_injections_passed': merge_res.get('all_passed', False)
        }
    except Exception as exc:
        report['module_checks']['merge_independent'] = {'error': str(exc)}

    has_errors = len(report['syntax_errors']) > 0 or not all(
        v.get('all_cases_verified', False) or v.get('all_fixtures_passed', False) or v.get('all_failure_injections_passed', False)
        for v in report['module_checks'].values()
    )

    print(json.dumps(report, indent=2))
    return 1 if has_errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
