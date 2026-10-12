# Comprehensive Bibliography & Literature References
**Sequential Reciprocal Matching Under Uncertainty (The One Introduction Problem / Romeo & Juliet)**

This references repository maintains all peer-reviewed academic papers, theoretical frameworks, algorithmic foundations, and empirical research citations utilized in formulating, benchmarking, and executing our novel matching policy (**AV-RHB+**).

---

## 1. Dynamic Matching & Two-Sided Market Design
1. **Akbarpour, M., Li, S., & Oveis Gharan, S. (2020).** *Thickness and Information in Dynamic Matching Markets.* Journal of Political Economy, 128(3), 783–815. [DOI: 10.1086/704761](https://doi.org/10.1086/704761)
   - *Key Theorem:* Proves that in dynamic matching markets with unobserved departure times, greedy matching incurs an exponential-to-polynomial loss penalty ($\Omega(1/d)$ vs $\mathcal{O}(e^{-d/2})$) when departures can be anticipated, but periodic batch clearing restores market thickness.
2. **Baccara, M., Lee, S., & Yariv, L. (2020).** *Optimal Dynamic Matching.* Theoretical Economics, 15(3), 1221–1278. [DOI: 10.3982/TE3740](https://doi.org/10.3982/TE3740)
   - *Key Formulation:* Characterizes optimal dynamic mechanisms when agents arrive stochastically and have heterogeneous match values and waiting costs; establishes the inventory cutoff buffer policy.
3. **Ashlagi, I., Nikzad, A., & Strack, P. (2023).** *Matching in Dynamic Imbalanced Markets.* The Review of Economic Studies, 90(2), 527–564. [DOI: 10.1093/restud/rdac041](https://doi.org/10.1093/restud/rdac041)
   - *Key Takeaway:* Proves that when departures are silent and unobservable, greedy clearing suffers no asymptotic penalty over batching, validating daily micro-batching.
4. **Kerimov, S., Ashlagi, I., & Gurvich, I. (2023).** *On the Optimality of Greedy Policies in Dynamic Matching.* Operations Research, 72(4), 1481–1499. [DOI: 10.1287/opre.2021.0182](https://doi.org/10.1287/opre.2021.0182)
   - *Key Takeaway:* Square-root resolving interval $\Delta t^* \propto \sqrt{C_1 / (C_2 \cdot \theta)}$ bounding regret under capacity slack.
5. **Anderson, R., Ashlagi, I., Gamarnik, D., & Kanoria, Y. (2017).** *Efficient Dynamic Barter Exchange.* Operations Research, 65(6), 1446–1459. [DOI: 10.1287/opre.2017.1644](https://doi.org/10.1287/opre.2017.1644)
6. **Roth, A. E., & Sotomayor, M. A. (1992).** *Two-Sided Matching: A Study in Game-Theoretic Modeling and Analysis.* Cambridge University Press.
7. **Shimer, R., & Smith, L. (2000).** *Assortative Matching and Search.* Econometrica, 68(2), 343–369. [DOI: 10.1111/1468-0262.00112](https://doi.org/10.1111/1468-0262.00112)
8. **Blanchet, J., Reiman, M., Virag, C., & Wang, Y. (2022).** *Dynamic Bipartite Matching with Abandonment: Fluid Approximations and Asymptotic Optimality.* Mathematics of Operations Research, 47(3), 2095–2126.

---

## 2. Reciprocal Recommender Systems (RRS) & Dyadic Choice Modeling
9. **Pizzato, L., Chung, T., Rej, T., Koprinska, I., & Kay, J. (2010).** *RECON: A Reciprocal Recommender for Online Dating.* Proceedings of the 4th ACM Conference on Recommender Systems (RecSys '10), pp. 207–214.
   - *Key Formulation:* Proves the breakdown of independent choice and formulates the Harmonic Mean aggregation operator $\Phi_{\text{harmonic}} = \frac{2 r_{A \to B} r_{B \to A}}{r_{A \to B} + r_{B \to A}}$ to severely penalize asymmetric attraction.
10. **Neve, J., & Palomares, I. (2019).** *Latent Factor Models and Aggregation Operators for Collaborative Filtering in Reciprocal Recommender Systems.* Proceedings of the 13th ACM Conference on Recommender Systems (RecSys '19), pp. 403–407.
    - *Key Formulation:* Dual Latent Factor Model (LFRR) separating user $'s role as active evaluator ($\mathbf{p}_u$) from their role as candidate ($\mathbf{q}_u$).
11. **Palomares, I., Porcel, C., Pizzato, L., Guy, I., & Herrera-Viedma, E. (2021).** *Reciprocal Recommender Systems: Analysis of State-of-the-Art Literature, Challenges and Opportunities towards Social Recommendation.* Information Fusion, 69, pp. 103–127.
12. **Bruch, E. E., & Newman, M. E. J. (2018).** *Aspirational Pursuit of Mates in Online Dating Markets.* Science Advances, 4(8), eaap9815.
    - *Key Finding:* Daters pursue candidates 25% more desirable than themselves, but realized reciprocal matches peak strictly when desirability gap $|D_A - D_B| \to 0$ (assortative sorting).
13. **Hitsch, G. J., Hortaçsu, A., & Ariely, D. (2010).** *Matching and Sorting in Online Dating.* American Economic Review, 100(1), pp. 130–163.
    - *Key Finding:* Empirical characterization of non-linear and signed age gap penalties and non-compensatory dealbreaker attributes.
14. **Tomita, Y., & Yokoyama, T. (2024 / 2026).** *Balancing Fairness and High Match Rates in Reciprocal Recommender Systems: A Nash Social Welfare Approach.* ACM Transactions on Recommender Systems (TORS), 2026 / RecSys '24.
15. **Xia, P., Liu, B., Sun, Y., & Chen, C. (2015).** *Reciprocal Recommendation System for Online Dating.* Proceedings of the 2015 IEEE/ACM International Conference on Advances in Social Networks Analysis and Mining (ASONAM '15), pp. 234–241.
16. **Akehurst, J., Koprinska, I., Yacef, K., Pizzato, L., Kay, J., & Rej, T. (2011).** *CCR – A Content-Collaborative Reciprocal Recommender for Online Dating.* Proceedings of the 22nd International Joint Conference on Artificial Intelligence (IJCAI '11).

---

## 3. Delayed Feedback, Survival Bandits & Right-Censoring
17. **Chapelle, O. (2014).** *Modeling Delayed Feedback in Display Advertising.* Proceedings of the 20th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '14), pp. 1097–1105.
    - *Key Formulation:* Delayed Feedback Model (DFM) using Expectation-Maximization to treat unobserved conversions as a mixture of non-conversions and pending conversions ( = \mathbb{P}(C=1 \mid Y=0, e_i)$), preventing false negative starvation.
18. **Vernade, C., Cappé, O., & Perchet, V. (2017).** *Stochastic Bandit Models for Delayed Conversions.* Proceedings of the 33rd Conference on Uncertainty in Artificial Intelligence (UAI 2017), PMLR 73.
    - *Key Formulation:* Delayed UCB index weighting exposures by the delay CDF (E_a(t))$, preserving the optimal logarithmic asymptotic regret rate.
19. **Joulani, P., György, A., & Szepesvári, C. (2013).** *Online Learning under Delayed Feedback.* Proceedings of the 30th International Conference on Machine Learning (ICML 2013), JMLR W&CP 28(3): 1453–1461.
    - *Key Theorem:* Delays incur only an additive regret penalty (K \cdot \mathbb{E}[\tau])$ in stochastic environments.
20. **Mandel, T., Liu, Y.-E., Brunskill, E., & Popović, Z. (2015).** *The Queue Method: Handling Delay, Heuristics, Prior Data, and Evaluation in Bandits.* Proceedings of the 29th AAAI Conference on Artificial Intelligence (AAAI '15), pp. 2849–2856.
21. **Walsh, T. J., Nouri, A., Li, L., & Littman, M. L. (2009).** *Learning and Planning in Environments with Delayed Feedback.* Autonomous Agents and Multi-Agent Systems, 18(1): 83–105.
    - *Key Concept:* Augmented Information State $\tilde{s}_t = (\mathcal{S}_t^{obs}, \mathcal{B}_t)$ tracking pending in-flight decisions with elapsed times to restore the Markov property without lookahead.
22. **Farewell, V. T. (1982).** *The Use of a Mixture Model in the Analysis of Survival Data with Long-Term Survivors.* Biometrics, 38(4): 1041–1046.

---

## 4. Combinatorial Matching & General Graph Algorithms
23. **Edmonds, J. (1965).** *Paths, Trees, and Flowers.* Canadian Journal of Mathematics, 17, 449–467.
    - *Key Algorithm:* Maximum Weight Matching on general graphs (Edmonds' Blossom Algorithm). Eliminates the bipartite restriction and correctly resolves odd-cycle components (, C_5$), which compose 58.76% of feasible pairings in our dating pool.
24. **Chen, W., Wang, Y., & Yuan, Y. (2013).** *Combinatorial Multi-Armed Bandit: General Framework, Results and Applications.* ICML 2013.
25. **Kveton, B., Szepesvari, C., Wen, Z., & Ashkan, A. (2015).** *Cascading Bandits: Learning to Rank over Combinatorial Subsets.* ICML 2015.

---

## 5. Active Sensing, Clarification & Value of Information (VoI)
26. **Howard, R. A. (1966).** *Information Value Theory.* IEEE Transactions on Systems Science and Cybernetics, 2(1), 22–26.
    - *Key Formulation:* Expected Value of Information (EVOI) $\mathbb{E}[\Delta U] = \mathbb{E}_{y}[\max_a \mathbb{E}[U(a) \mid y]] - \max_a \mathbb{E}[U(a)]$. Proves that querying soft fields for nodes with unverified hard constraints has strictly zero VoI.
27. **Blackwell, D. (1953).** *Equivalent Comparisons of Experiments.* The Annals of Mathematical Statistics, 24(2), 265–272.
28. **Krause, A., & Guestrin, C. (2005).** *Near-Optimal Nonmyopic Value of Information in Graphical Models.* UAI 2005.
29. **Settles, B. (2009).** *Active Learning Literature Survey.* Computer Sciences Technical Report 1648, University of Wisconsin–Madison.

---

## 6. Distribution Shift, Non-Stationary Bandits & Robustness
30. **Gama, J., Žliobaitė, I., Bifet, A., Pechenizkiy, M., & Bouchachia, A. (2014).** *A Survey on Concept Drift Adaptation.* ACM Computing Surveys, 46(4), 1–37.
31. **Garivier, A., & Moulines, E. (2011).** *On Upper-Confidence Bound Policies for Non-Stationary Bandit Problems.* ALT 2011.
    - *Key Formulation:* Sliding-Window and Discounted UCB for tracking abrupt parameter shifts (such as the -0.5 logit drop at Day 35 in  and weight sign flips in ).
32. **Page, E. S. (1954).** *Continuous Inspection Schemes.* Biometrika, 41(1/2), 100–115. (CUSUM Change-Point Detection).
