"""Policies for Research 8 soft query trial."""

from .g import decide as decide_g
from .g_random_soft import decide as decide_g_random_soft
from .g_targeted_soft import decide as decide_g_targeted_soft

__all__ = ["decide_g", "decide_g_random_soft", "decide_g_targeted_soft"]
