"""Read-only repository-visible smoke seed audit, with explicit coverage limits."""
import argparse, ast, json, os, re, time
from pathlib import Path
from .fingerprints import file_digest
SEEDS=list(range(700001,700005))

def audit(root):
 root=Path(root).resolve();start=time.process_time();files=[];hits=[];gaps=[];raw=[];anchors=[]
 suffixes={'.py','.json','.jsonl','.md','.txt','.sh','.yaml','.yml','.toml','.csv','.tsv','.log'}
 def read(p,kind):
  if p.stat().st_size>64*1024*1024:
   gaps.append({'path':str(p.relative_to(root)),'reason':'exceeds declared 64MiB metadata limit'});return None
  files.append({'path':str(p.relative_to(root)),'sha256':file_digest(p),'bytes':p.stat().st_size,'kind':kind})
  return p.read_text(errors='replace')
 for base,dirs,names in os.walk(root):
  rel=Path(base).relative_to(root)
  dirs[:]=[d for d in dirs if d not in {'.git','.venv','__pycache__','node_modules','results','research7','research7a','research7b'} and not d.startswith('.') and not ('scratch' in rel.parts and 'research7' in d)]
  for name in names:
   p=Path(base)/name
   if p.suffix not in suffixes and not name.startswith('Dockerfile'):continue
   if 'scratch' in rel.parts and 'research7' in str(rel/p.name):continue
   text=read(p,'historical_source_declarations')
   if text is None:continue
   for seed in SEEDS:
    for match in re.finditer(r'(?<![\w.])'+str(seed)+r'(?!\w)',text):
     line=text.count('\n',0,match.start())+1;hits.append({'path':str(p.relative_to(root)),'line':line,'seed':seed,'context':text.splitlines()[line-1][:400]})
   if p.suffix=='.py':
    try:
     tree=ast.parse(text)
     for call in ast.walk(tree):
      if isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='range' and 1<=len(call.args)<=3:
       try:args=[ast.literal_eval(a) for a in call.args]
       except (ValueError,TypeError):continue
       if all(type(a) is int for a in args):
        overlap=[s for s in SEEDS if s in range(*args)]
        if overlap:hits.append({'path':str(p.relative_to(root)),'line':call.lineno,'range_args':args,'overlap':overlap})
    except SyntaxError as exc:gaps.append({'path':str(p.relative_to(root)),'reason':str(exc)})
 for base,dirs,names in os.walk(root/'results'):
  keep=[]
  for d in dirs:
   if d in {'attempts','commits','public','privileged','segments','production_smoke_context'} or 'traces' in d or d.endswith('_full'):
    raw.append({'path':str((Path(base)/d).relative_to(root)),'coverage':'preserved inventory/registration/archive-index; raw payload not reparsed'})
   else:keep.append(d)
  dirs[:]=keep
  for name in names:
   p=Path(base)/name
   if p.suffix not in {'.json','.jsonl','.md','.txt','.log'}:continue
   text=read(p,'historical_result_metadata')
   if text is None:continue
   for seed in SEEDS:
    for match in re.finditer(r'(?<![\w.])'+str(seed)+r'(?!\w)',text):
     line=text.count('\n',0,match.start())+1;hits.append({'path':str(p.relative_to(root)),'line':line,'seed':seed,'context':text.splitlines()[line-1][:400],'kind':'result_text_token'})
   if p.suffix!='.json':continue
   try:data=json.loads(text)
   except ValueError as exc:gaps.append({'path':str(p.relative_to(root)),'reason':str(exc)});continue
   def visit(v,keys=()):
    if isinstance(v,dict):
     for k,x in v.items():visit(x,keys+(str(k),))
    elif isinstance(v,list):
     for i,x in enumerate(v):visit(x,keys+(str(i),))
    elif type(v) is int and v in SEEDS and any('seed' in k.lower() for k in keys):hits.append({'path':str(p.relative_to(root)),'keys':keys,'seed':v})
   visit(data)
 for name in ('seed_inventory.json','seed_inventory_extended.json','seed_evidence_manifest.json','prior_artifact_index.json','seed_inventory_closure.json'):
  p=root/'research6/audits'/name
  if p.is_file():anchors.append({'path':str(p.relative_to(root)),'sha256':file_digest(p)})
  else:gaps.append({'path':str(p.relative_to(root)),'reason':'inherited evidence absent'})
 for rel,expected in [('results/research5/archive_index.json','7fce78beefa52c25cae8bcf2c6068bb796d146b35a55cc3bacafce8d509996e6'),('results/research5/raw_greedy.tar.gz','04c022a38dc9d3b739c9a8758a238e3b3a1f9cb014676544e1da85a345179d91')]:
  p=root/rel
  if not p.is_file():gaps.append({'path':rel,'reason':'historical closed anchor absent'});continue
  actual=file_digest(p);anchors.append({'path':rel,'sha256':actual,'bytes':p.stat().st_size})
  if actual!=expected:gaps.append({'path':rel,'reason':'historical closed anchor hash mismatch'})
 return {'status':'repository_visible_no_overlap' if not(hits or gaps) else 'needs_review','eligible_stages':{'P1_smoke':SEEDS},'conservative_prior_exclusion_guard':[1,699999],'intersections':hits,'unresolved_intersections':gaps,'scanned_files':files,'inherited_evidence':anchors,'raw_payload_coverage':raw,'scope':'Repository-visible historical source/declarations and result metadata; raw payloads reused by prior audited trace/archive coverage and registrations, not reparsed. All integers1-699999 conservatively excluded. Unknown historical external/private/deleted use outside certification. Current R7 prospective namespace is excluded from past-use scan based on user no-R7-use declaration.','external_declaration_path':'research7/audits/external_use_declaration.json','cpu_seconds':time.process_time()-start,'worlds_generated':0}

def main():
 p=argparse.ArgumentParser();p.add_argument('--repository-root',required=True);p.add_argument('--output',required=True);args=p.parse_args();d=audit(args.repository_root)
 with Path(args.output).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 print(json.dumps({k:d[k] for k in ('status','intersections','unresolved_intersections','cpu_seconds')},indent=2));print('scanned_files',len(d['scanned_files']))
if __name__=='__main__':main()
