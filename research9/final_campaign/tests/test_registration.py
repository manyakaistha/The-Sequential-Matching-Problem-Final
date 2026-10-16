"""In-memory source-bound stage mutations; no simulation outcomes."""
import copy,json,unittest
from research9.final_campaign import registration as r

class RegistrationTests(unittest.TestCase):
    def valid(self):
        asset=json.loads((r.BASE/'selected_model.json').read_text());split=json.loads((r.BASE/'split.json').read_text())
        arms=['G','Q6','P']+r.CANDIDATES[:4 if asset['probability_admitted'] else 3]
        seeds=split['validation'][:8];stage='R9_final_screen_v1'
        reg=dict(schema_version='R9-final-campaign-v1',status='frozen_execution_registration',execution_authorized=True,stage_id=stage,ordered_seed_list=seeds,families=r.FAMILIES,policy_ids=arms,policies=r.policy_specs(arms),source_manifest=r.source_manifest(),resource_forecast=r.CAPS,storage=r.STORAGE,analysis=r.ANALYSIS,active_days=60,followup_days=40,observation_cutoff=99)
        import itertools
        reg['cells']=[dict(stage_id=stage,seed=s,family=f,policy_id=a,cell_key=f'{stage}_{s}_{f}_{a}') for s,f,a in itertools.product(seeds,r.FAMILIES,arms)];reg['total_cells']=len(reg['cells']);reg['registration_sha256']=r.registration_hash(reg)
        return reg
    def test_valid_grid_and_failed_q_gate_disables_waiting(self):
        reg=self.valid();r.verify_registration(reg)
        if not json.loads((r.BASE/'selected_model.json').read_text())['probability_admitted']:self.assertNotIn('model_continuation',reg['policy_ids'])
    def test_resigned_mutations_rejected(self):
        for field,value in [('active_days',59),('observation_cutoff',59),('policy_ids',['G']),('total_cells',1),('execution_authorized',False)]:
            with self.subTest(field=field):
                reg=copy.deepcopy(self.valid());reg[field]=value;reg['registration_sha256']=r.registration_hash(reg)
                with self.assertRaises(ValueError):r.verify_registration(reg)
    def test_arbitrary_integer_roundtrip(self):
        seeds=json.loads((r.BASE/'final_seed_reservation.json').read_text())['seeds']
        self.assertEqual(seeds,json.loads(json.dumps(seeds)))
        self.assertEqual(len(set(seeds)),96)
        self.assertTrue(all(type(s)is int and 2**127<=s<2**128 for s in seeds))
if __name__=='__main__':unittest.main()
