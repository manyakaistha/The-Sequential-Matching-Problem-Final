"""Fail-closed final grid, freeze, preserved-history and manifest verification."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results/extended'
FAMILIES = {'development', 'sparse', 'cold_start', 'delayed', 'shift', 'drift'}


def load(path):
    return json.loads(path.read_text())


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-manifest', action='store_true')
    args = parser.parse_args()
    frozen = load(RESULTS / 'frozen_candidate.json')
    for key in ('code_hashes', 'auxiliary_code_hashes'):
        for name, expected in frozen[key].items():
            assert digest(ROOT / name) == expected, name
    development = load(RESULTS / 'development.json')
    assert digest(ROOT / 'research/extended_policy_development.py') == development['code_hashes']['extended_policy.py']
    for name, expected in development['code_hashes'].items():
        if name != 'extended_policy.py':
            assert frozen['code_hashes'][name] == expected, name
    grids = {}
    for name, seeds, count in (('development', range(1001, 1009), 22),
                               ('selection', range(2001, 2013), 7),
                               ('confirmation', range(3001, 3041), 2)):
        raw = load(RESULTS / (name + '.json'))
        rows = raw['episodes']
        policies = {r['policy'] for r in rows}
        expected = {(p, f, s) for p in policies for f in FAMILIES for s in seeds}
        actual = {(r['policy'], r['variant'], r['seed']) for r in rows}
        assert len(policies) == count and len(rows) == len(expected) and actual == expected, name
        assert raw['complete'] and raw['planned_episodes'] == len(rows), name
        assert all(r['valid'] and r.get('failures', 0) == 0 for r in rows), name
        if name != 'development':
            assert raw['code_hashes'] == frozen['code_hashes'], name
        grids[name] = dict(episodes=len(rows), seed_clusters=len(seeds), policies=count, valid=True)
    confirmation = load(RESULTS / 'confirmation.json')
    assert {r['policy'] for r in confirmation['episodes']} == {'greedy', frozen['policy']}
    assert all(r['configuration'] == frozen['configuration'] for r in confirmation['episodes'] if r['policy'] == frozen['policy'])
    prior = load(ROOT / 'results/research/manifest.json')
    for name, expected in prior['hashes'].items():
        preserved = {'REPORT.md': 'research/REPORT_2026-10-07.md',
                     'docs/REFERENCES.md': 'research/REFERENCES_2026-10-07.md'}.get(name, name)
        assert digest(ROOT / preserved) == expected, preserved
    for document in (ROOT / 'REPORT.md', ROOT / 'research/EXTENDED_REPRODUCTION.md'):
        for target in re.findall(r'\]\(([^)]+)\)', document.read_text()):
            if '://' not in target and not target.startswith('#'):
                assert (document.parent / target.split('#')[0]).exists(), target
    if args.check_manifest:
        manifest = load(RESULTS / 'manifest.json')
        for category in ('files', 'artifacts'):
            for name, expected in manifest[category].items():
                path = ROOT / name
                assert path.stat().st_size == expected['bytes'] and digest(path) == expected['sha256'], name
        print('Manifest verified:', len(manifest['files']), 'sources and', len(manifest['artifacts']), 'artifacts')
    else:
        summary = dict(main_experiment_grids=grids, main_episodes=sum(r['episodes'] for r in grids.values()),
                       frozen_inference_and_auxiliary_hashes_match=True, prior_manifest_sources_and_archives_match=True,
                       report_links_exist=True, scope='No new rollout or statistical test; completed-package integrity only.')
        (RESULTS / 'final_integrity.json').write_text(json.dumps(summary, indent=2) + '\n')
        print('Grid/freeze/history verification passed:', summary['main_episodes'], 'main episodes')


if __name__ == '__main__':
    main()
