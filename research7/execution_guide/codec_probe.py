"""Offline only: opaque request-byte codec, no simulator/policy imports.

Framing is prototype v1, not an admitted production log format. All sizes are
bounded by MAX_RECORD; each checkpoint decodes without any earlier record.
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
import random
from pathlib import Path
import struct
import time
import zlib

MAX_RECORD = 16 * 1024 * 1024
MAX_CHUNKS = 32768
HEADER = struct.Struct('>4sBQQ32s32s32s')
OP = struct.Struct('>BQQ')
ZERO = bytes(32)


def digest(raw):
    return hashlib.sha256(raw).digest()


def chunks(raw):
    """Opaque exact-byte boundaries; valid also for arbitrary non-JSON bytes."""
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


def delta(raw, previous):
    # At most one previous-record byte string plus a linear-size index.
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
    return b''.join(operations)


def encode(raw, previous=None, checkpoint=False):
    if len(raw) > MAX_RECORD:
        raise ValueError('record exceeds cap')
    full = zlib.compress(raw, 6)
    # Uncompressed full fallback provides strict additive growth bound.
    mode, payload = (0, raw) if len(full) >= len(raw) else (1, full)
    if previous is not None and not checkpoint:
        difference = delta(raw, previous)
        candidate = zlib.compress(difference, 6) if difference is not None else None
        if candidate is not None and len(candidate) < len(payload):
            mode, payload = 2, candidate
    basis = digest(previous) if mode == 2 else ZERO
    return HEADER.pack(b'R7C1', mode, len(raw), len(payload), basis,
                       digest(raw), digest(payload)) + payload


def inflate(payload, cap):
    decoder = zlib.decompressobj()
    result = decoder.decompress(payload, cap + 1)
    if len(result) > cap or decoder.unconsumed_tail or not decoder.eof or decoder.unused_data:
        raise ValueError('invalid compressed payload or expansion cap')
    return result


def decode(frame, previous=None):
    if len(frame) < HEADER.size:
        raise ValueError('truncated header')
    magic, mode, size, packed, basis, sha, payload_sha = HEADER.unpack(frame[:HEADER.size])
    if magic != b'R7C1' or mode not in (0, 1, 2) or size > MAX_RECORD or packed > MAX_RECORD:
        raise ValueError('invalid header')
    payload = frame[HEADER.size:]
    if len(payload) != packed or digest(payload) != payload_sha:
        raise ValueError('truncated/corrupt payload')
    if mode != 2 and basis != ZERO:
        raise ValueError('non-delta basis')
    if mode == 0:
        raw = payload
    elif mode == 1:
        raw = inflate(payload, size)
    else:
        if previous is None or digest(previous) != basis:
            raise ValueError('missing/wrong predecessor')
        # Each opaque chunk >=2 bytes, op <=17 bytes; conservative linear cap.
        ops = inflate(payload, 10 * size + OP.size)
        raw = bytearray()
        cursor = 0
        while cursor < len(ops):
            if len(ops) - cursor < OP.size:
                raise ValueError('truncated operation')
            kind, offset, count = OP.unpack(ops[cursor:cursor + OP.size])
            cursor += OP.size
            if len(raw) + count > size:
                raise ValueError('output size violation')
            if kind == 0 and offset == 0 and cursor + count <= len(ops):
                raw.extend(ops[cursor:cursor + count]); cursor += count
            elif kind == 1 and offset + count <= len(previous):
                raw.extend(previous[offset:offset + count])
            else:
                raise ValueError('invalid copy/literal')
        raw = bytes(raw)
    if len(raw) != size or digest(raw) != sha:
        raise ValueError('record digest/length mismatch')
    return raw


def persist_before_call(path, frame):
    """Illustrative single-writer contract; caller invokes inference only on return.

