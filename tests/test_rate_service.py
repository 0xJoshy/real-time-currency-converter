from datetime import datetime

from models.rate_snapshot import RateSnapshot
from services.rate_client import RateApiError
from services.rate_service import RateService


def snap():
    return RateSnapshot("USD", {"USD": 1.0, "PHP": 58.0}, datetime(2026, 1, 2, 3, 4, 5))


def test_first_failure_leaves_no_rates():
    def fail():
        raise RateApiError("No internet connection.")
    svc = RateService(fail)
    result = svc.refresh()
    assert not result.ok and result.message == "No internet connection."
    assert svc.snapshot is None


def test_failure_keeps_last_good_rates():
    state = {"fail": False}
    good = snap()
    def fetch():
        if state["fail"]:
            raise RateApiError("The request timed out.")
        return good
    svc = RateService(fetch)
    assert svc.refresh().ok
    state["fail"] = True
    result = svc.refresh()
    assert not result.ok
    assert svc.snapshot is good
    assert "2026-01-02 03:04:05" in result.message
    assert svc.last_error == result.message


def test_unexpected_exception_does_not_crash():
    def boom():
        raise KeyError("secret detail")
    result = RateService(boom).refresh()
    assert not result.ok and "secret detail" not in result.message


def test_success_clears_error():
    state = {"fail": True}
    def fetch():
        if state["fail"]:
            raise RateApiError("x")
        return snap()
    svc = RateService(fetch)
    svc.refresh()
    state["fail"] = False
    assert svc.refresh().ok and svc.last_error is None
