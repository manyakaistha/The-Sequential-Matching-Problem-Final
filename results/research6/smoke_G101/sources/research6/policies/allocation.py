"""Fixed shipped-score allocation controls; no simulator or host state reads.

K requires NetworkX. N1 has two passes and 20,000 repair probes in total.
N2 changes exact integer-score ties only, with coherent endpoint priorities.
"""
import hashlib
import itertools

from kit import SOFT, baseline_asks, baseline_match, eligibility

SALT = 'research6-N2-public-v1'
PROBE_LIMIT = 20_000
PASSES = 2


def scored_edges(state):
    active = [m for m in state['members'] if m['available']]
    past = {tuple(sorted((i['user_a'], i['user_b'])))
            for i in state['introductions']}
    scores = {}
    for a, b in itertools.combinations(active, 2):
        pair = tuple(sorted((a['member_id'], b['member_id'])))
        if pair not in past and eligibility(a, b)['status'] == 'feasible':
            scores[pair] = sum(a['fields'].get(k) is not None and
                               a['fields'].get(k) == b['fields'].get(k)
                               for k in SOFT)
    return dict(sorted(scores.items()))


def cardinality_matching(scores):
    """Exact general-graph cardinality, then total shipped integer score."""
    import networkx as nx
    graph = nx.Graph()
    graph.add_nodes_from(sorted({u for pair in scores for u in pair}))
    for pair, score in sorted(scores.items()):
        graph.add_edge(*pair, weight=score)
    matching = nx.max_weight_matching(graph, maxcardinality=True, weight='weight')
    return sorted(tuple(sorted(pair)) for pair in matching)


def local_repair(initial, scores):
    """Only legal length-three augmentation and improving two-edge exchanges."""
    matching = {tuple(sorted(pair)) for pair in initial}
    vertices = sorted({u for pair in scores for u in pair})
    neighbors = {u: [] for u in vertices}
    for a, b in scores:
        neighbors[a].append(b)
        neighbors[b].append(a)
    probes = 0
    for _ in range(PASSES):
        changed = False
        for incumbent in sorted(matching):
            if incumbent not in matching:
                continue
            used = {u for pair in matching for u in pair}
            a, b = incumbent
            accepted = False
            for x in neighbors[a]:
                if x in used:
                    continue
                for y in neighbors[b]:
                    probes += 1
                    if probes > PROBE_LIMIT:
                        return sorted(matching)
                    if y in used or x == y:
                        continue
                    matching.remove(incumbent)
                    matching.update((tuple(sorted((a, x))), tuple(sorted((b, y)))))
                    changed = accepted = True
                    break
                if accepted:
                    break
        for first, second in itertools.combinations(sorted(matching), 2):
            if first not in matching or second not in matching:
                continue
            a, b = first
            c, d = second
            for proposed in (((a, c), (b, d)), ((a, d), (b, c))):
                probes += 1
                if probes > PROBE_LIMIT:
                    return sorted(matching)
                replacement = {tuple(sorted(pair)) for pair in proposed}
                if all(pair in scores for pair in replacement) and (
                        sum(scores[pair] for pair in replacement) >
                        scores[first] + scores[second]):
                    matching.difference_update((first, second))
                    matching.update(replacement)
                    changed = True
                    break
        if not changed:
            break
    return sorted(matching)


def stable_reranking(scores, day):
    block = day // 8
    priorities = {u: hashlib.sha256(
        f'{SALT}|{block}|{u}'.encode('utf-8')).hexdigest()
        for pair in scores for u in pair}
    def order(pair):
        return (-scores[pair], tuple(sorted(priorities[u] for u in pair)), pair)
    used, matching = set(), []
    for pair in sorted(scores, key=order):
        if not used.intersection(pair):
            matching.append(pair)
            used.update(pair)
    return matching


def action(request, config):
    state, ident = request['state'], config['id']
    if ident == 'P':
        from research4.candidates import CANDIDATES, decision
        return decision(request, dict(CANDIDATES['population_control']))
    if request['phase'] == 'ask':
        return {'asks': baseline_asks(state), 'memory': {}}
    if ident == 'G':
        return {'pairs': baseline_match(state), 'memory': {}}
    scores = scored_edges(state)
    if ident == 'K':
        pairs = cardinality_matching(scores)
    elif ident == 'N1':
        pairs = local_repair(baseline_match(state), scores)
    elif ident == 'N2':
        pairs = stable_reranking(scores, state['day'])
    else:
        raise ValueError('unknown allocation candidate')
    return {'pairs': [list(pair) for pair in pairs], 'memory': {}}
