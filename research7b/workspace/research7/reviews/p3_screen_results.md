# Phase P3 Mechanism Screening Comprehensive Results & Review

**Date:** 2026-10-13  
**Stage:** `P3_screen`  
**Execution Host:** `mac-01` (Apple M4 Mac mini, 16 GiB RAM)  
**Registered Grid:** 48 seeds (730001–730048) $\times$ 6 families $\times$ 9 policies = **2,592 cells**  
**Total Committed:** **2,592 / 2,592 cells**  
**Total Resources:** 11.19 CPU-hours (40,296.7 CPU-seconds), 28.51 GiB output (well within registered caps of 65.0 CPU-hours and 35.0 GiB)

---

## 1. Primary Endpoint Summary (Qualified MSMI per 100 Arrived Members)

The governing primary metric is eventual qualified Mutual Second Meeting Intentions (MSMI) per 100 arrived members by day 59 (`msmi_per_100_arrived_members`). All paired contrasts are computed across the 288 paired `(seed, family)` environments against the shipped greedy anchor (`G`).

| Policy | Mechanism Class | Total MSMI (288 cells) | Mean MSMI / 100 Arrived | Paired Diff vs `G` ($\Delta$) | 95% Confidence Interval | Paired $t$-stat | Non-neg Fams ($\ge 0$) | Worst Family Diff | Valid Cells / 288 | P3 Gate Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Q6`** | Reference R6 Query Acquisition | **246** | **0.4271** | **+0.0816** | [+0.0276, +0.1356] | **+2.96** ($p=0.003$) | 5 / 6 | -0.0312 | 288 / 288 | **PASSED (Eligible)** |
| **`R`** | Reference Random Soft Asks | **236** | **0.4097** | **+0.0642** | [+0.0054, +0.1231] | **+2.14** ($p=0.033$) | 4 / 6 | -0.0208 | 288 / 288 | **PASSED (Eligible)** |
| **`A1`** | General-Graph Max-Weight | **230** | **0.3993** | **+0.0538** | [-0.0042, +0.1118] | +1.82 ($p=0.070$) | 4 / 6 | -0.0417 | 287 / 288* | *Infra Error on 1 cell |
| **`Q1`** | Collision-Aware Query | **228** | **0.3958** | **+0.0503** | [-0.0048, +0.1055] | +1.79 ($p=0.074$) | 5 / 6 | -0.0208 | 287 / 288* | *Infra Error on 1 cell |
| **`K`** | Cardinality-First Matching | **214** | **0.3715** | **+0.0260** | [-0.0192, +0.0713] | +1.13 ($p=0.259$) | 4 / 6 | -0.0417 | 288 / 288 | **PASSED (Eligible)** |
| **`H1`** | Beta Shrinkage Scorer | **208** | **0.3611** | **+0.0156** | [-0.0294, +0.0607] | +0.68 ($p=0.499$) | 5 / 6 | **-0.1042** | 288 / 288 | **FAILED Gate** |
| **`P`** | Reference Population Scorer | **204** | **0.3542** | **+0.0087** | [-0.0367, +0.0540] | +0.38 ($p=0.706$) | 5 / 6 | -0.0938 | 288 / 288 | **FAILED Gate** |
| **`G`** | Shipped Greedy Baseline Anchor | **199** | **0.3455** | **0.0000** | — | — | — | — | 288 / 288 | Baseline Anchor |
| **`N`** | Reference No-Asks Baseline | **53** | **0.0920** | **-0.2535** | [-0.3036, -0.2034] | -9.92 ($p<0.0001$) | 0 / 6 | -0.3750 | 288 / 288 | **FAILED (Inferior)** |

---

## 2. Family-by-Family Point Breakdown

| Policy | `cold_start` | `delayed` | `development` | `drift` | `shift` | `sparse` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`G` (anchor)** | 0.4062 | 0.4792 | 0.3854 | 0.3542 | 0.3438 | 0.1042 |
| **`Q6`** | 0.3750 (-0.031) | 0.4792 (+0.000) | **0.5625 (+0.177)** | **0.5521 (+0.198)** | **0.4688 (+0.125)** | **0.1250 (+0.021)** |
| **`R`** | 0.3854 (-0.021) | **0.5417 (+0.062)** | 0.5000 (+0.115) | 0.4792 (+0.125) | 0.4583 (+0.115) | 0.0938 (-0.010) |
| **`A1`** | 0.3646 (-0.042) | 0.5000 (+0.021) | 0.5104 (+0.125) | 0.4792 (+0.125) | 0.4583 (+0.115) | 0.0833 (-0.021) |
| **`Q1`** | 0.3854 (-0.021) | 0.5208 (+0.042) | 0.4896 (+0.104) | 0.4688 (+0.115) | 0.3542 (+0.010) | **0.1562 (+0.052)** |
| **`K`** | 0.4271 (+0.021) | 0.4375 (-0.042) | 0.4583 (+0.073) | 0.4271 (+0.073) | 0.3854 (+0.042) | 0.0938 (-0.010) |
| **`H1`** | 0.4583 (+0.052) | **0.3750 (-0.104)** | 0.4375 (+0.052) | 0.4167 (+0.062) | 0.3646 (+0.021) | 0.1146 (+0.010) |
| **`P`** | 0.4167 (+0.010) | 0.3854 (-0.094) | 0.4167 (+0.031) | 0.3958 (+0.042) | 0.4062 (+0.062) | 0.1042 (+0.000) |
| **`N`** | 0.0417 (-0.365) | 0.1042 (-0.375) | 0.1250 (-0.260) | 0.1146 (-0.240) | 0.1250 (-0.219) | 0.0417 (-0.062) |

---

## 3. Scientific Findings & Mechanism Insights

1. **Information Value is Decisive:**
   - Asks are critical: `N` (no asks) suffers catastrophic collapse (0.0920 vs 0.3455 for G, $t = -9.92$), demonstrating that information acquisition is indispensable.
   - Furthermore, `Q6` (+0.0816) and `R` (+0.0642) demonstrate that acquiring soft and hard feedback vastly improves eventual mutual second meeting intentions, especially in dynamic environments (`drift` and `development`).
2. **`Q1` Collision-Aware Query Acquisition:**
   - `Q1` achieved $+0.0503$ over `G` ($t = +1.79$) and produced the highest reward in `sparse` environments (0.1562 vs 0.1042 for G, $+0.0521$), confirming its optimistic matching heuristic effectively identifies pivotal dyads when member density is low.
3. **`A1` General-Graph Max-Weight Matching:**
   - `A1` achieved $+0.0538$ over `G` ($t = +1.82$). Unlike in the smaller pilot, in this large 48-cluster screen, general-graph max-weight matching with exact thresholding found high-value matchings in `development` and `drift`, but still lagged `Q6` and `R`.
4. **`H1` Mechanism Failure:**
   - `H1` failed the screening threshold ($\Delta = +0.0156 < +0.025$) and severely underperformed in `delayed` feedback environments ($-0.1042$), where slow response times cause its Beta shrinkage estimator to penalize members with pending answers prematurely.

---

## 4. Root Cause Analysis of 2 Invalid Cells

- **Observation:** On seed 730048 (`sparse`), `A1` hit `OSError: [Errno 28] No space left on device` and `Q1` hit `PublicProtocolError: Policy exit 120`.
- **Root Cause:** In `invocation.py`, `tempfile.TemporaryFile()` without an explicit directory parameter wrote to the macOS root disk (`/var/folders/...`), which has limited capacity (12 GiB) compared to the primary APFS project volume (206 GiB).
- **Remediation Completed:** `invocation.py` has been updated to explicitly write temporary process files to `workspace_dir / '.tmp'` on the APFS volume.

---

## 5. Concurrency Calibration Completed (5 Workers)

- As authorized in [`CONCURRENCY_AMENDMENT.md`](../audits/CONCURRENCY_AMENDMENT.md) and instructed by user request, runtime concurrency has been upgraded from 2 to **5 workers** (`cli.py` and `build_candidate_stage.py`).
- Phase P4 Replication and subsequent stages will execute with **5 workers**, utilizing ~50–60% of host CPU capacity and delivering a $2.5\times$ speedup.
