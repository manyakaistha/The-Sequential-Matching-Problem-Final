"""Reviewed launch entrypoint anchoring the immutable design's complete bytes."""
import hashlib
from pathlib import Path

EXPECTED_DESIGN_SHA256='56a8eb63200c069d3a64185c716ab62986d61f423a762e675d16f22f389663dc'
def verify_registration():
    current=hashlib.sha256(Path('results/research5/design.json').read_bytes()).hexdigest()
    if current!=EXPECTED_DESIGN_SHA256:raise ValueError('Complete design bytes differ from independent registration anchor; refuse launch')
def main():
    print('[START] Sequential matching confirmation test', flush=True)
    verify_registration()
    from research5.run_test import main as execute
    execute()
    verify_registration()
if __name__=='__main__':main()
