"""Fail-closed validation of complete, reviewed execution registrations."""
import importlib.metadata
import math
from pathlib import Path
from .schema import CellKey, EXPECTED_SIX_FAMILIES, validate_registration_schema
from .fingerprints import digest, file_digest, registration_design


class RegistrationValidationError(ValueError):
    pass


class RegistrationValidator:
    def __init__(self, workspace_root=None):
        self.workspace_root = Path(workspace_root or Path(__file__).resolve().parents[2]).resolve()

    compute_sha256 = staticmethod(file_digest)

    def _path(self, relative):
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
            raise ValueError(f'Unsafe source path: {relative}')
        path = (self.workspace_root / relative).resolve()
        if not path.is_relative_to(self.workspace_root):
            raise ValueError(f'Unsafe source path: {relative}')
        return path

    def validate_executable_readiness(self, registration, manifest_path=None):
        ok, errors = validate_registration_schema(registration)
        if not ok:
            return False, errors
        errors = list(errors)
        def reject(message): errors.append(message)
        if registration['status'] != 'frozen_execution_registration':
            reject(f"Execution blocked: registration status is '{registration['status']}' (planning_only is not executable)")
        if registration['execution_authorized'] is not True:
            reject('Execution blocked: explicit execution authorization missing.')
        if registration['seed_freshness_certified'] is not True:
            reject('Execution blocked: seed_freshness_certified is False.')
        stages = {'P1_smoke','P2_train','P2_validation','P2a_pilot','P3_screen','P4_replication','P5_selection','P6_confirmation'}
        if registration['authorized_scope'] not in stages or registration['authorized_scope'] != registration['stage_id']:
            reject('Execution blocked: scope is not an empirical research stage or differs from stage_id.')
        if registration['registration_design_sha256'] != digest(registration_design(registration)):
            reject('Frozen registration design digest mismatch.')
        for relative_key, hash_key in [('freshness_evidence_path','freshness_evidence_sha256'),('amendment_path','amendment_sha256')]:
            try:
                path = self._path(registration[relative_key])
                if not path.is_file() or file_digest(path) != registration[hash_key]:
                    reject(f'Missing or changed admission evidence: {relative_key}')
            except (ValueError, OSError) as exc: reject(str(exc))
        try:
            import json
            evidence = json.loads(self._path(registration['freshness_evidence_path']).read_text())
            if evidence.get('status') != 'repository_visible_no_overlap' or evidence.get('unresolved_intersections') or evidence.get('intersections'):
                reject('Freshness evidence is not a closed repository-visible audit.')
            if registration['seed_inventory_hash'] != registration['freshness_evidence_sha256']:
                reject('Seed inventory/evidence identity mismatch.')
            certified = evidence.get('eligible_stages', {}).get(registration['stage_id'], [])
            if certified != registration['ordered_seed_list']:
                reject('Ordered seeds do not match closed freshness audit stage.')
        except (OSError, ValueError, TypeError) as exc: reject(f'Unreadable seed evidence: {exc}')
        sources = registration['source_manifest']
        if not isinstance(sources, dict) or not sources:
            reject('Execution blocked: source manifest is empty.')
            sources = {}
        for relative, expected in sources.items():
            try:
                path = self._path(relative)
                if not path.is_file() or file_digest(path) != expected:
                    reject(f'Source missing or changed after registration: {relative}')
            except (ValueError, OSError) as exc: reject(str(exc))
        for name, key in [('kit.py','kit_sha256'),('evaluate.py','evaluate_sha256')]:
            expected = registration['governing_simulator'].get(key)
            if sources.get(name) != expected:
                reject(f'{name} missing from source closure or governing simulator hash mismatch')
        for name in ('research7/runtime/runner.py','research7/runtime/recorder.py','research7/runtime/leases.py','research7/runtime/interfaces.py','research7/runtime/metrics.py','research7/registry/schema.py','research7/registry/validator.py'):
            if name not in sources: reject(f'Required runtime source not frozen: {name}')
        dependencies = registration['dependency_manifest']
        if not isinstance(dependencies, dict) or not {'numpy','scipy','networkx'}.issubset(dependencies):
            reject('Incomplete dependency version freeze.')
        else:
            for name, version in dependencies.items():
                try:
                    if importlib.metadata.version(name) != version: reject(f'Dependency changed: {name}')
                except importlib.metadata.PackageNotFoundError: reject(f'Dependency missing: {name}')
        assets = registration['inference_assets']
        if not isinstance(assets, dict):
            reject('Assets must be a path-to-sha256 manifest.'); assets = {}
        for relative, expected in assets.items():
            try:
                if file_digest(self._path(relative)) != expected: reject(f'Inference asset changed: {relative}')
            except (ValueError, OSError) as exc: reject(str(exc))
        policies = registration['policies']
        if not isinstance(policies, dict) or not policies:
            reject('Empty policy panel.'); policies = {}
        for ident, policy in policies.items():
            if not isinstance(policy, dict): reject(f'Invalid policy specification: {ident}'); continue
            config = policy.get('config')
            if not isinstance(config, dict) or config.get('id') != ident or policy.get('config_sha256') != digest(config):
                reject(f'Policy config identity mismatch: {ident}')
            entrypoint = policy.get('entrypoint', '')
            if not isinstance(entrypoint, str) or entrypoint.count(':') != 1:
                reject(f'Invalid frozen entrypoint: {ident}')
            elif entrypoint.split(':')[0].replace('.', '/')+'.py' not in sources:
                reject(f'Policy entrypoint missing from source closure: {ident}')
            if policy.get('execution_mode') not in ('trusted_inprocess', 'subprocess_json'):
                reject(f'Unsupported execution mode: {ident}')
        seeds = registration['ordered_seed_list']
        if not isinstance(seeds,list) or not seeds or any(type(s) is not int or s<0 for s in seeds) or len(seeds)!=len(set(seeds)):
            reject('Empty, duplicate or invalid ordered seed list.'); seeds=[]
        families = registration['families']
        cells = registration['cells']
        if not isinstance(cells,list) or not cells:
            reject('Execution blocked: registered grid is empty.'); cells=[]
        expected = {(s,f,p) for s in seeds for f in families for p in policies}
        actual=set(); hashes=set()
        key_fields = {'program_id','stage_id','seed','family','policy_id','config_sha256','source_tree_sha256','inference_assets_sha256','cell_key'}
        for cell in cells:
            if not isinstance(cell,dict) or set(cell)!=key_fields:
                reject('Malformed cell identity.'); continue
            if type(cell['seed']) is not int or cell['seed']<0:
                reject('Cell seed must be a nonnegative integer.'); continue
            triple = (cell['seed'],cell['family'],cell['policy_id'])
            if triple in actual or cell['cell_key'] in hashes: reject('Duplicate cell identity.')
            actual.add(triple); hashes.add(cell['cell_key'])
            if triple not in expected: reject('Cell is outside the frozen cross-product.')
            if cell['program_id']!=registration['program_id'] or cell['stage_id']!=registration['stage_id']:
                reject('Cell program/stage differs from registration.')
            if cell['config_sha256']!=policies.get(cell['policy_id'],{}).get('config_sha256'):
                reject('Cell config differs from policy freeze.')
            if cell['source_tree_sha256']!=digest(sources) or cell['inference_assets_sha256']!=digest(assets):
                reject('Cell source/assets differs from freeze.')
            key = CellKey(**{k:cell[k] for k in key_fields if k!='cell_key'})
            if key.cell_hash()!=cell['cell_key']: reject('Canonical cell digest mismatch.')
        if actual!=expected: reject('Frozen seed/family/policy grid is incomplete or has extra cells.')
        assignments = registration['shard_assignments']
        if not isinstance(assignments,dict) or set(assignments)!= {'mac-01'} or assignments.get('mac-01') != seeds:
            reject('Current execution contract requires one complete mac-01 seed shard.')
        caps = registration['resource_forecast']
        limits={'max_cpu_hours':160,'max_rss_gib':10,'max_output_gib':100,'max_attempt_cpu_seconds':3600,'max_attempt_wall_seconds':7200,'max_physical_attempts':100000}
        for name, maximum in limits.items():
            value = caps.get(name)
            if type(value) not in (int,float) or not math.isfinite(value) or not 0<value<=maximum:
                reject(f'Invalid/excessive positive resource cap: {name}')
        if type(caps.get('free_reserve_gib_min')) not in (int,float) or caps.get('free_reserve_gib_min',0)<30:
            reject('Free disk reserve must be at least 30 GiB.')
        reviews = registration['reviews']
        admitted=False
        for review in reviews:
            if review.get('status')!='approved': continue
            if review.get('scope')!=registration['authorized_scope'] or review.get('reviewed_design_sha256')!=registration['registration_design_sha256']:
                reject('Independent review scope/design differs from freeze.'); continue
            if review.get('reviewer') in review.get('developers',[]) or not review.get('reviewer'):
                reject('Independent reviewer/developer separation not established.'); continue
            try:
                path=self._path(review.get('path'))
                if not path.is_file() or file_digest(path)!=review.get('sha256'):
                    reject('Independent admission review bytes changed.'); continue
                import json
                body=json.loads(path.read_text())
                if body.get('status')!='approved' or body.get('reviewed_design_sha256')!=review['reviewed_design_sha256'] or body.get('scope')!=review['scope']:
                    reject('Admission document does not approve this frozen design.'); continue
                admitted=True
            except (ValueError,OSError,TypeError) as exc: reject(f'Invalid independent review evidence: {exc}')
        if not admitted: reject('Execution blocked: no hash-bound independent admission review.')
        return not errors,errors
