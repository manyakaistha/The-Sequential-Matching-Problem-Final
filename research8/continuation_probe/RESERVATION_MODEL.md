# Reservation value and the bounded probe

Let B be the remainder of today's matching and e=(u,v) disjoint from B. All expectations condition on the public history H and a declared belief model, never a hidden simulator calendar. Write C_hold(H,B) for expected future qualified count after B, and C_match(H,B,e) for expected future qualified count after B+e. Immediate rewards of B cancel. Then matching e is better exactly when

    q_e(H) >= tau_e(H;B),
    tau_e(H;B) = C_hold(H,B) - C_match(H,B,e).

Ties may retain the parent. This is an exact comparison of these two actions when q and both continuation expectations are correct. q_e is eventual qualified reward, including the full follow-up window. Continuation covers busy occupancy, endpoint survival, pauses (including pauses without qualified reward), dyad exhaustion, query effects and future competing options. Holding is not justified merely by a positive future edge or a better ranking score.

An actor threshold tau_t(u) is exact only in a reduced single-resource model. If u has one immediate opportunity worth q, matching leads to expected future value C_after(t,u), and holding leads to C_ready(t,u), then tau_t(u)=C_ready-C_after. In the special two-day case, a current match blocks all remaining reuse, an independent future compatible arrival occurs with probability p, u survives with probability s, and the future match yields r, tau_t(u)=s*p*r. Thus waiting is optimal iff q<s*p*r. Without blocking, the current reward and later opportunity may both be collected, so this threshold does not apply.

For two interacting actors the joint threshold generally cannot be replaced by tau_t(u)+tau_t(v): they may compete for the same future actor, share pause outcomes, or displace other matches. A rollout action should compare whole legal matchings under shared future randomness and observation-consistent continuation decisions. At day59 both future continuation terms are zero; tau_e=0 for a pure edge deletion, and positive eventual q must not be penalized by a shortened observation window.

The current return-hold policy does not estimate calibrated q or solve this Bellman comparison. It is a deliberately narrow ordinal-score hypothesis about a publicly evidenced potential return tomorrow. Its one-day/once-per-endpoint cap limits damage; it does not establish positive expected value. The registered development probe asks whether the mechanism is present before any broader continuation model is fitted or evaluated.

Useful falsifiers: holding when the better actor cannot actually return; future survival/availability lower than assumed; high score unrelated to qualified reward; held endpoints depart; another actor captures the future opportunity; current match can finish and reuse before the future opportunity; or holding only shifts dyad/day randomness. A negative probe does not refute all reservation models.
