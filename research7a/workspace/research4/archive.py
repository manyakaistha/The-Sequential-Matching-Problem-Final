"""Lossless round-four raw trace archives with verified, non-overwriting restore."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path('results/research4')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as file:
        for block in iter(lambda:file.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def build():
    index = {'format': 'tar.gz regular files, repository relative paths', 'archives': []}
    for directory in sorted(ROOT.glob('*_traces')):
        if not directory.is_dir(): continue
        files = sorted(p for p in directory.rglob('*') if p.is_file())
        target = ROOT / (directory.name+'.tar.gz')
        if target.exists(): raise ValueError('refuse archive overwrite')
        members = [{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
        with tarfile.open(target, 'w:gz', compresslevel=6) as archive:
            for path in files: archive.add(path, arcname=str(path), recursive=False)
        index['archives'].append(dict(path=str(target), bytes=target.stat().st_size,
                                      sha256=sha(target), members=members))
    (ROOT/'archive_index.json').write_text(json.dumps(index,indent=2)+'\n')


def verify(restore=False):
    index=json.loads((ROOT/'archive_index.json').read_text())
    count=0
    for record in index['archives']:
        if sha(record['path']) != record['sha256']: raise ValueError('archive digest')
        expected={r['path']:r for r in record['members']}
        seen=set()
        with tarfile.open(record['path'],'r:gz') as archive:
            for member in archive:
                if member.name not in expected or member.name in seen or not member.isfile(): raise ValueError('unregistered member')
                path=Path(member.name)
                if path.is_absolute() or '..' in path.parts or not str(path).startswith('results/research4/'): raise ValueError('unsafe path')
                payload=archive.extractfile(member).read()
                r=expected[member.name]
                if len(payload)!=r['bytes'] or hashlib.sha256(payload).hexdigest()!=r['sha256']: raise ValueError('member digest')
                if restore and not path.exists():
                    path.parent.mkdir(parents=True,exist_ok=True)
                    with path.open('xb') as file: file.write(payload)
                if path.exists() and sha(path)!=r['sha256']: raise ValueError('existing bytes differ')
                seen.add(member.name);count+=1
        if seen!=set(expected): raise ValueError('missing member')
    print('Verified',len(index['archives']),'archives;',count,'members; existing differing bytes never overwritten')


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','verify','restore']);args=p.parse_args()
    if args.action=='build':build()
    else:verify(args.action=='restore')


if __name__=='__main__':main()
