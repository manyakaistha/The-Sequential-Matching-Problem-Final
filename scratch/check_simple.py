import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from research.terminal_model import update_memory
import json
memory = update_memory({'day': 0, 'members': []}, {}, {'learning': True})
print("Simple funnel:", memory['simple_funnel'])
