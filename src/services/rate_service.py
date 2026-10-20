"""Holds the latest good rates. A failed refresh never erases them (FR-07)."""

import threading
from dataclasses import dataclass
from typing import Callable, Optional

from models.rate_snapshot import RateSnapshot
from services.rate_client import RateApiError


@dataclass(frozen=True)
class RefreshResult:
    ok: bool
    message: str  # plain text for the status label


class RateService:
    def __init__(self, fetch: Callable[[], RateSnapshot]):
        self._fetch = fetch
        self._lock = threading.Lock()
        self._snapshot: Optional[RateSnapshot] = None
        self._last_error: Optional[str] = None

    @property
    def snapshot(self) -> Optional[RateSnapshot]:
        with self._lock:
            return self._snapshot

    @property
    def last_error(self) -> Optional[str]:
        with self._lock:
            return self._last_error

    def refresh(self) -> RefreshResult:
        """Fetch new rates. Never raises; the result says what happened."""
        try:
            snapshot = self._fetch()
        except RateApiError as err:
            message = str(err)
        except Exception:
            message = "Something went wrong while updating the rates."
        else:
            with self._lock:
                self._snapshot = snapshot
                self._last_error = None
            return RefreshResult(True, "Rates updated.")

        with self._lock:
            old = self._snapshot
            if old is not None:
                message += f" Using the rates from {old.fetched_at:%Y-%m-%d %H:%M:%S}."
            self._last_error = message
        return RefreshResult(False, message)
