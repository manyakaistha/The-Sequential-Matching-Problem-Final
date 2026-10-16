"""Build a pre-data reference-only smoke freeze; independent approval is separate."""
import importlib.metadata
import json
from pathlib import Path
import sys
from .fingerprints import digest,file_digest,registration_design
from .schema import CellKey,EXPECTED_SIX_FAMILIES,EXPECTED_SIMULATOR_PARAMS


def build(workspace):
    workspace=Path(workspace).resolve()
    sources={}
    # Broad closure covers every installed historical Python source under the
    # inherited research packages, not just a handpicked direct import list.
    paths=set(workspace.glob('*.py'))
    for directory in ('research','research2','research3','research4','research5','research6'):
        paths.update((workspace/directory).rglob('*.py'))
    for directory in ('research7/runtime','research7/registry','research7/policies'):
        paths.update((workspace/directory).rglob('*.py'))
    for path in sorted(paths):
        if '__pycache__' in path.parts:continue
        sources[str(path.relative_to(workspace))]=file_digest(path)
    for name in ('requirements-research.lock.txt','../requirements-research.lock.txt'):
        path=workspace/name
        # Outer package lock copied as evidence by installer; only rooted paths frozen.
        if path.is_file() and not name.startswith('../'):sources[name]=file_digest(path)
    policies={p:dict(config={'id':p},config_sha256=digest({'id':p}),entrypoint='research7.policies.references:decide',execution_mode='trusted_inprocess') for p in ('G','N','R','P','K','Q6')}
    seeds=list(range(700001,700005));assets={};cells=[]
    for seed in seeds:
        for family in EXPECTED_SIX_FAMILIES:
            for ident in policies:
                key=CellKey('research7_20261012','P1_smoke',seed,family,ident,policies[ident]['config_sha256'],digest(sources),digest(assets))
                cells.append(dict(zip(('program_id','stage_id','seed','family','policy_id','config_sha256','source_tree_sha256','inference_assets_sha256'),key.as_tuple()),cell_key=key.cell_hash()))
    freshness='research7/audits/smoke_freshness_v2.json';amendment='research7/audits/SMOKE_SCOPE.md'
    reg=dict(schema_version=1,program_id='research7_20261012',stage_id='P1_smoke',status='frozen_execution_registration',source_manifest=sources,inference_assets=assets,dependency_manifest={name:importlib.metadata.version(name) for name in ('numpy','scipy','networkx')},governing_simulator=dict(EXPECTED_SIMULATOR_PARAMS,kit_sha256=sources['kit.py'],evaluate_sha256=sources['evaluate.py'],python_version=sys.version,world_pool_id='evaluation',policy_execution_mode='trusted_inprocess_non_sandbox'),policies=policies,seed_inventory_hash=file_digest(workspace/freshness),seed_freshness_certified=True,ordered_seed_list=seeds,families=list(EXPECTED_SIX_FAMILIES),cells=cells,selection_statistics={'inferential':False,'scope':'integration_smoke_only','primary':'qualified_MSMI_per100_arrived_by59','allow_selection':False},shard_assignments={'mac-01':seeds},resource_forecast={'max_cpu_hours':4,'max_rss_gib':10,'max_output_gib':3,'free_reserve_gib_min':30,'max_attempt_cpu_seconds':90,'max_attempt_wall_seconds':180,'max_physical_attempts':144,'max_attempt_output_bytes':32*1024**2,'workers':2,'numerical_threads':1},reviews=[],predecessor_freeze_hash=file_digest(workspace/'research7/PLANNING_MANIFEST.json'),authorized_scope='P1_smoke',execution_authorized=True,freshness_evidence_path=freshness,freshness_evidence_sha256=file_digest(workspace/freshness),amendment_path=amendment,amendment_sha256=file_digest(workspace/amendment),registration_design_sha256='')
    reg['registration_design_sha256']=digest(registration_design(reg))
    return reg


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();workspace=Path(__file__).resolve().parents[2];reg=build(workspace)
    with Path(args.output).open('x') as stream:json.dump(reg,stream,indent=2);stream.write('\n')
    print(json.dumps({'cells':len(reg['cells']),'source_files':len(reg['source_manifest']),'design_sha256':reg['registration_design_sha256'],'status':'awaiting_independent_admission'},indent=2))
if __name__=='__main__':main()
