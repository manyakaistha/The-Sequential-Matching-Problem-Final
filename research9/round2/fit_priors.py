"""Fit empirical priors (theta 'emp') strictly from observable training data (data/public_*).

No private simulator traits, unobserved futures, or test seeds are accessed.
Fits:
- Beta prior for member response rate (method of moments across observed members).
- Soft field agreement probabilities (empirical marginal pairwise agreement).
- Acceptance model: logistic regression on soft feature agreement from observed intro feedback.
- Date occurrence probability and timing.
- Second-meeting intention response probability and 3-day on-time feedback probability.
- Hard constraint distributions (age offsets, gender preferences, smoking, children, zones, schedules)
  from questionnaires and observed profiles.
"""
import copy
import glob
import json
import math
from pathlib import Path
from collections import Counter, defaultdict

from kit import HARD, SOFT, GENDERS, OPTIONS
from .priors import sim_theta, flat_theta, write_builtin, HERE

WEIGHTED = ('relationship_goal', 'relationship_pace', 'lifestyle', 'conversations')


def _sigmoid(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def fit_empirical_priors(data_glob="data/public_*/state.json"):
    files = sorted(glob.glob(data_glob))
    if not files:
        raise FileNotFoundError(f"No files found matching {data_glob}")

    # Aggregators
    member_responses = defaultdict(lambda: [0, 0])  # member_id -> [responses, opportunities]
    member_ages = []
    age_min_offsets = []
    age_max_offsets = []
    who_to_meet_sizes = []
    gender_counts = Counter()
    rel_struct_counts = Counter()
    smoking_counts = Counter()
    partner_smoking_counts = Counter()
    has_children_list = []
    partner_children_counts = Counter()
    wants_children_counts = Counter()
    extra_zone_list = []
    extra_zone_choice_counts = Counter()
    schedule_sizes = []

    soft_values = defaultdict(list)  # field -> list of values
    
    acceptance_samples = []  # list of (phi, y) where phi is 4-vec of agreement (+1 / -0.5), y in {0, 1}
    date_opportunities = 0
    date_happened = 0
    date_within_30 = 0
    second_responses = 0
    second_on_time = 0
    second_samples = []  # list of (same_goal: bool, y in {0, 1})

    for path in files:
        state = json.loads(Path(path).read_text())
        members = {m['member_id']: m for m in state['members']}
        intros = {i['introduction_id']: i for i in state['introductions']}
        
        # 1. Member profile stats & Hard field priors
        for m in state['members']:
            age = m.get('age')
            if age is not None:
                member_ages.append(age)
            fields = m.get('fields', {})
            
            # Age offsets
            amin = fields.get('age_min')
            amax = fields.get('age_max')
            if age is not None and amin is not None:
                age_min_offsets.append(max(1, age - amin))
            if age is not None and amax is not None:
                age_max_offsets.append(max(1, amax - age))
                
            # who to meet
            wtm = fields.get('who_to_meet')
            if wtm is not None and isinstance(wtm, list):
                who_to_meet_sizes.append(len(wtm))
                for g in wtm:
                    gender_counts[g] += 1
            
            # Other hard fields
            if fields.get('relationship_structure') is not None:
                rel_struct_counts[fields['relationship_structure']] += 1
            if fields.get('smoking') is not None:
                smoking_counts[fields['smoking']] += 1
            if fields.get('partner_smoking') is not None:
                partner_smoking_counts[fields['partner_smoking']] += 1
            if fields.get('has_children') is not None:
                has_children_list.append(1 if fields['has_children'] else 0)
            if fields.get('partner_children') is not None:
                partner_children_counts[fields['partner_children']] += 1
            if fields.get('wants_children') is not None:
                wants_children_counts[fields['wants_children']] += 1
            if fields.get('acceptable_zones') is not None:
                zones = fields['acceptable_zones']
                if len(zones) > 1:
                    extra_zone_list.append(1)
                    for z in zones[1:]:
                        extra_zone_choice_counts[z] += 1
                else:
                    extra_zone_list.append(0)
            if fields.get('schedule') is not None:
                schedule_sizes.append(len(fields['schedule']))
                
            # Soft fields
            for k in SOFT:
                if fields.get(k) is not None:
                    soft_values[k].append(fields[k])

        # 2. Feedback & Response stats
        intro_feedback = defaultdict(list)
        for e in state.get('feedback', []):
            iid = e.get('introduction_id')
            if iid:
                intro_feedback[iid].append(e)

        for iid, events in intro_feedback.items():
            intro = intros.get(iid)
            if not intro:
                continue
            u_a, u_b = intro['user_a'], intro['user_b']
            
            # Introduction responses
            resp_events = [e for e in events if e.get('event') == 'introduction_response']
            for e in resp_events:
                mid = e.get('member_id')
                val = e.get('value')
                member_responses[mid][1] += 1
                if val in ('yes', 'no'):
                    member_responses[mid][0] += 1
                    
            # Mutual acceptance check
            mutual_yes = (len(resp_events) == 2 and all(e.get('value') == 'yes' for e in resp_events))
            
            # Acceptance training pairs
            m_a = members.get(u_a)
            m_b = members.get(u_b)
            if m_a and m_b:
                fa, fb = m_a.get('fields', {}), m_b.get('fields', {})
                # For each person who gave a response
                for e in resp_events:
                    val = e.get('value')
                    if val in ('yes', 'no'):
                        y = 1.0 if val == 'yes' else 0.0
                        phi = []
                        for k in WEIGHTED:
                            va, vb = fa.get(k), fb.get(k)
                            if va is not None and vb is not None:
                                phi.append(1.0 if va == vb else -0.5)
                            else:
                                phi.append(0.0)
                        acceptance_samples.append((phi, y))

            # Dates
            date_events = [e for e in events if e.get('event') == 'date_happened']
            if mutual_yes:
                date_opportunities += 1
                if date_events and any(e.get('value') is True for e in date_events):
                    date_happened += 1
                    occ = date_events[0].get('occurred_day')
                    ass = intro.get('assigned_day', 0)
                    if occ is not None and (occ - ass) <= 30:
                        date_within_30 += 1

            # Second meeting intentions
            sec_events = [e for e in events if e.get('event') == 'second_meeting_intention']
            for se in sec_events:
                second_responses += 1
                occ = se.get('occurred_day')
                # find date day
                d_day = date_events[0].get('occurred_day') if date_events else None
                if occ is not None and d_day is not None and (occ - d_day) <= 3:
                    second_on_time += 1
                val = se.get('value')
                if val in ('yes', 'no'):
                    y = 1.0 if val == 'yes' else 0.0
                    same_g = False
                    if m_a and m_b:
                        ga = m_a.get('fields', {}).get('relationship_goal')
                        gb = m_b.get('fields', {}).get('relationship_goal')
                        same_g = (ga is not None and gb is not None and ga == gb)
                    second_samples.append((1.0 if same_g else 0.0, y))

    # Response rate moments (debiased for binomial sampling noise)
    total_res = sum(r[0] for r in member_responses.values())
    total_opp = sum(r[1] for r in member_responses.values())
    m_rate = total_res / max(1, total_opp)
    
    # Use members with >= 2 opportunities to estimate latent variance
    multi_opps = [(r[0] / r[1], r[1]) for r in member_responses.values() if r[1] >= 2]
    if len(multi_opps) >= 10:
        sample_v = sum((p - m_rate) ** 2 for p, _ in multi_opps) / len(multi_opps)
        binom_v = sum(m_rate * (1 - m_rate) / n for _, n in multi_opps) / len(multi_opps)
        latent_v = max(0.008, sample_v - binom_v)
        term = max(1.0, m_rate * (1 - m_rate) / latent_v - 1)
        alpha_resp = m_rate * term
        beta_resp = (1 - m_rate) * term
    else:
        alpha_resp, beta_resp = 12.0, 3.5

    # Soft equal probabilities
    soft_equal_prob = {}
    for k in WEIGHTED:
        vals = soft_values[k]
        if vals:
            c = Counter(vals)
            tot = sum(c.values())
            # Probability two random draws from empirical distribution agree: sum p_i^2
            p_eq = sum((cnt / tot) ** 2 for cnt in c.values())
            soft_equal_prob[k] = round(p_eq, 4)
        else:
            soft_equal_prob[k] = 0.3333

    # Acceptance logistic regression (gradient descent with ridge prior)
    # y ~ sigmoid(b0 + w1*phi1 + w2*phi2 + w3*phi3 + w4*phi4)
    b0 = -0.2
    w = [0.5, 0.3, 0.2, 0.15]
    if acceptance_samples:
        for _ in range(50):
            gb0 = 0.0
            gw = [0.0] * 4
            for phi, y in acceptance_samples:
                logit = b0 + sum(wi * pi for wi, pi in zip(w, phi))
                p = _sigmoid(logit)
                err = y - p
                gb0 += err
                for j in range(4):
                    gw[j] += err * phi[j]
            # Ridge penalty toward 0
            n_samp = len(acceptance_samples)
            b0 += 0.01 * (gb0 / n_samp)
            for j in range(4):
                w[j] += 0.01 * (gw[j] / n_samp - 0.05 * w[j])

    # Date probabilities
    p_happen = (date_happened / date_opportunities) if date_opportunities > 0 else 0.75
    p_within30 = (date_within_30 / date_happened) if date_happened > 0 else 0.95

    # Second meeting parameters
    p_on_time = (second_on_time / second_responses) if second_responses > 0 else 0.60
    # Logistic for second meeting
    sb0 = 0.15
    s_goal = 0.4
    if second_samples:
        for _ in range(40):
            gsb0 = 0.0
            gs_goal = 0.0
            for same_g, y in second_samples:
                logit = sb0 + s_goal * same_g
                p = _sigmoid(logit)
                err = y - p
                gsb0 += err
                gs_goal += err * same_g
            n_s = len(second_samples)
            sb0 += 0.01 * (gsb0 / n_s)
            s_goal += 0.01 * (gs_goal / n_s - 0.05 * s_goal)

    # Helper for empirical discrete distribution
    def _dist(counts):
        tot = sum(counts.values())
        return {str(k): round(v / tot, 4) for k, v in sorted(counts.items())}

    def _offset_dist(offsets, min_v=3, max_v=10):
        c = Counter(offsets)
        tot = sum(c.values()) if c else 1
        return {str(k): round(c.get(k, 1) / (tot + (max_v - min_v + 1)), 4) for k in range(min_v, max_v + 1)}

    emp_theta = {
        'name': 'emp',
        'source': 'Fitted strictly from observable training data (data/public_*)',
        'soft_equal_prob': soft_equal_prob,
        'accept': {
            'intercept': round(b0, 4),
            'bias_sd': 0.65,
            'shared_sd': 0.45,
            'weights': {
                'relationship_goal': round(max(0.01, w[0]), 4),
                'relationship_pace': round(max(0.01, w[1]), 4),
                'lifestyle': round(max(0.01, w[2]), 4),
                'conversations': round(max(0.01, w[3]), 4),
            }
        },
        'response': {
            'alpha': round(alpha_resp, 4),
            'beta': round(beta_resp, 4),
        },
        'date': {
            'p_happen': round(p_happen, 4),
            'p_within30': round(p_within30, 4),
        },
        'second': {
            'intercept': round(sb0, 4),
            'goal_coef': round(max(0.05, s_goal), 4),
            'bias_sd': 0.5,
            'p_on_time': round(p_on_time, 4),
        },
        'hard': {
            'age_min_offset': _offset_dist(age_min_offsets, 3, 10),
            'age_max_offset': _offset_dist(age_max_offsets, 3, 10),
            'who_to_meet_size': _dist(Counter(who_to_meet_sizes or [1, 2, 3])),
            'gender_inclusion': _dist(gender_counts or Counter(GENDERS)),
            'relationship_structure': _dist(rel_struct_counts or Counter({'monogamous': 9, 'non_monogamous': 1})),
            'smoking': _dist(smoking_counts or Counter({'no': 75, 'occasionally': 20, 'yes': 5})),
            'partner_smoking': _dist(partner_smoking_counts or Counter({'no_smoking': 1, 'any': 1})),
            'has_children': round(sum(has_children_list) / max(1, len(has_children_list)), 4) if has_children_list else 0.15,
            'partner_children': _dist(partner_children_counts or Counter({'any': 1, 'no_children': 1})),
            'wants_children': _dist(wants_children_counts or Counter({'yes': 1, 'no': 1, 'unsure': 1})),
            'extra_zone': round(sum(extra_zone_list) / max(1, len(extra_zone_list)), 4) if extra_zone_list else 0.3,
            'extra_zone_choice': _dist(extra_zone_choice_counts or Counter(['zone_a', 'zone_b', 'zone_c', 'zone_d'])),
            'schedule_size': _dist(Counter(schedule_sizes or [1, 2, 3])),
        }
    }
    return emp_theta


def main():
    write_builtin()
    emp = fit_empirical_priors()
    path = HERE / "emp.json"
    path.write_text(json.dumps(emp, indent=2, sort_keys=True) + "\n")
    print(f"Wrote empirical priors to {path}")
    print(json.dumps({
        'accept': emp['accept'],
        'response': emp['response'],
        'date': emp['date'],
        'second': emp['second']
    }, indent=2))


if __name__ == '__main__':
    main()
