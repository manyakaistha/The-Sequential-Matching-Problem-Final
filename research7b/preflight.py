#!/usr/bin/env python3
"""Read-only stdlib checks. Never imports repository policy/simulator code."""
import argparse, ast, hashlib, importlib.metadata, json, os, platform, shutil, subprocess, sys
from pathlib import Path

def main():
    if sys.version_info < (3, 10):
        print(json.dumps({'status':'unsupported_python','required':'Python >=3.10',
                          'actual':sys.version,'execution_authorized':False}), file=sys.stderr)
        return 1
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integrity-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args=parser.parse_args()
    package=Path(__file__).resolve().parent
    manifest=json.loads((package/'BUNDLE_MANIFEST.json').read_text())
    errors=[]; syntax=[]
    for entry in manifest['files']:
        relative=Path(entry['path'])
        target=package/relative
        if relative.is_absolute() or '..' in relative.parts or target.is_symlink() or not target.resolve().is_relative_to(package):
            errors.append({'path':entry['path'],'reason':'unsafe path'});continue
        if not target.is_file():
            errors.append({'path':entry['path'],'reason':'missing'});continue
        data=target.read_bytes()
        if len(data)!=entry['bytes'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:
            errors.append({'path':entry['path'],'reason':'size/hash mismatch'})
        if target.suffix=='.py':
            try: ast.parse(data,filename=entry['path'])
            except (SyntaxError,UnicodeDecodeError) as exc: syntax.append({'path':entry['path'],'reason':str(exc)})
    expected=hashlib.sha256((package/'BUNDLE_MANIFEST.json').read_bytes()).hexdigest()
    if (package/'BUNDLE_MANIFEST.sha256').read_text().split()[0]!=expected:errors.append({'path':'BUNDLE_MANIFEST.json','reason':'manifest checksum mismatch'})
    config=json.loads((package/'machine.json').read_text())
    report={'status':'static_checks_only','host':config['host_id'],'integrity_errors':errors,'syntax_errors':syntax,
            'checked_files':len(manifest['files']),'runtime_status':'pending_implementation_and_review',
            'execution_authorized':False,'seed_freshness_certified':False}
    dependency_errors=[]
    if not args.integrity_only:
        dependencies=[]
        for line in (package/'requirements-research.lock.txt').read_text().splitlines():
            if not line or line.startswith('#'):continue
            name,want=line.split('==',1)
            try: actual=importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError: actual=None
            ok=actual==want
            dependencies.append({'distribution':name,'required':want,'installed':actual,'ok':ok})
            if not ok:dependency_errors.append(name)
        memory=None
        if sys.platform=='darwin':
            try:memory=int(subprocess.check_output(['sysctl','-n','hw.memsize'],text=True,timeout=5).strip())
            except (OSError,ValueError,subprocess.SubprocessError):pass
        elif sys.platform.startswith('linux'):
            try:
                for line in Path('/proc/meminfo').read_text().splitlines():
                    if line.startswith('MemTotal:'):memory=int(line.split()[1])*1024
            except (OSError,ValueError):pass
        disk=shutil.disk_usage(package/'workspace')
        report.update(python=sys.version,platform=platform.platform(),architecture=platform.machine(),
                      cpu_count=os.cpu_count(),physical_memory_bytes=memory,free_disk_bytes=disk.free,
                      docker_executable_present=shutil.which('docker') is not None,dependencies=dependencies,
                      free_disk_reserve_met=disk.free>=config['free_reserve_GiB']*1024**3,
                      working_memory_cap_bytes=config['working_RSS_GiB_max']*1024**3,
                      hardware_note='Presence/capacity only; no workload, benchmark, Docker daemon call, or available-RAM guarantee.')
    if args.output:
        destination=args.output.resolve()
        allowed=(package/'setup_outputs').resolve()
        if not destination.is_relative_to(allowed):parser.error('--output must be under package/setup_outputs')
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if errors or syntax:return 1
    if dependency_errors or report.get('free_disk_reserve_met') is False:return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