Production requires durable directory creation, tested filesystem guarantees,
attempt/sequence identity, exclusive writer and separate completion protocol.
"""
    with open(path, 'ab') as stream:
        stream.write(frame)
        stream.flush()
        os.fsync(stream.fileno())


def read_frames(stream):
    """Yield only complete frames; fail closed on an incomplete/corrupt tail.

Recovery may keep the previously yielded complete prefix but must never claim
the incomplete request was persisted or that its inference call happened.
"""
    while True:
        header = stream.read(HEADER.size)
        if not header:
            return
        if len(header) != HEADER.size:
            raise ValueError('truncated archive header')
        packed = HEADER.unpack(header)[3]
        if packed > MAX_RECORD:
            raise ValueError('archive payload cap')
        payload = stream.read(packed)
        if len(payload) != packed:
            raise ValueError('truncated archive payload')
        yield header + payload


def failures():
    rows = []
    rng = random.Random(0)
    previous = b'},'.join(rng.randbytes(128) for _ in range(1000))
    raw = previous + b'\xff\x00 malformed { ordering \xfe'
    frame = encode(raw, previous)
    assert frame[4] == 2
    assert decode(frame, previous) == raw
    assert decode(encode(b'')) == b''
    assert decode(encode(bytes(range(256)) * 3)) == bytes(range(256)) * 3
    assert delta(b'},' * (MAX_CHUNKS + 1), previous) is None
    for name, bad, basis in [('truncated', frame[:-1], previous),
                              ('bit_flip', frame[:-1] + bytes([frame[-1] ^ 1]), previous),
                              ('missing_basis', frame, None),
                              ('wrong_basis', frame, b'wrong'),
                              ('header_flip', bytes([frame[0] ^ 1]) + frame[1:], previous)]:
        try:
            decode(bad, basis)
        except ValueError:
            rows.append(name)
        else:
            raise AssertionError(name)
    for name, ops in [('copy_bounds', OP.pack(1, len(previous), len(raw))),
                      ('output_overrun', OP.pack(1, 0, len(raw) + 1)),
                      ('unknown_operation', OP.pack(9, 0, 1)),
                      ('truncated_operation', b'\x01'),
                      ('expansion_cap', b'x' * (10 * len(raw) + OP.size + 1))]:
        payload = zlib.compress(ops)
        invalid = HEADER.pack(b'R7C1', 2, len(raw), len(payload), digest(previous),
                              digest(raw), digest(payload)) + payload
        try:
            decode(invalid, previous)
        except ValueError:
            rows.append(name)
        else:
            raise AssertionError(name)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    begin = time.process_time()
    commits = [json.loads(p.read_text()) for p in sorted((args.source / 'commits').glob('*.json'))]
    eligible = [c for c in commits if c['cell']['policy_id'] == 'G']
    seeds = sorted({c['cell']['seed'] for c in eligible})[:2]
    families = sorted({c['cell']['family'] for c in eligible})
    chosen = sorted((c for c in eligible if c['cell']['seed'] in seeds),
                    key=lambda c: (c['cell']['seed'], c['cell']['family']))
    assert len(families) == 6 and len(chosen) == 12
    args.output.mkdir(parents=True, exist_ok=True)
    # Predeclare selection in a persisted manifest before reading wire payloads.
    declaration = {'selection': 'G; first two ascending seeds; all six families; no outcome selection',
                   'seeds': seeds, 'families': families,
                   'cells': [{'key': c['cell_key_hash'], 'attempt': c['attempt_id'],
                              'seed': c['cell']['seed'], 'family': c['cell']['family']} for c in chosen]}
    (args.output / 'sample_manifest.json').write_text(json.dumps(declaration, indent=2) + '\n')
    rows = []
    for commit in chosen:
        attempt = args.source / 'attempts' / commit['cell_key_hash'] / commit['attempt_id']
        previous = None
        row = dict(seed=commit['cell']['seed'], family=commit['cell']['family'], records=0,
                   request_raw_bytes=0, request_existing_bytes=0, segment_existing_bytes=0,
                   codec_request_bytes=0, codec_completion_bytes=0, full_request_zlib_bytes=0,
                   checkpoints=0, delta_frames=0, codec_cpu_seconds=0)
        target = args.output / (str(row['seed']) + '_' + row['family'] + '.r7c')
        with target.open('wb') as stream:
            for request_path in sorted((attempt / 'public').glob('*.request.bin')):
                if time.process_time() - begin > 170:
                    raise RuntimeError('CPU safety budget reached')
                req = json.loads(gzip.decompress(request_path.read_bytes()))
                raw = base64.b64decode(req['wire_request_base64'], validate=True)
                seq = req['sequence']
                candidates = list((attempt / 'public' / 'segments').glob(f'{seq:03d}_*.bin'))
                assert len(candidates) == 1
                segment_path = candidates[0]
                segment = json.loads(gzip.decompress(segment_path.read_bytes()))
                assert base64.b64decode(segment['wire_request_base64'], validate=True) == raw
                response = base64.b64decode(segment['wire_response_base64'], validate=True)
                completion = {k: v for k, v in segment.items() if k not in
                              ('wire_request_base64', 'wire_request_utf8', 'wire_response_base64', 'wire_response_utf8')}
                completion['request_sha256'] = digest(raw).hex()
                completion['response_base64'] = base64.b64encode(response).decode('ascii')
                completion['request_envelope'] = {k: v for k, v in req.items() if k != 'wire_request_base64'}
                # Preserve replacement-decoded display fields as metadata when needed.
                for key, wire in [('wire_request_utf8', raw), ('wire_response_utf8', response)]:
                    assert segment[key] == wire.decode('utf8', errors='replace')
                meta = json.dumps(completion, ensure_ascii=False, separators=(',', ':')).encode('utf8')
                checkpoint = row['records'] % 12 == 0
                cpu_start = time.process_time()
                frame = encode(raw, previous, checkpoint)
                assert decode(frame, None if checkpoint else previous) == raw
                complete_frame = encode(meta)
                assert json.loads(decode(complete_frame)) == completion
                assert base64.b64decode(json.loads(decode(complete_frame))['response_base64']) == response
                row['codec_cpu_seconds'] += time.process_time() - cpu_start
                stream.write(frame); stream.write(complete_frame)
                row['records'] += 1
                row['checkpoints'] += int(checkpoint)
                row['delta_frames'] += int(frame[4] == 2)
                row['request_raw_bytes'] += len(raw)
                row['request_existing_bytes'] += request_path.stat().st_size
                row['segment_existing_bytes'] += segment_path.stat().st_size
                row['codec_request_bytes'] += len(frame)
                row['codec_completion_bytes'] += len(complete_frame)
                row['full_request_zlib_bytes'] += len(zlib.compress(raw, 6)) + HEADER.size
                previous = raw
        rows.append(row)
    disk_verified = 0
    for archive in sorted(args.output.glob('*.r7c')):
        previous = None
        with archive.open('rb') as stream:
            frames = iter(read_frames(stream))
            for frame in frames:
                request = decode(frame, previous)
                completion = json.loads(decode(next(frames)))
                assert completion['request_sha256'] == digest(request).hex()
                previous = request
                disk_verified += 1
    result = {'scope': 'offline prototype exact wire bytes; metadata semantic preservation; no source gzip-byte preservation',
              'header_bytes': HEADER.size, 'max_record_bytes': MAX_RECORD, 'checkpoint_interval': 12,
              'failure_cases_detected': failures(), 'disk_verified_records': disk_verified, 'rows': rows,
              'total_cpu_seconds': time.process_time() - begin,
              'totals': {k: sum(r[k] for r in rows) for k in rows[0] if k not in ('seed', 'family')}}
    (args.output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['totals'], indent=2))
    print('total_cpu_seconds', result['total_cpu_seconds'])


if __name__ == '__main__':
    main()
