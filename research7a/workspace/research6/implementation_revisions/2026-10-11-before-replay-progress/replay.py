"""Replay recorded requests; ordered actions, memory, semantic and wire equality."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from research6.recorder import sha, write_new


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--commit',required=True)
    parser.add_argument('--output',required=True);parser.add_argument('--mode',choices=('direct','subprocess','container'),default='direct')
    parser.add_argument('--image');args=parser.parse_args()
    row=json.loads(Path(args.commit).read_text())
    for source,expected in row['source_hashes'].items():
        if sha(source)!=expected: raise ValueError('replay source mismatch '+source)
    if not row['valid']:raise ValueError('replay invalid committed attempt requires separate error audit')
    root=Path(args.output);root.mkdir(parents=True,exist_ok=False)
    public=Path(row['attempt_path'])/'public';results=[]
    for request_path in sorted(public.glob('*.request.json.gz')):
        with gzip.open(request_path,'rt') as stream:request=json.load(stream)
        prefix=request_path.name.split('.')[0]
        with gzip.open(public/(prefix+'.response.json.gz'),'rt') as stream:expected=json.load(stream)
        raw=request['wire_utf8'].encode();started=time.monotonic()
        stderr=b''
        if args.mode=='direct':
            from research6.policies.policy import decide
            actual=decide(json.loads(raw),row['config']);wire=json.dumps(actual,allow_nan=False).encode()
        else:
            if args.mode=='container':
                if not args.image:parser.error('container requires --image')
                import evaluate
                command=evaluate.docker_command(args.image)+['--candidate',row['policy']]
            else:command=[sys.executable,'-m','research6.policies.policy','--candidate',row['policy']]
            process=subprocess.run(command,input=raw,capture_output=True,timeout=10)
            stderr=process.stderr;wire=process.stdout
            if process.returncode:raise ValueError('replay process failed '+stderr.decode(errors='replace'))
            actual=json.loads(wire)
        elapsed=time.monotonic()-started
        key='asks' if request['request']['phase']=='ask' else 'pairs'
        def semantic(action):
            return sorted((sorted(pair) if key=='pairs' else pair for pair in action),key=lambda x:json.dumps(x,sort_keys=True))
        result={'sequence':request['sequence'],'mode':args.mode,'elapsed_seconds':elapsed,
                'ordered_equal':actual[key]==expected['response'][key],
                'memory_equal':actual['memory']==expected['response']['memory'],
                'semantic_equal':semantic(actual[key])==semantic(expected['response'][key]),
                'literal_wire_equal':wire==expected['wire_utf8'].encode(),
                'stdout_sha256':hashlib.sha256(wire).hexdigest(), 'stderr_utf8':stderr.decode(errors='replace'),
                'stdout_utf8':wire.decode(), 'input_sha256':hashlib.sha256(raw).hexdigest()}
        write_new(root/(prefix+'.json'),result);results.append(result)
        if not all(result[k] for k in ('ordered_equal','memory_equal','semantic_equal')):
            raise ValueError('replay action/memory divergence; retained '+prefix)
    write_new(root/'summary.json',{'mode':args.mode,'invocations':len(results),'all_ordered_equal':all(r['ordered_equal'] for r in results),
              'all_semantic_equal':all(r['semantic_equal'] for r in results),
              'literal_wire_equal_count':sum(r['literal_wire_equal'] for r in results),
              'scope':'Recorded request replay, no new simulator episode or independent outcome cluster'})
    print(f'[replay] {len(results)} calls {args.mode} ordered/semantic equal; {root}',flush=True)


if __name__=='__main__':main()
