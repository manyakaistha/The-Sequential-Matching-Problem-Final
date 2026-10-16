# Phase 5: Research 5 (Replication, World Audit, and Provenance Verification)

**Document Reference**: `study_notes/phases/05_research5_replication_and_world_audit.md`  
**Base Repository Artifacts**: [`research5/FINAL_REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/FINAL_REPORT.md), [`research5/REPRODUCTION.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/REPRODUCTION.md), [`research5/RESULT_REPLICATION.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/RESULT_REPLICATION.md), [`research5/ARCHIVE_AUDIT_REVIEW.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/ARCHIVE_AUDIT_REVIEW.md), [`research5/WORLD_REVIEW.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/WORLD_REVIEW.md)  
**Verification Engines & Replicators**: [`research5/benchmark.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/benchmark.py), [`research5/verify_logs.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/verify_logs.py), [`research5/verify_statistics.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/verify_statistics.py), [`research5/verify_worlds.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/verify_worlds.py), [`research5/restore_artifacts.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/restore_artifacts.py)

---

## 1. Context and Problem Formulation

In Round 4, `population_control` scored a nominal paired difference of $+0.0565$ MSMI/100 ($p = 0.0683$), which was statistically inconclusive under the 3-test Bonferroni program gate. However, the magnitude of the point estimate raised the question of whether `population_control` possessed a genuine practical advantage over greedy baseline (such as $+0.05$ MSMI/100) that lacked sufficient power to be detected at $n=56$ seed clusters.

Research 5 was designed not as an exploratory search for new heuristics, but as a **massive, pre-registered confirmatory replication and world audit**. To conclusively resolve the performance of `population_control` against shipped greedy, the evaluation scale was expanded by nearly an order of magnitude to **430 independent seed clusters (5,160 total episodes)**.

Simultaneously, Research 5 served as a comprehensive forensic provenance audit to eliminate doubts regarding:
1. Whether both competing policies started from identical initial simulator worlds,
2. Whether interrupted executions introduced survival or selection bias,
3. Whether unhandled exceptions or hidden fallback invocations occurred in the evaluation logs.

---

## 2. Hypotheses Tested

1. **The Replicated Superiority Hypothesis**: `population_control` will establish a statistically significant improvement of at least $+0.05$ MSMI/100 over shipped greedy at the registered multi-round significance level $\alpha = 0.0125$ ($98.75\%$ confidence interval).
2. **Initial World Provenance Invariance**: Both competing policies (`population_control` and `greedy`) are initialized with mathematically identical member arrival queues, latent attributes, and random stream seeds across all 2,580 evaluated world instances.
3. **Execution Robustness & Zero Fallback**: Across 5,160 production episodes (619,200 individual daily decision invocations), the frozen policy executes with zero unhandled exceptions, zero container resource violations, and zero fallback activations.

---

## 3. Status and Historical Timeline

