"""Lossless streaming journal codec for Research 7 (Format Version 2).

Preserves byte-exact wire payloads with opaque COPY/literal delta frames,
strict CRC/SHA-256 integrity verification, and crash-resilient pre-inference durability.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import struct
import time
from typing import Any, Dict, Generator, Optional, Tuple
import zlib


MAX_RECORD = 16 * 1024 * 1024  # 16 MiB
MAX_CHUNKS = 32768
# Header format: 4s magic (R7C1), B mode (0:raw, 1:zlib, 2:delta), Q uncompressed_len,
# Q packed_len, 32s predecessor_basis_sha256, 32s raw_sha256, 32s payload_sha256
HEADER = struct.Struct('>4sBQQ32s32s32s')  # 117 bytes
OP = struct.Struct('>BQQ')  # 17 bytes (kind: 0=literal, 1=copy; offset: uint64, count: uint64)
ZERO = bytes(32)


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(raw: bytes) -> bytes:
    return hashlib.sha256(raw).digest()


def chunks(raw: bytes):
    """Opaque exact-byte boundaries splitting at b'},'."""
    start = 0
    while True:
        end = raw.find(b'},', start)
        if end < 0:
            if start < len(raw):
                yield start, raw[start:]
            return
        end += 2
        yield start, raw[start:end]
        start = end


def delta(raw: bytes, previous: bytes) -> Optional[bytes]:
    """Single-pass dictionary chunk index producing COPY and LITERAL operations."""
    index = {}
    for count, (offset, piece) in enumerate(chunks(previous)):
        if count >= MAX_CHUNKS:
            return None
        index.setdefault(piece, offset)
    operations = []
    literal = bytearray()
    for count, (_, piece) in enumerate(chunks(raw)):
        if count >= MAX_CHUNKS:
            return None
        offset = index.get(piece)
        if offset is None:
            literal.extend(piece)
        else:
            if literal:
                operations.append(OP.pack(0, 0, len(literal)) + literal)
                literal.clear()
            operations.append(OP.pack(1, offset, len(piece)))
    if literal:
        operations.append(OP.pack(0, 0, len(literal)) + literal)
    return bytes(b''.join(operations))


def encode(raw: bytes, previous: Optional[bytes] = None, checkpoint: bool = False) -> bytes:
    """Encode raw bytes with delta, zlib, or uncompressed literal fallback."""
    if len(raw) > MAX_RECORD:
        raise ValueError(f'Record length {len(raw)} exceeds cap {MAX_RECORD}')
    full = zlib.compress(raw, 6)
    # Mode 0: literal uncompressed fallback (bounded growth guarantee)
    # Mode 1: zlib compressed
    mode, payload = (0, raw) if len(full) >= len(raw) else (1, full)
    if previous is not None and not checkpoint:
        difference = delta(raw, previous)
        candidate = zlib.compress(difference, 6) if difference is not None else None
        if candidate is not None and len(candidate) < len(payload):
            mode, payload = 2, candidate
    basis = digest(previous) if mode == 2 else ZERO
    return HEADER.pack(b'R7C1', mode, len(raw), len(payload), basis,
                       digest(raw), digest(payload)) + payload


def inflate(payload: bytes, cap: int) -> bytes:
    decoder = zlib.decompressobj()
    result = decoder.decompress(payload, cap + 1)
    if len(result) > cap or decoder.unconsumed_tail or not decoder.eof or decoder.unused_data:
        raise ValueError('Invalid compressed payload or expansion cap exceeded')
    return result


def decode(frame: bytes, previous: Optional[bytes] = None) -> bytes:
    """Decode a single R7C1 frame with strict integrity and bounds checks."""
    if len(frame) < HEADER.size:
        raise ValueError('Truncated frame header')
    magic, mode, size, packed, basis, sha, payload_sha = HEADER.unpack(frame[:HEADER.size])
    if magic != b'R7C1' or mode not in (0, 1, 2) or size > MAX_RECORD or packed > MAX_RECORD:
        raise ValueError(f'Invalid header fields: magic={magic}, mode={mode}, size={size}, packed={packed}')
    payload = frame[HEADER.size:]
    if len(payload) != packed or digest(payload) != payload_sha:
        raise ValueError('Truncated or corrupt frame payload')
    if mode != 2 and basis != ZERO:
        raise ValueError('Non-delta frame must have zero basis')
    if mode == 0:
        raw = payload
    elif mode == 1:
        raw = inflate(payload, size)
    else:
        if previous is None or digest(previous) != basis:
            raise ValueError('Missing or incorrect predecessor basis for delta frame')
        ops = inflate(payload, 10 * size + OP.size)
        raw = bytearray()
        cursor = 0
        while cursor < len(ops):
            if len(ops) - cursor < OP.size:
                raise ValueError('Truncated operation in delta stream')
            kind, offset, count = OP.unpack(ops[cursor:cursor + OP.size])
            cursor += OP.size
            if len(raw) + count > size:
                raise ValueError('Delta operation exceeds decoded output size cap')
            if kind == 0 and offset == 0 and cursor + count <= len(ops):
                raw.extend(ops[cursor:cursor + count])
                cursor += count
            elif kind == 1 and offset + count <= len(previous):
                raw.extend(previous[offset:offset + count])
            else:
                raise ValueError('Invalid copy/literal delta operation')
        raw = bytes(raw)
    if len(raw) != size or digest(raw) != sha:
        raise ValueError('Decoded record digest or length mismatch')
    return raw


def read_frames(stream) -> Generator[bytes, None, None]:
    """Yield complete frames from a binary stream.

    Raises ValueError on truncated header or truncated payload.
    """
    while True:
        header = stream.read(HEADER.size)
        if not header:
            return
        if len(header) != HEADER.size:
            raise ValueError('Truncated archive header')
        packed = HEADER.unpack(header)[3]
        if packed > MAX_RECORD:
            raise ValueError('Archive packed size exceeds maximum record cap')
        payload = stream.read(packed)
        if len(payload) != packed:
            raise ValueError('Truncated archive payload')
        yield header + payload


@dataclass
class JournalEntryInfo:
    sequence: int
    day: int
    phase: str
    kind: str  # 'request' or 'completion'
    offset: int
    length: int
    sha256: str
    timestamp_utc: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JournalWriter:
    """Append-only, fsync-durability journal writer for a single attempt."""

    def __init__(self, journal_path: Path, index_path: Optional[Path] = None, checkpoint_interval: int = 12):
        self.journal_path = Path(journal_path)
        self.index_path = Path(index_path) if index_path else None
        self.checkpoint_interval = checkpoint_interval
        self._journal_file = None
        self._index_file = None
        self._previous_request_record: Optional[bytes] = None
        self._offset = 0

    def open(self):
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        self._journal_file = self.journal_path.open('a+b')
        self._journal_file.seek(0, os.SEEK_END)
        self._offset = self._journal_file.tell()
        if self.index_path:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            self._index_file = self.index_path.open('a+b')

    def close(self):
        if self._journal_file:
            try:
                self._journal_file.flush()
                os.fsync(self._journal_file.fileno())
            finally:
                self._journal_file.close()
                self._journal_file = None
        if self._index_file:
            try:
                self._index_file.flush()
                os.fsync(self._index_file.fileno())
            finally:
                self._index_file.close()
                self._index_file = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def persist_request(self, sequence: int, day: int, phase: str, attempt_id: str, wire_request: bytes) -> JournalEntryInfo:
        """Durable pre-inference request persistence.
        
        Persists exact envelope and wire request before inference starts.
        Fsyncs to disk immediately.
        """
        if not self._journal_file:
            self.open()
        envelope = {
            "record_kind": "request",
            "attempt_id": attempt_id,
            "sequence": sequence,
            "day": day,
            "phase": phase,
            "timestamp_utc": stamp(),
            "wire_bytes_len": len(wire_request),
        }
        envelope_bytes = json.dumps(envelope, separators=(',', ':'), sort_keys=True).encode('ascii')
        record_bytes = envelope_bytes + b'\n' + wire_request

        checkpoint = (sequence % self.checkpoint_interval == 1) or (self._previous_request_record is None)
        frame = encode(record_bytes, self._previous_request_record, checkpoint=checkpoint)

        offset = self._offset
        self._journal_file.seek(offset)
        self._journal_file.write(frame)
        self._journal_file.flush()
        os.fsync(self._journal_file.fileno())
        self._offset += len(frame)

        self._previous_request_record = record_bytes

        info = JournalEntryInfo(
            sequence=sequence,
            day=day,
            phase=phase,
            kind="request",
            offset=offset,
            length=len(frame),
            sha256=hashlib.sha256(frame).hexdigest(),
            timestamp_utc=envelope["timestamp_utc"],
        )
        if self._index_file:
            self._index_file.write((json.dumps(info.to_dict(), sort_keys=True) + '\n').encode('utf-8'))
            self._index_file.flush()
            os.fsync(self._index_file.fileno())

        return info

    def persist_completion(
        self,
        sequence: int,
        day: int,
        phase: str,
        attempt_id: str,
        wire_request: bytes,
        wire_response: bytes,
        memory_before: Any,
        memory_after: Any,
        action: Any,
        policy_status: Dict[str, Any],
        stdout_text: str,
        stderr_text: str,
        elapsed_seconds: float,
        cpu_seconds: float,
    ) -> JournalEntryInfo:
        """Post-inference completion persistence.
        
        Persists exact wire response, execution metadata and policy output.
        Fsyncs to disk immediately.
        """
        if not self._journal_file:
            self.open()
        import base64
        completion = {
            "record_kind": "completion",
            "attempt_id": attempt_id,
            "sequence": sequence,
            "day": day,
            "phase": phase,
            "request_sha256": hashlib.sha256(wire_request).hexdigest(),
            "wire_response_base64": base64.b64encode(wire_response).decode('ascii'),
            "memory_before": memory_before,
            "memory_after": memory_after,
            "action": action,
            "policy_status": policy_status,
            "stdout": stdout_text,
            "stderr": stderr_text,
            "elapsed_seconds": elapsed_seconds,
            "cpu_seconds": cpu_seconds,
            "timestamp_utc": stamp(),
        }
        completion_raw = json.dumps(completion, separators=(',', ':'), sort_keys=True).encode('utf-8')
        complete_frame = encode(completion_raw)

        offset = self._offset
        self._journal_file.seek(offset)
        self._journal_file.write(complete_frame)
        self._journal_file.flush()
        os.fsync(self._journal_file.fileno())
        self._offset += len(complete_frame)

        info = JournalEntryInfo(
            sequence=sequence,
            day=day,
            phase=phase,
            kind="completion",
            offset=offset,
            length=len(complete_frame),
            sha256=hashlib.sha256(complete_frame).hexdigest(),
            timestamp_utc=completion["timestamp_utc"],
        )
        if self._index_file:
            self._index_file.write((json.dumps(info.to_dict(), sort_keys=True) + '\n').encode('utf-8'))
            self._index_file.flush()
            os.fsync(self._index_file.fileno())

        return info


def scan_journal(journal_path: Path) -> Dict[str, Any]:
    """Scan and verify a journal file.
    
    Detects:
    - valid frames
    - pairs of request/completion
    - whether file ends with an uncompleted request
    - whether file has a torn/corrupt tail
    """
    journal_path = Path(journal_path)
    if not journal_path.exists():
        return {"exists": False, "frames": [], "pairs": [], "torn_tail": False, "error": "File not found"}

    raw = journal_path.read_bytes()
    offset = 0
    frames = []
    pairs = []
    previous_request_record = None
    pending_request = None
    torn_tail = False
    error = None

    while offset < len(raw):
        remaining = raw[offset:]
        if len(remaining) < HEADER.size:
            torn_tail = True
            error = f"Torn header at offset {offset}: {len(remaining)} bytes remaining (need {HEADER.size})"
            break
        magic, mode, size, packed, basis, sha, payload_sha = HEADER.unpack(remaining[:HEADER.size])
        if magic != b'R7C1' or mode not in (0, 1, 2) or size > MAX_RECORD or packed > MAX_RECORD:
            torn_tail = True
            error = f"Corrupt header at offset {offset}"
            break
        frame_len = HEADER.size + packed
        if len(remaining) < frame_len:
            torn_tail = True
            error = f"Torn payload at offset {offset}: have {len(remaining) - HEADER.size} bytes, need {packed}"
            break
        frame_bytes = remaining[:frame_len]
        try:
            # Check payload digest
            if digest(frame_bytes[HEADER.size:]) != payload_sha:
                torn_tail = True
                error = f"Corrupt payload checksum at offset {offset}"
                break
            # Try decoding
            is_delta = (mode == 2)
            decoded = decode(frame_bytes, previous_request_record if is_delta else None)
        except Exception as exc:
            torn_tail = True
            error = f"Decode error at offset {offset}: {exc}"
            break

        frames.append({
            "offset": offset,
            "length": frame_len,
            "mode": mode,
            "size": size,
            "sha256": hashlib.sha256(frame_bytes).hexdigest(),
        })

        if b'\n' in decoded:
            first_line = decoded.split(b'\n', 1)[0]
            try:
                env = json.loads(first_line.decode('ascii'))
                if env.get("record_kind") == "request":
                    wire_req = decoded.split(b'\n', 1)[1]
                    pending_request = (env, wire_req)
                    previous_request_record = decoded
                    offset += frame_len
                    continue
            except Exception:
                pass

        try:
            comp = json.loads(decoded.decode('utf-8'))
            if comp.get("record_kind") == "completion":
                if pending_request is not None:
                    pairs.append({
                        "sequence": comp["sequence"],
                        "day": comp["day"],
                        "phase": comp["phase"],
                        "request_envelope": pending_request[0],
                        "request_sha256": hashlib.sha256(pending_request[1]).hexdigest(),
                        "completion": comp,
                    })
                    pending_request = None
                offset += frame_len
                continue
        except Exception:
            pass

        offset += frame_len

    return {
        "exists": True,
        "total_bytes": len(raw),
        "valid_bytes": offset if not torn_tail else offset,
        "frames_count": len(frames),
        "pairs_count": len(pairs),
        "pairs": pairs,
        "pending_request": pending_request[0] if pending_request else None,
        "torn_tail": torn_tail,
        "error": error,
    }
