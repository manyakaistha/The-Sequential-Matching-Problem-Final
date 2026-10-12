import json

def test_heuristic(edges):
    # edges = [(w, (u, v))]
    # standard blossom
    import networkx as nx
    g = nx.Graph()
    g.add_weighted_edges_from((u, v, w) for w, (u, v) in edges)
    return nx.max_weight_matching(g)
