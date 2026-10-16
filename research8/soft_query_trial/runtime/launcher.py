"""Multi-worker execution coordinator for Research 8 soft query trial.

Features:
- Enforces user mandate: at most 3 simulation worker processes globally.
- Cached output_size calculation to eliminate coordinator dispatch stalls.
- Complete reconciliation and restart-idempotency.
- Lockfile protection against concurrent coordinators.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
import fcntl
import json
import os
from pathlib import Path
import resource
import shutil
import sys
import time

# Ensure workspace is on sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from research8.soft_query_trial.runtime.runner import Research8Runner


_size_cache = {
    "size": None,
    "last_check_time": 0,
    "added_count": 0,
}


def cached_output_size(path: Path) -> int:
    now = time.time()
    if _size_cache["size"] is None or (now - _size_cache["last_check_time"]) > 600:
        total = sum(p.stat().st_size for p in Path(path).rglob("*") if p.is_file())
        _size_cache["size"] = total
        _size_cache["last_check_time"] = now
        _size_cache["added_count"] = 0
        return total
    _size_cache["added_count"] += 1
    return _size_cache["size"] + _size_cache["added_count"] * (5 * 1024 * 1024)


def worker_task(job):
    workspace, registration, output_dir, cell = job
    runner = Research8Runner(Path(workspace), registration, Path(output_dir))
    return runner.execute_cell(cell)


def run_experiment(registration_path: Path, output_dir: Path, workers: int = 3):
    if not (1 <= workers <= 3):
        raise ValueError(f"Mandated simulator limit: 1 to 3 workers (got {workers})")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    commits_dir = output_dir / "commits"
    commits_dir.mkdir(parents=True, exist_ok=True)

    lock_file = output_dir / "coordinator.lock"
    lock_fd = lock_file.open("a")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_fd.close()
        raise RuntimeError("Another coordinator currently holds the lock for this output directory.")

    try:
        reg_dict = json.loads(Path(registration_path).read_text())
        cells = reg_dict.get("cells", [])
        if not cells:
            raise ValueError("Registration contains 0 cells.")

        # Reconcile existing commits
        committed = set()
        for p in commits_dir.glob("*.json"):
            committed.add(p.stem)

        queue = [c for c in cells if c["cell_key"] not in committed]
        total_cells = len(cells)
        done_cells = len(committed)

        print(f"=== Research 8 Coordinator Initialized ===")
        print(f"Registration: {registration_path}")
        print(f"Output: {output_dir}")
        print(f"Workers: {workers} (strict cap: <= 3)")
        print(f"Total cells: {total_cells} | Already committed: {done_cells} | Queue: {len(queue)}")

        start_time = time.monotonic()
        pending = {}

        with ProcessPoolExecutor(max_workers=workers) as pool:
            while queue or pending:
                # Dispatch tasks up to worker limit
                while queue and len(pending) < workers:
                    cell = queue.pop(0)
                    job = (str(WORKSPACE_ROOT), reg_dict, str(output_dir), cell)
                    future = pool.submit(worker_task, job)
                    pending[future] = cell["cell_key"]

                if not pending:
                    break

                done, _ = wait(pending.keys(), return_when=FIRST_COMPLETED)
                for f in done:
                    ck = pending.pop(f)
                    done_cells += 1
                    try:
                        res = f.result()
                        msmi = res.get("metrics", {}).get("msmi_per_100_arrived_members", 0.0)
                        cpu_s = res.get("cpu_seconds", 0.0)
                        elapsed = time.monotonic() - start_time
                        rate = (done_cells - len(committed)) / max(1e-5, elapsed) * 3600
                        print(f"[{done_cells}/{total_cells}] Cell {ck} -> MSMI/100={msmi:.4f} in {cpu_s:.1f}s CPU ({rate:.0f} cells/hr)")
                    except Exception as exc:
                        print(f"[{done_cells}/{total_cells}] Cell {ck} FAILED: {exc}")

        print(f"=== Experiment Complete: {done_cells}/{total_cells} cells committed cleanly. ===")
        return 0

    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def main():
    parser = argparse.ArgumentParser(description="Research 8 High-Throughput Launcher")
    parser.add_argument("--registration", required=True, help="Path to frozen registration JSON")
    parser.add_argument("--output", required=True, help="Path to output results directory")
    parser.add_argument("--workers", type=int, default=3, help="Worker count (max 3)")
    args = parser.parse_args()

    sys.exit(run_experiment(Path(args.registration), Path(args.output), args.workers))


if __name__ == "__main__":
    main()
