"""Research 7 Runtime Engine and Durable Logging Scaffolding.

Provides strict public isolation, protocol validation, cell lease tracking,
lossless compressed recording, and bundle transfer verification.
"""

from .interfaces import (
    sanitize_observation,
    validate_ask_batch,
    validate_match_batch,
    validate_policy_memory,
    PublicProtocolError,
)
from .metrics import compute_run_metrics
from .leases import CellLease, LeaseManager, LeaseError
from .recorder import DurableRecorder, AttemptLogger
from .runner import RegisteredRunner, RunnerBlockerError
from .transfer import BundleTransferManager

__all__ = [
    "sanitize_observation",
    "validate_ask_batch",
    "validate_match_batch",
    "validate_policy_memory",
    "PublicProtocolError",
    "compute_run_metrics",
    "CellLease",
    "LeaseManager",
    "LeaseError",
    "DurableRecorder",
    "AttemptLogger",
    "RegisteredRunner",
    "RunnerBlockerError",
    "BundleTransferManager",
]
