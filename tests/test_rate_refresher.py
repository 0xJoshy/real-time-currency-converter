import time
from datetime import datetime

from models.rate_snapshot import RateSnapshot
from services.rate_refresher import RateRefresher


def make_snapshot():
    return RateSnapshot("USD", {"USD": 1.0, "PHP": 58.0, "EUR": 0.9}, datetime.now())


def test_start_fetches_immediately():
    r = RateRefresher(make_snapshot, interval_seconds=100)
    assert r.start() is True
    assert r.snapshot is not None
    r.stop()


def test_auto_refresh_runs_on_interval():
    calls = []
    def fetch():
        calls.append(1)
        return make_snapshot()
    r = RateRefresher(fetch, interval_seconds=0.05)
    r.start()
    time.sleep(0.3)
    r.stop()
    assert len(calls) >= 3


def test_failed_refresh_keeps_old_rates_and_thread_survives():
    state = {"fail": False, "n": 0}
    def fetch():
        state["n"] += 1
        if state["fail"]:
            raise RuntimeError("boom")
        return make_snapshot()
    r = RateRefresher(fetch, interval_seconds=0.05)
    r.start()
    good = r.snapshot
    state["fail"] = True
    time.sleep(0.2)
    assert r.snapshot is good
    assert r.last_error == "boom"
    state["fail"] = False
    time.sleep(0.2)
    r.stop()
    assert r.last_error is None


def test_manual_refresh_cooldown():
    r = RateRefresher(make_snapshot, interval_seconds=100, manual_cooldown_seconds=60)
    r.start()
    ok, msg = r.manual_refresh()
    assert ok is False and "wait" in msg.lower()
    r.stop()


def test_cross_rate():
    assert make_snapshot().rate("EUR", "PHP") == 58.0 / 0.9
