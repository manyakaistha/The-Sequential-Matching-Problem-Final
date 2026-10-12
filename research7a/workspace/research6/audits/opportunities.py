"""Public-only examined-R4-screen graph audit; never generates worlds."""
import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import time
import networkx as nx
from kit import HARD, eligibility
from research6.policies.allocation import scored_edges, cardinality_matching, local_repair, stable_reranking
from kit import baseline_match


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--registration',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();reg=json.loads(Path(args.registration).read_text())
    root=Path(args.output);root.mkdir(parents=True,exist_ok=False)
    for source,expected in reg['source_hashes'].items():
        if hashlib.sha256(Path(source).read_bytes()).hexdigest()!=expected:raise ValueError('A source changed')
    rows=[];start=time.process_time()
    partial=(root/'public_graph_rows.jsonl').open('x')
    seen=set()
    for source,expected in reg['inputs'].items():
        raw=Path(source).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('examined input changed')
        trace=json.loads(raw)
        if trace['policy']!='greedy' or len(trace['match_states'])!=60:raise ValueError('unexpected source trajectory')
        for item in trace['match_states']:
            state=item['state']
            key=(trace['seed'],trace['variant'],state['day'])
            if key in seen or not 0<=state['day']<60:raise ValueError('duplicate/invalid state')
            seen.add(key)
            scores=scored_edges(state);g=baseline_match(state)
            k=cardinality_matching(scores);n1=local_repair(g,scores);n2=stable_reranking(scores,state['day'])
            available=[m for m in state['members'] if m['available']]
            eligible=[m for m in available if any(m['fields'][f] is None for f in HARD) and not any(m['field_status'][f]=='declined' for f in HARD)]
            verified=[m for m in available if all(m['fields'][f] is not None for f in HARD)]
            graph=nx.Graph();graph.add_nodes_from(m['member_id'] for m in verified);graph.add_edges_from(scores)
            first=Counter();second=Counter()
            for event in state['feedback']:
                if event['member_id'] and event['event']=='introduction_response':first[event['member_id']]+=1
                if event['member_id'] and event['event']=='second_meeting_intention':second[event['member_id']]+=1
            contention=sum(1 for u in graph if graph.degree(u)>1)
            tied_contention=sum(any(c>1 for c in Counter(scores[tuple(sorted((u,v)))] for v in graph[u]).values()) for u in graph)
            rows.append({'source':source,'seed':trace['seed'],'family':trace['variant'],'day':state['day'],
                'phase':'after_asks','available':len(available),'verified':len(verified),'query_eligible_remaining':len(eligible),
                'legal_unused_edges':len(scores),'component_sizes':sorted((len(c) for c in nx.connected_components(graph)),reverse=True),
                'degree_histogram':dict(Counter(dict(graph.degree()).values())), 'contended_endpoints':contention,
                'G_count':len(g),'K_count':len(k),'N1_count':len(n1),
                'G_shipped_score':sum(scores[tuple(p)] for p in g),
                'N1_shipped_score':sum(scores[tuple(p)] for p in n1),
                'N1_shipped_score_gap':sum(scores[tuple(p)] for p in n1)-sum(scores[tuple(p)] for p in g),
                'tied_contended_endpoints':tied_contention,
                'K_count_gap':len(k)-len(g),'N1_count_gap':len(n1)-len(g),
                'K_action_changed':{tuple(e) for e in k}!={tuple(e) for e in g},
                'N1_action_changed':{tuple(e) for e in n1}!={tuple(e) for e in g},
                'N2_action_changed':{tuple(e) for e in n2}!={tuple(e) for e in g},
                'available_first_history':dict(Counter(min(first[m['member_id']],2) for m in available)),
                'available_second_history':dict(Counter(min(second[m['member_id']],2) for m in available)),
                'selected_edges_with_second_history':sum(second[a]>0 or second[b]>0 for a,b in g),
                'declined_hard_available':sum(any(m['field_status'][f]=='declined' for f in HARD) for m in available)})
            partial.write(json.dumps(rows[-1])+'\n');partial.flush()
            if time.process_time()-start>reg['cpu_seconds_max']:raise RuntimeError('A budget reached; partial scope not certified')
        print(f'[A audit] {source} retained public states={len(rows)} cpu={time.process_time()-start:.1f}s',flush=True)
    partial.close()
    if len(rows)!=reg['expected_states'] or len(reg['inputs'])!=reg['expected_episodes']:raise ValueError('incomplete fixed audit grid')
    (root/'public_graph_rows.json').write_text(json.dumps(rows,indent=2)+'\n')
    stats={name:sum(r[name] for r in rows) for name in ('G_count','K_count','N1_count','G_shipped_score','N1_shipped_score','N1_shipped_score_gap','tied_contended_endpoints','K_count_gap','N1_count_gap','K_action_changed','N1_action_changed','N2_action_changed','available','verified','query_eligible_remaining','legal_unused_edges','contended_endpoints','selected_edges_with_second_history')}
    episodes=defaultdict(list)
    for r in rows:episodes[r['seed'],r['family']].append(r)
    summary={'scope':'Registered examined R4 B greedy post-ask states only; no privileged truth/new worlds/policy rollouts',
        'state_count':len(rows),'episode_count':len(episodes),'pooled_counts':stats,
        'episode_balanced_mean_counts':{name:sum(sum(r[name] for r in rs)/len(rs) for rs in episodes.values())/len(episodes) for name in stats},
        'cpu_seconds':time.process_time()-start,'registration_sha256':hashlib.sha256(Path(args.registration).read_bytes()).hexdigest()}
    (root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':main()
