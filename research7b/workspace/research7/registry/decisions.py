"""Append-only decision ledger for Research 7 coordinator."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class DecisionRecord:
    decision_id: str
    timestamp_utc: str
    phase: str
    author_role: str
    decision_type: str
    summary: str
    referenced_evidence: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, allow_nan=False)


class DecisionLedger:
    """Manages append-only decisions.jsonl with strict durability and fsync."""

    def __init__(self, ledger_path: Path):
        self.ledger_path = Path(ledger_path)

    def record_decision(
        self,
        phase: str,
        author_role: str,
        decision_type: str,
        summary: str,
        referenced_evidence: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DecisionRecord:
        record = DecisionRecord(
            decision_id=f"DEC-{uuid.uuid4().hex[:8]}",
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            phase=phase,
            author_role=author_role,
            decision_type=decision_type,
            summary=summary,
            referenced_evidence=referenced_evidence or [],
            metadata=metadata or {},
        )

        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        line = (record.to_json() + "\n").encode("utf-8")
        with self.ledger_path.open("ab") as stream:
            stream.write(line)
            stream.flush()
            os.fsync(stream.fileno())

        return record

    def list_decisions(self) -> List[DecisionRecord]:
        if not self.ledger_path.exists():
            return []
        records = []
        with self.ledger_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                records.append(
                    DecisionRecord(
                        decision_id=d["decision_id"],
                        timestamp_utc=d["timestamp_utc"],
                        phase=d["phase"],
                        author_role=d["author_role"],
                        decision_type=d["decision_type"],
                        summary=d["summary"],
                        referenced_evidence=d.get("referenced_evidence", []),
                        metadata=d.get("metadata", {}),
                    )
                )
        return records
