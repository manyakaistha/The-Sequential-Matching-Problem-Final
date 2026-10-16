"""Unit tests for analysis, row validation, and selection logic."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from research9.final_campaign import analyze


class AnalyzeUnitTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.output = Path(self.tmp.name)
        (self.output / 'commits').mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_rows_for_validation(self):
        reg = {
            'registration_sha256': 'fake_reg_sha',
            'source_manifest': {'fake/source.py': 'fake_sha'},
            'cells': [
                {'stage_id': 's1', 'seed': 1, 'family': 'F1', 'policy_id': 'G', 'cell_key': 'k1'},
                {'stage_id': 's1', 'seed': 1, 'family': 'F1', 'policy_id': 'P', 'cell_key': 'k2'},
            ],
        }
        # Missing commits
        with self.assertRaises(ValueError):
            analyze.rows_for(self.output, reg)

        # Write valid commit for k1
        row1 = {
            'cell': reg['cells'][0],
            'registration_sha256': 'fake_reg_sha',
            'source_sha256': reg['source_manifest'],
            'is_valid': True,
            'metrics': {'valid': True, 'msmi_per_100_arrived_members': 1.0, 'mutual_second_meeting_intention': 1, 'assignments': 10, 'coverage': 0.5},
            'error': None,
            'fallback_count': 0,
            'invocation_seconds_max': 0.1,
        }
        (self.output / 'commits' / 'k1.json').write_text(json.dumps(row1))

        # Still incomplete (k2 missing)
        with self.assertRaises(ValueError):
            analyze.rows_for(self.output, reg)

        # Write invalid commit for k2 (fallback_count > 0)
        row2_invalid = copy.deepcopy(row1)
        row2_invalid['cell'] = reg['cells'][1]
        row2_invalid['fallback_count'] = 1
        (self.output / 'commits' / 'k2.json').write_text(json.dumps(row2_invalid))
        with self.assertRaises(ValueError):
            analyze.rows_for(self.output, reg)

        # Fix k2 to be valid
        row2_valid = copy.deepcopy(row1)
        row2_valid['cell'] = reg['cells'][1]
        (self.output / 'commits' / 'k2.json').write_text(json.dumps(row2_valid))
        rows = analyze.rows_for(self.output, reg)
        self.assertEqual(set(rows.keys()), {'k1', 'k2'})

    def test_summarize_math(self):
        reg = {
            'policy_ids': ['G', 'model_greedy'],
            'families': ['F1', 'F2'],
            'ordered_seed_list': [1, 2],
        }
        rows = {}
        for s in [1, 2]:
            for f in ['F1', 'F2']:
                for a in ['G', 'model_greedy']:
                    score = 2.0 if a == 'model_greedy' else 1.0
                    rows[f"{s}_{f}_{a}"] = {
                        'cell': {'seed': s, 'family': f, 'policy_id': a},
                        'metrics': {
                            'msmi_per_100_arrived_members': score,
                            'mutual_second_meeting_intention': int(score * 10),
                            'assignments': 20,
                            'coverage': 0.8,
                        },
                        'fallback_count': 0,
                        'invocation_seconds_max': 0.05,
                    }
        values, summary = analyze.summarize(reg, rows)
        self.assertEqual(summary['G']['mean_msmi'], 1.0)
        self.assertEqual(summary['model_greedy']['mean_msmi'], 2.0)
        self.assertEqual(summary['G']['n_seed_clusters'], 2)
        self.assertEqual(summary['model_greedy']['n_seed_clusters'], 2)


if __name__ == '__main__':
    unittest.main()
