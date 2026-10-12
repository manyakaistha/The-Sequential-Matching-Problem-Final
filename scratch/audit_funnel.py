import collections
import itertools
import json
import math
import sys
from pathlib import Path

# Add kit.py to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kit import Simulator, generate, eligibility
from evaluate import execute
from research_policy import FEATURES

# For simple_fifo, we can run it using imported logic.
from extended_policy import decide as decide_extended

def decide_simple_fifo(request):
    return decide_extended(request, config={"model": "simple"})

from policy import decide as decide_greedy

print("Script written successfully.")
