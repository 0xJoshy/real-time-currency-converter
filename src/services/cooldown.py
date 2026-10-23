"""Cooldown for the manual Refresh button (FR-08).

No Tkinter here, and the clock can be replaced, so it is testable without a
window and without waiting.
"""

import math
import time


class Cooldown:
    """Blocks an action for `seconds` after it was last started."""

    def __init__(self, seconds: float, clock=time.monotonic):
        self._seconds = seconds
        self._clock = clock
        self._ready_at = 0.0

    def remaining(self) -> int:
        """Whole seconds left to wait. 0 means the action is allowed now."""
        return max(0, math.ceil(self._ready_at - self._clock()))

    def start(self) -> None:
        """Begin the cooldown from now."""
        self._ready_at = self._clock() + self._seconds
