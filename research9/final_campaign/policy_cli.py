"""Cold public-policy adapter. Import isolation is not a filesystem/network sandbox."""
import importlib
import json
import resource
import sys
import time


def main():
    root, entrypoint, wire_limit = sys.argv[1:]
    sys.path.insert(0, root)
    limit = int(wire_limit)
    data = sys.stdin.buffer.read(limit + 1)
    if len(data) > limit:
        raise ValueError('request exceeds wire limit')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('nonfinite JSON value: ' + value)
    payload = json.loads(data, object_pairs_hook=pairs, parse_constant=constant)
    if set(payload) != {'request', 'config'}:
        raise ValueError('invalid public envelope')
    module_name, function_name = entrypoint.split(':')
    if not module_name.startswith(('research9.final_campaign.', 'research8.soft_query_trial.policies.', 'research8.soft_query_followup.v2.')):
        raise ValueError('entrypoint outside allowed source packages')
    module = importlib.import_module(module_name)
    start = time.monotonic()
    response = getattr(module, function_name)(payload['request'], payload['config'])
    status = getattr(module, 'LAST_STATUS', {})
    envelope = {'response': response, 'telemetry': {
        'elapsed_seconds': time.monotonic() - start,
        'fallback': bool(status.get('fallback', False)),
        'reason': status.get('reason'),
        'rss_raw': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'rss_units': 'bytes' if sys.platform == 'darwin' else 'KiB',
    }}
    encoded = json.dumps(envelope, allow_nan=False).encode()
    if len(encoded) > limit:
        raise ValueError('response exceeds wire limit')
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
