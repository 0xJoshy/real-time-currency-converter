from unittest.mock import MagicMock, patch

import pytest
import requests

from services.rate_client import ExchangeRateClient, RateApiError


def fake_response(data=None, status=200, bad_json=False):
    resp = MagicMock()
    resp.status_code = status
    if bad_json:
        resp.json.side_effect = ValueError("not json")
    else:
        resp.json.return_value = data
    return resp


def fetch_error(**patch_kwargs):
    with patch("services.rate_client.requests.get", **patch_kwargs):
        with pytest.raises(RateApiError) as exc:
            ExchangeRateClient("SECRETKEY").fetch()
    return str(exc.value)


def test_success():
    data = {"result": "success", "base_code": "USD", "conversion_rates": {"USD": 1, "PHP": 58.2}}
    with patch("services.rate_client.requests.get", return_value=fake_response(data)):
        snap = ExchangeRateClient("k").fetch()
    assert snap.rates["PHP"] == 58.2 and snap.base == "USD"


def test_timeout_message():
    assert "timed out" in fetch_error(side_effect=requests.Timeout("SECRETKEY"))


def test_connection_message():
    assert "internet" in fetch_error(side_effect=requests.ConnectionError("SECRETKEY"))


def test_other_request_error_message():
    assert "Could not reach" in fetch_error(side_effect=requests.RequestException("SECRETKEY"))


def test_api_error_types():
    for kind, word in [("invalid-key", "invalid"), ("quota-reached", "limit"), ("inactive-account", "not active")]:
        msg = fetch_error(return_value=fake_response({"result": "error", "error-type": kind}))
        assert word in msg


def test_unknown_api_error_has_default_message():
    msg = fetch_error(return_value=fake_response({"result": "error", "error-type": "weird"}))
    assert "returned an error" in msg


def test_unreadable_and_server_down():
    assert "could not be read" in fetch_error(return_value=fake_response(bad_json=True))
    assert "unavailable" in fetch_error(return_value=fake_response(bad_json=True, status=503))


def test_incomplete_data():
    assert "incomplete" in fetch_error(return_value=fake_response({"result": "success"}))
    assert "incomplete" in fetch_error(
        return_value=fake_response({"result": "success", "conversion_rates": {"PHP": 0, "X": "a"}}))


def test_messages_never_leak_the_key():
    for kwargs in [
        dict(side_effect=requests.Timeout("https://x/SECRETKEY/latest")),
        dict(side_effect=requests.ConnectionError("https://x/SECRETKEY/latest")),
        dict(return_value=fake_response({"result": "error", "error-type": "invalid-key"})),
    ]:
        assert "SECRETKEY" not in fetch_error(**kwargs)
