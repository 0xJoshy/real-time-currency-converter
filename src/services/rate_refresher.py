"""Keeps the latest rates cached and refreshes them on a fixed interval (FR-04)."""
import threading
import time
from typing import Callable, Optional

from models.rate_snapshot import RateSnapshot


class RateRefresher:
    """Background refresh of rates.

    - Holds the latest good snapshot; a failed refresh keeps the old one.
    - Refreshes every `interval_seconds` on a daemon thread.
    - Manual refreshes are rate-limited by `manual_cooldown_seconds` so the
      user cannot burn through the API's free-tier quota.
    """

    def __init__(
        self,
        fetch: Callable[[], RateSnapshot],
        interval_seconds: float,
        manual_cooldown_seconds: float = 60,
    ):
        self._fetch = fetch
        self._interval = interval_seconds
        self._cooldown = manual_cooldown_seconds
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._snapshot: Optional[RateSnapshot] = None
        self._last_error: Optional[str] = None
        self._last_attempt = 0.0

    # --- state -----------------------------------------------------------
    @property
    def snapshot(self) -> Optional[RateSnapshot]:
        with self._lock:
            return self._snapshot

    @property
    def last_error(self) -> Optional[str]:
        with self._lock:
            return self._last_error

    @property
    def interval_seconds(self) -> float:
        return self._interval

    # --- refresh ---------------------------------------------------------
    def refresh(self) -> bool:
        """Fetch now. Returns True on success; keeps old rates on failure."""
        try:
            snapshot = self._fetch()
        except Exception as exc:  # the thread must never die (reliability NFR)
            with self._lock:
                self._last_error = str(exc)
                self._last_attempt = time.monotonic()
            return False
        with self._lock:
            self._snapshot = snapshot
            self._last_error = None
            self._last_attempt = time.monotonic()
        return True

    def manual_refresh(self) -> tuple:
        """User-triggered refresh. Returns (ok, message)."""
        with self._lock:
            wait = self._cooldown - (time.monotonic() - self._last_attempt)
        if self._last_attempt and wait > 0:
            return False, f"Please wait {int(wait) + 1}s before refreshing again."
        if self.refresh():
            return True, "Rates refreshed."
        return False, self.last_error or "Refresh failed."

    # --- background loop -------------------------------------------------
    def start(self) -> bool:
        """Do the first fetch, then keep refreshing in the background."""
        ok = self.refresh()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return ok

    def _loop(self) -> None:
        while not self._stop.wait(self._interval):
            self.refresh()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
