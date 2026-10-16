# Research 7 Execution Amendment: Worker Concurrency Calibration

**Date:** 2026-10-13  
**Authority:** Explicit user instruction under autonomous execution authorization.  
**Scope:** All future Research 7 empirical stages (including P4 Replication, P5 Selection, P6 Confirmation, and fitting/testing runs).

---

## 1. Rationale and Host Measurements

1. **Host Profile:** Apple M4 Mac mini with 10 CPU cores (4 Performance + 6 Efficiency cores) and 16 GiB unified RAM on APFS.
2. **Observed Resource Utilization during P3 Screen:**
   - 2 simulation workers yielded only ~27% aggregate CPU utilization, leaving ~72.5% CPU idle.
   - Peak worker RSS measured across thousands of cells is only ~75–100 MB per worker.
   - Zero memory leaks, zero zombie process group leaks (enforced by `killpg` in `invocation.py`).
   - Root disk `/tmp` usage has been permanently eliminated by redirecting subprocess execution pipes to `workspace_dir / '.tmp'` on the 206 GiB APFS volume, preventing swap amplification and disk pressure.
3. **Capacity Assessment:**
   - Operating at **6 concurrent workers** will consume ~450–500 MB combined RSS, remaining safely within physical memory (<3% of 16 GiB) without swap pressure on the host.
   - Running 6 concurrent single-threaded simulation workers (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`) consumes 6 physical cores (~60–70% CPU utilization), tripling execution throughput ($3.0\times$) while leaving 4 CPU cores free for the coordinator and macOS background services.
4. **Startup Latency Optimization:**
   - Caching `validate_executable_readiness` inside `RegisteredRunner` eliminates redundant $O(N^2)$ manifest serialization, enabling instantaneous startup for large grids (4,608+ cells).

---

## 2. Amended Concurrency Specification

1. **Default Worker Setting:** All future stage registrations and CLI executions will use **6 concurrent simulation workers** (`--workers 6`).
2. **CLI Guard:** `cli.py` guard permits `1 <= workers <= 8`.
3. **Stage Builders:** `build_candidate_stage.py` and future registration builders default to `"workers": 6` in `resource_forecast`.
4. **Execution Invariance:** Phase P3 completed under its registered 2-worker ledger. Code modifications take effect for Phase P4 and subsequent stages.
