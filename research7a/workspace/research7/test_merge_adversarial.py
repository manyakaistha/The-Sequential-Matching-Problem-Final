"""Constructed fail-closed merge regression checks; no simulation."""
import copy
import unittest
from research7.merge_independent import IndependentMerger, compute_cell_key, run_merge_failure_injection_suite


class MergeAdversarial(unittest.TestCase):
    def setUp(self):
        self.commit = dict(program_id='p',stage_id='s',seed=1,family='f',policy_id='G',
                           config_sha256='cfg',source_tree_sha256='src',inference_assets_sha256='assets',
                           valid=True,action_sha256='action',primary_score=1)
        fields=('program_id','stage_id','seed','family','policy_id','config_sha256','source_tree_sha256','inference_assets_sha256')
        self.commit['cell_key']=compute_cell_key(*(self.commit[k] for k in fields))
        self.reg=dict(program_id='p',stage_id='s',expected_cell_keys=[self.commit['cell_key']],
                      expected_seeds=[1],expected_families=['f'],expected_policies=['G'])
        self.bundle=dict(bundle_id='b',host_id='h',lease=dict(revoked=False,expired=False),commits=[self.commit])

    def check_blocked(self,reg,bundles):
        result=IndependentMerger(reg).evaluate_bundles(bundles)
        self.assertFalse(result['can_produce_primary_analysis'])
        self.assertEqual(result['merged_index'],{})
        return result

    def test_builtin(self):
        result=run_merge_failure_injection_suite()
        self.assertTrue(result['all_passed'],result)

    def test_identical_invalid_transport_duplicates(self):
        self.commit.update(valid=False,error='timeout',primary_score=None)
        other=copy.deepcopy(self.bundle);other['bundle_id']='duplicate'
        row=self.check_blocked(self.reg,[self.bundle,other])
        self.assertTrue(any('invalidity' in e for e in row['integrity_errors']))

    def test_empty_registration(self):
        self.check_blocked({},[])
        self.check_blocked({},[self.bundle])
        self.reg['expected_cell_keys']=[]
        self.check_blocked(self.reg,[self.bundle])

    def test_metadata_mismatch_each_identity_component(self):
        for key in ('program_id','stage_id','seed','family','policy_id','config_sha256','source_tree_sha256','inference_assets_sha256'):
            with self.subTest(key=key):
                b=copy.deepcopy(self.bundle)
                b['commits'][0][key]=2 if key=='seed' else 'different'
                self.check_blocked(self.reg,[b])

    def test_missing_identity_or_validity(self):
        for key in ('source_tree_sha256','valid'):
            b=copy.deepcopy(self.bundle);del b['commits'][0][key]
            self.check_blocked(self.reg,[b])

    def test_nonidentical_diagnostic_is_conflict(self):
        b=copy.deepcopy(self.bundle);b['commits'][0]['diagnostic']='different'
        row=self.check_blocked(self.reg,[self.bundle,b])
        self.assertEqual(len(row['quarantined_conflicts']),1)

    def test_clean_duplicate(self):
        b=copy.deepcopy(self.bundle);b['bundle_id']='duplicate'
        row=IndependentMerger(self.reg).evaluate_bundles([self.bundle,b])
        self.assertTrue(row['can_produce_primary_analysis'],row)
        self.assertEqual(row['total_cells_authoritative'],1)


if __name__=='__main__': unittest.main()
