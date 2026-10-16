"""One bounded audit pass plus public-only holding diagnostics; no second audit."""
from contextlib import contextmanager
from pathlib import Path
import hashlib,json,time
from statistics import mean
from research8.soft_query_followup.v2.registration import ROOT,write_once
from research8.soft_query_followup.v3 import audit
from research8.soft_query_followup.audit_efficiency.fast_audit import optimized_stream
from .registration import verify_registration

def holding_diagnostics(attempt,public):
    events=[];last=None
    with (attempt/'responses.jsonl').open() as stream:
        for line in stream:last=line
    if last:
        memory=json.loads(last)['response']['memory'] or {}
        events=memory.get('hold_events',[])
    actions={}
    interesting={e['day']+1 for e in events}
    with (attempt/'actions.jsonl').open() as stream:
        for line in stream:
            row=json.loads(line)
            if row['phase']=='match' and row['day'] in interesting:actions[row['day']]=row
    result=[]
    charged=set()
    for e in events:
        day=e['day'];pair=e['endpoints'];c=e['alternative'];row=actions[day+1]
        assert day<59 and len(pair)==2 and not charged.intersection(pair)
        charged.update(pair)
        assert e['new_score']>e['old_score']
        members={m['member_id']:m for m in row['request']['state']['members']}
        chosen={tuple(sorted(p)) for p in row['response']['pairs']}
        witness=tuple(sorted((e['held_endpoint'],c))) in chosen
        future=[i for i in public['introductions'] if i['assigned_day']>day]
        result.append(dict(e,alternative_available_next_day=members[c]['available'],witness_used_next_day=witness,original_pair_used_later=any({i['user_a'],i['user_b']}==set(pair) for i in future),held_endpoints_never_introduced_later=sum(not any(u in (i['user_a'],i['user_b']) for i in future) for u in pair)))
    return result

def main():
    base=ROOT/'research8/continuation_probe';out=ROOT/'results/research8/continuation_probe/v1'
    reg=json.loads((base/'registration.json').read_text());verify_registration(reg)
    original_attempt=audit._attempt;diagnostics={};function_times={}
    @contextmanager
    def observed_attempt(output,row):
        with original_attempt(output,row) as attempt:
            yield attempt
            public=json.loads((attempt/'final_public.json').read_text())
            diagnostics[row['cell']['cell_key']]=holding_diagnostics(attempt,public)
            function_times[row['cell']['cell_key']]=max(json.loads(line)['telemetry']['function_elapsed_seconds'] for line in (attempt/'invocations.jsonl').read_text().splitlines())
    audit._attempt=observed_attempt;audit._audit_stream=optimized_stream()[0]
    try:proof=audit.audit_campaign(out,reg)
    finally:audit._attempt=original_attempt
    commits={}
    for p in (out/'commits').glob('*.json'):
        r=json.loads(p.read_text());commits[r['cell']['cell_key']]=r
    parity=[]
    old=ROOT/'results/research8/soft_query_followup/v2_replication/commits'
    for r in commits.values():
        c=r['cell']
        if c['policy_id']=='Q6_parent':
            prior=json.loads((old/f"R8V2_development_replication_{c['seed']}_{c['family']}_Q6.json").read_text())
            assert all(r[k]==prior[k] for k in ('world_sha256','action_sha256','metrics','invocation_count','fallback_count'))
            parity.append(c['cell_key'])
    assert len(parity)==12
    summaries={}
    for arm in reg['policy_ids']:
        rows=[r for r in commits.values() if r['cell']['policy_id']==arm]
        summaries[arm]=dict(cells=len(rows),mean_msmi_per100=mean(r['metrics']['msmi_per_100_arrived_members'] for r in rows),qualified_pairs=sum(r['metrics']['mutual_second_meeting_intention'] for r in rows),mean_assignments=mean(r['metrics']['assignments'] for r in rows),max_cold_transport_seconds=max(r['invocation_seconds_max'] for r in rows),max_function_seconds=max(function_times[r['cell']['cell_key']] for r in rows),fallbacks=sum(r['fallback_count'] for r in rows))
    events=[e for rows in diagnostics.values() for e in rows]
    counts=dict(holds=len(events),potential_returns_observed=sum(e['alternative_available_next_day'] for e in events),witness_used_next_day=sum(e['witness_used_next_day'] for e in events),original_pair_used_later=sum(e['original_pair_used_later'] for e in events),held_endpoints_never_introduced_later=sum(e['held_endpoints_never_introduced_later'] for e in events))
    gate='mechanism_active_requires_further_development_not_superiority' if counts['holds'] and counts['witness_used_next_day'] else 'do_not_scale_this_frozen_rule_mechanism_gate_failed'
    report=dict(status='completed_audited_development_mechanism_probe',registration_sha256=reg['registration_sha256'],audit=proof,parent_exact_replays=len(parity),arm_summary=summaries,mechanism=counts,hold_events=diagnostics,decision=gate,inference_scope='two reused development seeds; no significance or policy superiority claim',commit_sha256={k:hashlib.sha256((out/'commits'/(k+'.json')).read_bytes()).hexdigest() for k in commits})
    write_once(base/'results.json',report)
    (base/'RESULTS.md').write_text('# Return-hold mechanism probe\n\n'+f"All24cells independently audited;12Q6parent replays exactly match prior actions and outcomes.\n\nDecision: {gate}.\n\n"+json.dumps(dict(arms=summaries,mechanism=counts),indent=2)+'\n\nThese are reused development worlds, not independent confirmation. No significance or superiority claim is supported by this probe.\n')
    print(json.dumps(dict(status=report['status'],decision=gate,arms=summaries,mechanism=counts),indent=2),flush=True)
if __name__=='__main__':main()
