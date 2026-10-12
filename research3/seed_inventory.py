"""Read-only inventory of inherited seed evidence; never runs simulator episodes.
Usage: .venv/bin/python research3/seed_inventory.py
JSON seed keys and seed-bearing source lines are evidence; source mentions are
conservatively excluded even when execution cannot be established.
"""
import ast, collections, hashlib, json, re, statistics, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/research3/seed_inventory.json'
EXCLUDED_DIRS = {'.git', '.venv', '__pycache__', 'node_modules', 'research3'}

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def walk_seeds(x, found):
    if isinstance(x,dict):
        for k,v in x.items():
            if k=='seed' and isinstance(v,int): found.add(v)
            elif 'seed' in k and isinstance(v,list) and all(isinstance(z,int) for z in v): found.update(v)
            elif 'seed' in k and isinstance(v,dict):
                found.update(int(z) for z in v if str(z).isdigit())
            walk_seeds(v,found)
    elif isinstance(x,list):
        for v in x:walk_seeds(v,found)

def main():
    evidence=[]; observed=set(); mentioned=set(); skips=[]
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if not p.is_file() or any(part in EXCLUDED_DIRS for part in rel.parts):continue
        if rel.parts[:2]==('results','research3'):continue
        if p.suffix not in {'.json','.log','.txt','.py','.sh','.md'}:continue
        found=set(); lines=[]
        if p.suffix=='.json' and p.stat().st_size<=16*1024*1024:
            try:walk_seeds(json.loads(p.read_text()),found)
            except (ValueError,UnicodeError):pass
        else:
            # Large trace/calibration files are covered by small headers and archive
            # indices; no future state or simulator random outcomes are inspected.
            if p.stat().st_size>16*1024*1024:
                with p.open('rb') as f: txt=f.read(65536).decode(errors='replace')
                skips.append({'path':str(rel),'reason':'first 64 KiB only; archive metadata and episode rows supply seed inventory'})
            else:txt=p.read_text(errors='replace')
            found.update(int(s) for s in re.findall(r'"seed"\s*:\s*(\d+)',txt))
            if p.suffix in {'.py','.sh','.md'}:
                for n,line in enumerate(txt.splitlines(),1):
                    if not re.search(r'\bseeds?\b|generate\(|--seeds|seed_range|seed[0-9]',line):continue
                    local=set()
                    for lo,hi in re.findall(r'range\((\d+)\s*,\s*(\d+)\)',line):
                        if 0<int(hi)-int(lo)<=10000:local.update(range(int(lo),int(hi)))
                    local.update(int(z) for z in re.findall(r'generate\(\s*(\d+)',line))
                    for lo,hi in re.findall(r'(\d{3,})\s*[–—:]\s*(\d{3,})',line):
                        if 0<=int(hi)-int(lo)<=10000:local.update(range(int(lo),int(hi)+1))
                    # Explicit seed lists/defaults, not arbitrary numerical work factors.
                    if re.search(r'(?:seeds?\s*=|--seeds|--seed.*default=)',line):
                        local.update(int(z) for z in re.findall(r'\b\d{2,}\b',line) if int(z) not in {200,1024})
                    if local:mentioned.update(local);lines.append({'line':n,'seeds':sorted(local),'text':line.strip()[:250]})
        if found:observed.update(found)
        if found or lines:evidence.append({'path':str(rel),'observed_seed_keys':sorted(found),'source_mentions':lines})
    # Planned ranges in the inherited unverified round are excluded even without
    # complete raw records. Prior source/runtime tests and public snapshots too.
    conservative={42,81,20260926}|set(range(101,106))|set(range(201,206))|set(range(301,306))|set(range(1001,1009))|set(range(2001,2013))|set(range(3001,3041))|set(range(4001,4041))|set(range(5001,5021))|set(range(6001,6041))|set(range(20261000,20261010))
    excluded=observed|mentioned|conservative
    frozen=json.loads((ROOT/'results/extended/frozen_candidate.json').read_text())
    hashes={}
    for p,h in {**frozen['code_hashes'],**frozen['auxiliary_code_hashes']}.items():
        actual=digest(ROOT/p);hashes[p]={'expected':h,'actual':actual,'match':actual==h}
    rows=json.loads((ROOT/'results/extended/confirmation.json').read_text())['episodes']
    by=collections.defaultdict(lambda:collections.defaultdict(dict))
    for r in rows:by[r['policy']][r['seed']][r['variant']]=r['msmi_per_100_arrived_members']
    assert len(rows)==480 and all(r['valid'] for r in rows)
    assert all(len(v)==6 for s in by.values() for v in s.values())
    d=[statistics.mean(by['simple_fifo'][s].values())-statistics.mean(by['greedy'][s].values()) for s in sorted(by['greedy'])]
    m=statistics.mean(d);sd=statistics.stdev(d);se=sd/math.sqrt(len(d))
    try:
        from scipy.stats import t
        critical=float(t.ppf(.975,len(d)-1));pval=float(2*t.sf(abs(m/se),len(d)-1))
    except ImportError:critical=2.0226909200367604;pval=None
    obj={'scope':'Inherited pre-round artifacts and scripts; mentions excluded regardless uncertain execution. No new simulations.',
         'observed_seed_keys':sorted(observed),'source_mentioned_seeds':sorted(mentioned),'conservative_inherited_exclusions':sorted(conservative),'excluded_seeds':sorted(excluded),
         'reserved_guard_band':[1,10000],'fresh_partition_recommendation':{'training':[10001,10040],'screening':[11001,11012],'focused':[12001,12032],'selection':[13001,13020],'confirmation_reserve':[14001,14200]},
         'fresh_range_check':all(s not in excluded for lo,hi in [(10001,10040),(11001,11012),(12001,12032),(13001,13020),(14001,14200)] for s in range(lo,hi+1)),
         'frozen_hash_check':hashes,'prior_confirmation_independent_reconstruction':{'n':len(d),'rows':len(rows),'greedy':statistics.mean(statistics.mean(v.values()) for v in by['greedy'].values()),'simple_fifo':statistics.mean(statistics.mean(v.values()) for v in by['simple_fifo'].values()),'paired_effect':m,'paired_sd':sd,'ci95':[m-critical*se,m+critical*se],'two_sided_p':pval,'seed_differences':dict(zip(map(str,sorted(by['greedy'])),d))},
         'evidence':evidence,'partial_scan_caveats':skips,'private_world_caveat':'organise.py can generate unknown cryptographic seeds; no private organiser worlds are used by this study. Exhaustive historical seed knowledge cannot be established from current files.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({'excluded_count':len(excluded),'fresh_range_check':obj['fresh_range_check'],'hash_mismatches':[p for p,v in hashes.items() if not v['match']],'prior_confirmation':obj['prior_confirmation_independent_reconstruction']|{'seed_differences':'in artifact'}},indent=2))
if __name__=='__main__':main()