- **11 October 2026**: Pre-registered protocol locked; evaluation initiated across seeds 90001–90430 (430 clusters $\times$ 6 scenario families $\times$ 2 policies = 5,160 episodes).
- **11 October 2026**: Operational interruptions encountered during execution (Attempt 1 committed 108 rows; Attempt 2 committed 10 rows; Attempt 3 completed the remaining 5,042 rows).
- **11 October 2026**: Independent completed-test statistics reconstructed and verified via `research5/verify_statistics.py`.
- **11 October 2026**: World provenance audit completed via `research5/verify_worlds.py`.
- **11 October 2026**: Final scientific report authored in [`research5/FINAL_REPORT.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/FINAL_REPORT.md).
- **Outcome Status**: **Definitive Confirmatory Failure**. The paired effect shrank to **$+0.000775$ MSMI/100** ($p = 0.9447$). Superiority was completely refuted; the target $+0.05$ effect was ruled out.

---

## 4. Algorithmic Architecture and Evaluated Policies

The evaluated policy remained strictly frozen as `population_control` (from Round 4), evaluated directly against shipped greedy baseline (`policy_greedy.py`).

### `population_control` Mechanism
- **Clarification**: Pure FIFO list-order hard constraint bundle queries (`"constraints"`, cost 3). Permanent declines cached and skipped.
- **Scoring Model**: Closed-form population log-odds:
  $$\text{Score}(u, v) = \sum_{k \in \mathcal{S}} \beta_k \cdot \mathbb{P}_{\text{pop}}(u_k = v_k \mid \text{disclosed fields})$$
  Missing soft attributes integrated over known population base rates. Zero within-episode online learning.
- **Allocation**: Descending score order greedy first-fit matching on verified reciprocally feasible edges.

---

## 5. Code Map and Concrete Execution Trace

### Repository Code Structure
- [`research5/benchmark.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/benchmark.py): High-throughput evaluation runner supporting incremental state checkpointing and recovery.
- [`research5/verify_statistics.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/verify_statistics.py): Standalone statistical verifier computing paired t-tests, bootstrap intervals, and per-family metrics directly from raw JSONL rows.
- [`research5/verify_worlds.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/verify_worlds.py): Validates initial world generation by regenerating worlds directly from `kit.generate()` and checking cryptographic digests against recorded episodes.
- [`research5/verify_logs.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/verify_logs.py): Audits 619,200 invocations for action legality, schema compliance, and memory limits.
- [`research5/restore_artifacts.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/restore_artifacts.py): Hardened archive extraction utility utilizing `O_NOFOLLOW` and `O_EXCL` flags to prevent directory traversal and symlink poisoning.

---

## 6. Experimental Design

### Evaluation Scale and Partitioning
- **Seed Range**: Seeds 90001–90430 ($n = 430$ independent seed clusters).
- **Scenario Families**: Evaluated across all 6 standard simulator families (`development`, `sparse`, `cold_start`, `delayed`, `shift`, `drift`) with equal weighting within each seed cluster.
- **Total Invocations**:
  $$430 \text{ seeds} \times 6 \text{ families} \times 2 \text{ policies} = 5,160 \text{ episodes} \times 120 \text{ calls/episode} = 619,200 \text{ calls}.$$
- **Total Arrived Members Evaluated**: $5,160 \times 200 = 1,032,000$ synthetic members ($516,000$ per policy).

---

## 7. Pre-Outcome Rules and Decision Gates

1. **Four-Round Multiplicity Gate**:
   Accounting for the four cumulative confirmatory tests (Round 1, Round 3, Round 4, Round 5), the family-wise error rate was bounded via Bonferroni:
   $$\alpha_{\text{program}} = \frac{0.05}{4} = 0.0125 \implies \text{Two-sided } 98.75\% \text{ confidence interval}.$$
2. **Superiority Criterion**:
   The lower bound of the registered $98.75\%$ paired confidence interval must strictly exceed zero ($CI_{98.75\%} \text{ lower} > 0$).
3. **Practical Effect Threshold**:
   Target effect size was $\delta = +0.05$ MSMI/100. Lower bound must exceed $+0.05$ to claim practical superiority.

---

## 8. Actual Execution, Operational Interruptions, and Audit Recovery

The large-scale confirmation experienced two operational halts during batch execution:
- **First Attempt**: Process terminated after committing 108 valid rows.
- **Second Attempt**: Process restarted and committed 10 additional rows before halting due to host node preemption.
- **Third Attempt**: Completed the remaining 5,042 rows to reach the exact pre-registered grid of 5,160 episodes.

