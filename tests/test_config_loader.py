import pytest

from src.infra.config_loader import _parse_check, _parse_probe

from src.domain import (
    StatusCodeCheck,
    ResponseTimeCheck,
    HashCheck,
    SslValidityCheck, Probe,
)
from src.common.result import Err, Ok


def test_parse_check_status_code_success():
    res = _parse_check({"type": "status_code", "expected_status_code": 200})

    match res:
        case Ok(v):
            assert v == StatusCodeCheck(expected_status_code=200)
        case Err(e):
            pytest.fail(f"Expected Success but got Failure: {e}")


def test_parse_check_response_time_success():
    res = _parse_check({"type": "response_time", "threshold_ms": 500})

    match res:
        case Ok(v):
            assert v == ResponseTimeCheck(threshold_ms=500)
        case Err(e):
            pytest.fail(f"Expected Success but got Failure: {e}")


def test_parse_check_hash_success():
    res = _parse_check({"type": "hash", "expected_hash": "abc123"})

    match res:
        case Ok(v):
            assert v == HashCheck(expected_hash="abc123")
        case Err(e):
            pytest.fail(f"Expected Success but got Failure: {e}")


def test_parse_check_ssl_validity_success():
    res = _parse_check({"type": "ssl_validity", "min_days_valid": 10})

    match res:
        case Ok(v):
            assert v == SslValidityCheck(min_days_valid=10)
        case Err(e):
            pytest.fail(f"Expected Success but got Failure: {e}")


def test_parse_check_invalid_failure():
    res = _parse_check({"type": "invalid_one"})

    match res:
        case Err(_):
            pass
        case Ok(_):
            pytest.fail(f"Expected Failure")


def test_parse_check_status_code_failure():
    res = _parse_check({"type": "status_code", "expected_code": 200})

    match res:
        case Err(_):
            pass
        case Ok(_):
            pytest.fail(f"Expected Failure")


def test_parse_check_response_time_failure():
    res = _parse_check({"type": "response_time", "threshold": 500})

    match res:
        case Err(_):
            pass
        case Ok(_):
            pytest.fail("Expected Failure")


def test_parse_check_hash_failure():
    res = _parse_check({"type": "hash", "hash": "abc123"})

    match res:
        case Err(_):
            pass
        case Ok(_):
            pytest.fail("Expected Failure")


def test_parse_check_ssl_validity_failure():
    res = _parse_check({"type": "ssl_validity", "min_days": 10})

    match res:
        case Err(_):
            pass
        case Ok(_):
            pytest.fail("Expected Failure")


def test_parse_check_non_mapping_failure():
    res = _parse_check(None)

    match res:
        case Err(_):
            pass
        case Ok(_):
            pytest.fail("Expected Failure")


def test_parse_probe_success():
    probe_dict = {
        "name": "example",
        "url": "https://example.com",
        "schedule": "5 4 * * *",
        "checks": [
            {"type": "status_code", "expected_status_code": 200},
            {"type": "response_time", "threshold_ms": 500},
            {"type": "hash", "expected_hash": "abc123"},
            {"type": "ssl_validity", "min_days_valid": 10},
        ],
    }

    res = _parse_probe(probe_dict)
    match res:
        case Ok(p):
            assert p == Probe(
                name="example",
                url="https://example.com",
                schedule="5 4 * * *",
                checks=[
                    StatusCodeCheck(expected_status_code=200),
                    ResponseTimeCheck(threshold_ms=500),
                    HashCheck(expected_hash="abc123"),
                    SslValidityCheck(min_days_valid=10),
                ],
            )
        case Err(e):
            pytest.fail(f"Expected Success but got Failure: {e}")


def test_parse_probe_missing_name():
    probe = {
        "url": "https://no-name.example",
        "schedule": "@daily",
        "checks": [{"type": "status_code", "expected_status_code": 200}],
    }

    res = _parse_probe(probe)
    match res:
        case Err(errs):
            assert any("Probe name is required" in e for e in errs)
        case Ok(_):
            pytest.fail("Expected Failure when probe name is missing")


def test_parse_probe_missing_url():
    probe = {
        "name": "no-url",
        "schedule": "@daily",
        "checks": [{"type": "status_code", "expected_status_code": 200}],
    }

    res = _parse_probe(probe)
    match res:
        case Err(errs):
            assert any("Probe url is required" in e for e in errs)
        case Ok(_):
            pytest.fail("Expected Failure when probe url is missing")


def test_parse_probe_missing_schedule():
    probe = {
        "name": "no-schedule",
        "url": "https://no-schedule.example",
        "checks": [{"type": "status_code", "expected_status_code": 200}],
    }

    res = _parse_probe(probe)
    match res:
        case Err(errs):
            assert any("Probe schedule is required" in e for e in errs)
        case Ok(_):
            pytest.fail("Expected Failure when probe schedule is missing")
