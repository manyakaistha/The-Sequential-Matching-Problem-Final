# Research 8 Soft Query Trial: Phase R8_smoke Audit & Resource Gate Review

**Date:** 2026-10-14  
**Stage:** `R8_smoke` (72 cells: 4 fresh seeds $\times$ 6 scenario families $\times$ 3 policy arms)  
**Output Directory:** `results/research8/soft_query_trial/smoke`  
**Reviewer:** Research 8 Autonomous Coordinator & Independent Reviewer  
**Disposition:** **PASSED ALL GATES — CLEARED FOR 432-CELL PRIMARY RUN (`R8_primary`)**

---

## 1. Grid Integrity & Reconciled Audit
- **Expected Cells:** 72
- **Verified Committed Cells:** 72 (100.0%)
- **Invalid Cells / Fallbacks:** 0 (100.0% valid)
- **World Parity:** 100% verified (exact identical world SHA256 across all 3 arms for each seed-family)
- **Denominator Parity:** 100% verified (exact identical arrived-by-day-59 count across all 3 arms for each seed-family)

---

## 2. Mechanism Funnel Verification

| Metric | Arm G | Arm G_random_soft | Arm G_targeted_soft | Target Verification |
| :--- | :---: | :---: | :---: | :--- |
| **Mean Hard Asks** | 63.4 | 63.4 | 63.4 | **Exact parity** across all 3 arms (0 displacement) |
| **Mean Soft Asks** | 0.0 | 93.8 | 91.9 | Unused budget actively filled with soft queries |
| **Mean Total Asks** | 63.4 | 157.2 | 155.3 | Confirms soft queries spend slack budget |
| **Mean Ask Cost** | 190.1 | 284.0 | 282.0 | Well within daily budget 12 ($60 \times 12 = 720$) |
| **Mean Assignments** | 68.5 | 68.9 | 69.5 | Stable allocation volume |
| **Mean Happened Dates** | 7.8 | 7.3 | 6.9 | Descriptively tracked |
| **Mean Qualified MSMI** | 0.42 | 0.58 | 0.50 | Raw dyad count |
| **Mean MSMI / 100** | 0.2083 | 0.2917 | 0.2500 | Normalized endpoint ($Y = 100 \times Q / A$) |

---

## 3. Predeclared Contrasts (4 Seed Clusters Diagnostic)
1. **$G_{\text{random\_soft}} - G$:** $\Delta = +0.0833 \pm 0.0589$ ($t = +1.41, p_{\text{unadj}} = 0.2522, p_{\text{holm}} = 0.5451$).
2. **$G_{\text{targeted\_soft}} - G$:** $\Delta = +0.0417 \pm 0.0241$ ($t = +1.73, p_{\text{unadj}} = 0.1817, p_{\text{holm}} = 0.5451$).
3. **$G_{\text{targeted\_soft}} - G_{\text{random\_soft}}:$** $\Delta = -0.0417 \pm 0.0417$ ($t = -1.00, p_{\text{unadj}} = 0.3910, p_{\text{holm}} = 0.5451$).

*(Note: Diagnostic development smoke on 4 seed clusters is not powered for statistical significance; its role is verifying mechanism activation, zero hard displacement, and observation isolation).*

---

## 4. Resource & Runtime Gate Certification
- **Observed Throughput:** 2,500 cells / hour on 3 simulation processes.
- **Observed Attempt CPU Time:** Mean ~3.1s CPU for G, ~4.7s CPU for soft-query arms.
- **Observed Disk Usage:** ~30 MB total for 72 cells.
- **Forecast for Primary Execution (432 cells):**
  - Estimated CPU time: ~1,800 CPU seconds (~30 CPU minutes).
  - Estimated wall-clock time: ~10 – 12 minutes on 3 workers.
  - Estimated output storage: ~180 MB (well below the 141 GiB available on `/Volumes/1700 APFS/`).
  - Memory: Max RSS per process <150 MB (rock-stable, 0 swap).

**Gate Verdict:** ALL PREREQUISITES CLOSED. Execution of `R8_primary` is fully cleared.