### Forensic Recovery Audit
The Critic and Replicator audited the fragmented execution ([`research5/ARCHIVE_AUDIT_REVIEW.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/ARCHIVE_AUDIT_REVIEW.md)):
- All 108 first-attempt rows and 10 second-attempt rows were retained with full recorder attribution.
- Zero failed or corrupted episodes were dropped or silently replaced.
- Uncommitted orphan records (including one `KeyboardInterrupt` and 3 damaged gzip segments) were preserved in raw quarantine archives. All 488 readable orphan responses matched the committed replay actions byte-for-byte.
- **Exhaustive Log Audit**: Every one of the 5,160 committed episodes was audited by `verify_logs.py`—100% legal actions, zero fallbacks, zero constraint violations.

---

## 9. Results with Uncertainty: The Total Collapse of the Point Gain

### Replicated Confirmatory Statistics (430 Seed Clusters, 5,160 Episodes)

| Metric | Shipped Greedy Baseline | Frozen `population_control` | Paired Difference | Confidence Intervals & Tests |
|---|---:|---:|---:|---:|
| **Qualified MSMI Dyads** | **1,968** | **1,972** | **+4 dyads** | — |
| **MSMI per 100 arrived** | **0.381395** | **0.382171** | **+0.000775** | **Registered 98.75% CI: [-0.027215, +0.028766]** |
| | | | | **Nominal 95% CI: [-0.021158, +0.022709]** |
| | | | | **Bootstrap 98.75% CI: [-0.025775, +0.029070]** |
| | | | | **Bootstrap 95% CI: [-0.021124, +0.022674]** |

- **Two-sided paired t-test**: $t(429) = 0.0695$, $p = 0.94465$.
- **Paired Seed Standard Deviation**: $\sigma_d = 0.2314$.
- **Standard Error**: $SE = 0.01116$.
- **Leave-One-Seed-Out Range**: `[-0.001360, +0.002331]`.
- **Verdict**: The paired difference is $+0.000775$ MSMI/100 (a difference of only 4 qualified couples across 1,032,000 arrived members). The confidence interval crosses zero symmetrically and decisively excludes both the planned $+0.05$ and $+0.10$ thresholds.

### Detailed Conversion Funnel Decomposition

Across all 5,160 episodes, the funnel metrics were virtually indistinguishable between policies:

| Funnel Transition | Shipped Greedy Baseline | `population_control` | Conversion Rate |
|---|---:|---:|---:|
| Total Introductions Made | 193,225 | 192,455 | — |
| Both First Responded | 112,549 | 112,139 | 58.25% vs 58.27% |
| Mutual Acceptance (Stage 1 Yes) | 27,919 | 28,202 | 24.81% vs 25.15% |
| Dates Actually Occurred | 22,038 | 22,124 | 78.94% vs 78.45% |
| Both Responded Second Meeting | 13,506 | 13,510 | 61.29% vs 61.06% |
| Both Positive Second Meeting | 5,444 | 5,460 | 40.31% vs 40.41% |
| **Qualified Terminal MSMI** | **1,968** | **1,972** | **36.15% vs 36.12%** |
| Total Inquiry Cost Expended | 512,073 units | 512,073 units | 100.0% identical |

---

## 10. Mechanistic Analysis and World Provenance Audit

### Initial World Cryptographic Audit (`verify_worlds.py`)
To disprove any suspicion of biased simulator initial conditions, the provenance audit regenerated initial worlds across all 2,580 seed-family cells:
- Master generator hash: `kit.generate()` verified (`0d2cb3d3b46ca2a6...`).
- Cryptographic SHA256 hashes of generated initial member queues matched stored episode observations in **2,580 out of 2,580 cells (100.0%)**.
- Both `greedy` and `population_control` faced mathematically identical agent arrival orders and latent parameters in every single episode.

### The Elimination of Round 4's $+0.0565$ Illusion
In Round 4 ($n=56$), `population_control` appeared to lead by $+0.0565$. Why did it drop to $+0.000775$ across $n=430$?
1. **Sampling Variance on Rare Discrete Outcomes**: With MSMI occurring at an absolute base rate of $\approx 0.38$ per 100 arrivals, an episode typically observes only 0, 1, or 2 qualified pairs. At $n=56$, a net swing of just 19 pairs across 672 episodes produces a $+0.0565$ point shift.
2. **Uniform Information Bounds**: Both policies expended the exact same inquiry budget (512,073 units) in pure FIFO hard bundles, discovering identical feasible graphs.
3. **The Flat Scoring Surface**: Population soft-feature log-odds vary across a narrow range ($[-0.5, +0.7]$). On sparse feasible graphs where most nodes have degree 0 or 1, sorting edges by population score yields matchings that overlap $> 95\%$ with greedy list-order matching.

---

## 11. Review and Critic Objections

1. **The Fallacy of Post-Hoc Significance Chasing**: The critic pointed out that Round 5 was initiated because Round 4 yielded $p = 0.0683$. Round 5 definitively proved that chasing marginal $p$-values in small samples is an exercise in chasing noise: when properly powered ($n=430$), the effect vanished entirely ($p = 0.945$).
2. **The Symlink Vulnerability in Artifact Restoration**: During the archive review ([`research5/ARCHIVE_AUDIT_REVIEW.md`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/ARCHIVE_AUDIT_REVIEW.md)), the critic discovered that standard `tarfile` and `zipfile` extraction routines could follow malicious symlinks. The team authored [`research5/restore_artifacts.py`](file:///Volumes/1700%20APFS/PERSONAL_PROGRAMMING_PROJECTS/Notes/The%20Sequential%20Matching%20Problem/research5/restore_artifacts.py), enforcing strict POSIX directory-descriptor traversal (`O_NOFOLLOW | O_EXCL`) and symlink refusal.

---

## 12. Final Decision and Action Taken

- **Confirmatory Verdict**: Complete and definitive rejection of superiority for `population_control`.
- **Baseline Retention**: Shipped greedy (`policy_greedy.py`) is retained as the authoritative, unbreakable benchmark.
- **Architectural Pruning**: Permanently cease research into static soft-attribute scoring functions. Prohibit further attempts to beat greedy through soft-feature weighting without fundamentally altering hard feasibility acquisition.

---

## 13. Learnings and Anti-Learnings

### Validated Scientific Learnings
- **Large-Sample Power Crushes Marginally Significant Illusions**: Expanding sample size from $n=56$ to $n=430$ proved that the $+0.0565$ effect was purely sampling noise.
- **Identical Inquiry Yields Identical Matching**: When policies use identical FIFO hard-constraint querying, the resulting feasible subgraphs are so sparse that allocation policy variations have almost zero causal leverage.

### Anti-Learnings
- **Do Not Interpret $p \approx 0.06$ as "Almost Significant"**: In high-variance discrete stochastic processes, marginal $p$-values frequently regress directly to $p \approx 1.0$ upon replication.
- **Do Not Pool Prior Failed Rounds**: Combining data from Round 4 ($n=56$) with Round 5 ($n=430$) to preserve a positive point estimate is scientifically invalid; the confirmatory replication must stand independently.

---

## 14. Defense Practice and Exam Exercises

### Question 1: Provenance and Replay Verification
*Describe the technical protocol required to verify that two competing policies were evaluated under identical conditions in a stochastic sequential simulator.*  
**Model Defense Answer**: Complete provenance verification requires three independent checks: (1) **World Generation Identity**: Regenerate initial world states using the fixed random seed and generator version, verifying cryptographic SHA256 hashes against initial state logs for both policies. (2) **Execution Isolation**: Replay identical action sequences in fresh isolated subprocesses and restricted containers, verifying that memory usage, response structures, and step latencies match. (3) **Independent Metric Reconstruction**: Reconstruct all primary and funnel metrics directly from logged primitive events using an independent parser, ensuring no dependence on the evaluator's internal state.

### Question 2: Power and Precision in Rare-Event Matching
*Suppose an evaluation observes an effect of $+0.000775$ MSMI/100 with paired standard deviation $\sigma_d = 0.2314$ across $n=430$ clusters. Calculate the two-sided $p$-value and interpret whether this establishes equivalence to zero.*  
**Model Defense Answer**: The standard error is $\text{SE} = 0.2314 / \sqrt{430} \approx 0.01116$. The test statistic is $t = 0.000775 / 0.01116 \approx 0.0694$. With 429 degrees of freedom, the two-sided $p$-value is $2 \times (1 - \Phi(0.0694)) \approx 0.9447$. In frequentist hypothesis testing, failing to reject $H_0: \delta = 0$ ($p > 0.05$) does *not* prove that $\delta = 0$ (equivalence). It proves only that the data are consistent with zero effect and that the target effect $\delta = +0.05$ is rejected with $98.75\%$ confidence.
