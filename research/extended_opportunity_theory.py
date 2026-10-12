from fractions import Fraction as F
from extended_theory import Edge, Instance, ExactModel

def instances():
    forever = (100,) * 4
    yield Instance('nonseparable_reservation', 2, (0,) * 4, forever,
                   (Edge(0, 1, F(1, 2), end=0), Edge(2, 3, F(1, 2), end=0), Edge(0, 2, F(9, 10), start=1)),
                   'Each separate endpoint removal destroys the same future edge; summing penalties double-counts its loss.')

class ModifiedModel(ExactModel):
    def choose(self, state, policy):
        if policy == 'exact_dp': return self.optimal(state)[1]
        
        feasible = self.feasible(state)
        
        if policy == 'reservation_max':
            wait = self.static_value(next(self.transitions(state, ()))[1])
            adjusted = {}
            for eid, e in feasible:
                after = sum((p * self.static_value(s) for p, s in self.transitions(state, (eid,))), F(0))
                adjusted[eid] = e.reward - (wait - after)
            return self.static_matching(state, adjusted)
        # fallback 
        return super().choose(state, policy)

for i in instances():
    model = ModifiedModel(i)
    res = model.run()
    res2 = model.evaluate(model.initial, 'reservation_max')
    
    print(res['instance']['name'], "reservation:", res['policies']['reservation']['rational_reward'], 
          "reservation_max:", res2)
