"""Read-only historical metric audit; not an event-level certification.

Host-side evaluator only. Seed/family are clustering keys, never policy inputs.
Run from repository root; writes JSON to stdout and changes no source/result.
"""
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev
import hashlib
import json
import math


def run():
    from scipy.stats import t
    folder = Path('research7b/workspace/results/research7/research7_20261012/7b/P4_replication/commits')
    data, worlds, arms = {}, defaultdict(set), defaultdict(list)
    digest = hashlib.sha256()
    for path in sorted(folder.glob('*.json')):
        raw = path.read_bytes()
        digest.update(path.name.encode())
        digest.update(hashlib.sha256(raw).digest())
        row = json.loads(raw)
        cell, metric = row['cell'], row['metrics']
        key = cell['seed'], cell['family'], cell['policy_id']
        if key in data or not row['is_valid'] or not metric['valid']:
            raise ValueError('duplicate or invalid committed cell')
        denominator = metric['arrived_members']
        count = metric['mutual_second_meeting_intention']
        if type(denominator) is not int or denominator != 200 or type(count) is not int or count < 0:
            raise ValueError('unexpected count/denominator')
        endpoint = 100 * count / denominator
        if endpoint != metric['msmi_per_100_arrived_members']:
            raise ValueError('stored endpoint disagrees with count/denominator')
        data[key] = endpoint
        arms[key[2]].append(endpoint)
        worlds[key[:2]].add(metric['world_sha256'])
    seeds = sorted({key[0] for key in data})
    families = sorted({key[1] for key in data})
    expected_arms = {'A1', 'G', 'K', 'N', 'P', 'Q1', 'Q6', 'R'}
    expected_families = {'development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift'}
    if len(seeds) != 96 or set(arms) != expected_arms or set(families) != expected_families:
        raise ValueError('unexpected registered grid identities')
    expected = {(s, f, a) for s in seeds for f in families for a in expected_arms}
    if set(data) != expected or any(len(v) != 1 for v in worlds.values()):
        raise ValueError('incomplete grid or paired world mismatch')
    contrasts = {}
    for candidate, parent in [('Q6', 'G'), ('P', 'G'), ('A1', 'G'), ('Q1', 'Q6')]:
        differences = [mean(data[s, f, candidate] - data[s, f, parent] for f in families) for s in seeds]
        average = mean(differences)
        sd = stdev(differences)
        se = sd / math.sqrt(len(differences))
        half_width = float(t.ppf(.975, len(differences) - 1)) * se
        contrasts[candidate + '-' + parent] = {
            'mean': average, 'sd_seed_cluster': sd, 'se': se,
            'exploratory95ci': [average - half_width, average + half_width]}
    return {'scope': 'independent root reconstruction of commit metrics only; no public-event rederivation',
            'cells': len(data), 'clusters': len(seeds), 'all_denominators': 200,
            'arm_means': {a: mean(v) for a, v in sorted(arms.items())}, 'contrasts': contrasts,
            'input_commit_digest_sha256': digest.hexdigest(),
            'confidence_scope': 'unadjusted exploratory t intervals; no superiority/promotion decision'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
