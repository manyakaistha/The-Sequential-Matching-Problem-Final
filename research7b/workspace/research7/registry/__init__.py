"""Research 7 Coordinator Registry Scaffolding.

Provides frozen experiment registration schemas, validators, append-only decision ledgers,
and global agent delegation tracking.
"""

from .schema import (
    RegistrationStatus,
    ExperimentRegistration,
    CellKey,
    validate_registration_schema,
)
from .validator import RegistrationValidator
from .decisions import DecisionLedger
from .delegations import DelegationManager

__all__ = [
    "RegistrationStatus",
    "ExperimentRegistration",
    "CellKey",
    "validate_registration_schema",
    "RegistrationValidator",
    "DecisionLedger",
    "DelegationManager",
]
