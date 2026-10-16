"""Prospective independent high-half128-bit seeds with scoped visible checks."""
import hashlib,json,os,secrets
from pathlib import Path
from research8.soft_query_followup.v2.registration import ROOT,file_sha256,write_once
BASE=ROOT/'research9/final_campaign'

def main():
    target=BASE/'final_seed_reservation.json'
    if target.exists():raise ValueError('final seeds already reserved; no redraw')
    records=[];omissions=[]
    # Bounded textual metadata over code/research trees, plus explicit results indexes.
    paths=[]
    for dirname in ('research','research3','research4','research5','research6','research7','research7a','research7b','research8','research9'):
        root=ROOT/dirname
        if not root.exists():continue
        for directory,dirs,files in os.walk(root):
            dirs[:]=[d for d in dirs if not d.startswith('.') and d not in ('node_modules','__pycache__','evidence','history','workspace')]
            for name in files:
                p=Path(directory)/name
                if p.suffix in ('.json','.jsonl','.txt','.md','.py') and any(key in str(p.relative_to(root)).lower() for key in ('regist','reserv','seed','inventory','manifest','audit','plan','summary')):paths.append(p)
    for relative in ('results/research8/soft_query_followup/v2_replication/commits','results/research8/soft_query_followup/v2_replication/archive_manifests','results/research8/continuation_probe/v1/commits'):
        paths.extend((ROOT/relative).glob('*.json'))
    # Explicitly include archived workspace manifests omitted by general traversal.
    for relative in ('research7b/workspace/research7/registrations','research7a/workspace/research7/registrations','research6/audits'):
        paths.extend((ROOT/relative).glob('*.json'))
    blobs=[]
    for p in sorted(set(paths)):
        size=p.stat().st_size
        if p.is_symlink() or size>8*2**20:
            omissions.append({'path':str(p.relative_to(ROOT)),'bytes':size,'reason':'symlink or >8MiB bounded metadata read'});continue
        raw=p.read_bytes();records.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
        blobs.append(raw)
    accepted=[];rejected=[]
    while len(accepted)<96:
        seed=(1<<127)+secrets.randbits(127)
        if seed in accepted:
            rejected.append({'seed':seed,'reason':'duplicate random draw'});continue
        needle=str(seed).encode()
        hit=next((r['path'] for r,b in zip(records,blobs) if needle in b),None)
        if hit:
            rejected.append({'seed':seed,'reason':'exact decimal visible metadata overlap','path':hit});continue
        accepted.append(seed)
    result=dict(schema='r9-final-independent-seed-reservation-v1',status='reviewed_independent_random_draws',seeds=accepted,rejected_draws=rejected,draw='secrets.randbits(127)+2**127;96distinct prospective draws; no other redraw',scope='prospectively independently randomized seeds; checked repository-visible metadata nonoverlap; universal prior-use unverified',checked_metadata=records,omissions=omissions,additional_omissions=['historical raw/compressed episode payloads not exhaustively decoded; archive indexes only','unindexed/deleted/external/private history unresolved; prior externally deleted840001+ items not recovered','general metadata traversal prunes workspace/evidence/history; explicit later workspace registrations are separately included'],collision_bound='Conditional on fixed unseen historical set sizeB independent of these random draws: P(any overlap)<=96*B/2**127. B=1e12 would give<6e-25; that B is illustrative, not certified.',integer_contract='allseedoperationsPythonint/JSONinteger; no NumPyint64,float,JSNumber conversion',review_receipt='reviews/seed_randomization_review.md')
    write_once(target,result)
    print(json.dumps({'reserved':96,'checked_metadata_files':len(records),'omissions':len(omissions),'rejected_draws':len(rejected),'scope':result['scope']}))
if __name__=='__main__':main()
