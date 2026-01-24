import pytest

from src.infra.config_loader import _parse_probe, _parse_config

from src.domain import Probe
from src.common.result import Err, Ok


def test_parse_probe_success():
    probe_dict = {
        "name": "example",
        "url": "https://example.com",
        "schedule": "5 4 * * *",
    }

    res = _parse_probe(probe_dict)
    match res:
        case Ok(p):
            # config_loader defaults checkCert to True when absent
            assert p == Probe(
                name="example",
                url="https://example.com",
                schedule="5 4 * * *",
                checkCert=True,
            )
        case Err(e):
            pytest.fail(f"Expected Success but got Failure: {e}")


def test_parse_probe_checkCert_true():
    probe_dict = {
        "name": "with-check",
        "url": "https://with-check.example",
        "schedule": "0 0 * * *",
        "checkCert": True,
    }

    res = _parse_probe(probe_dict)
    match res:
        case Ok(p):
            assert p.checkCert is True
        case Err(e):
            pytest.fail(f"Expected Success but got Failure: {e}")


def test_parse_probe_checkCert_false():
    probe_dict = {
        "name": "without-check",
        "url": "https://without-check.example",
        "schedule": "0 0 * * *",
        "checkCert": False,
    }

    res = _parse_probe(probe_dict)
    match res:
        case Ok(p):
            assert p.checkCert is False
        case Err(e):
            pytest.fail(f"Expected Success but got Failure: {e}")


def test_parse_probe_missing_name():
    probe = {
        "url": "https://no-name.example",
        "schedule": "0 0 * * *",
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
        "schedule": "0 0 * * *",
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
    }

    res = _parse_probe(probe)
    match res:
        case Err(errs):
            assert any("Probe schedule is required" in e for e in errs)
        case Ok(_):
            pytest.fail("Expected Failure when probe schedule is missing")


def test_parse_config_with_sink_success():
    config = {
        "sink": {
            "kafka": {
                "cfg": {"bootstrap.servers": "localhost:9092", "security.protocol": "PLAINTEXT"},
                "topic": "ping-results",
            }
        },
        "probes": [
            {
                "name": "example",
                "url": "https://example.com",
                "schedule": "0 0 * * *",
            }
        ],
    }

    res = _parse_config(config)
    match res:
        case Ok((kafka_cfg, topic, probes)):
            assert kafka_cfg == {"bootstrap.servers": "localhost:9092", "security.protocol": "PLAINTEXT"}
            assert topic == "ping-results"
            assert probes == [Probe(name="example", url="https://example.com", schedule="0 0 * * *", checkCert=True)]
        case Err(e):
            pytest.fail(f"Expected Success but got Failure: {e}")


def test_parse_config_without_sink_defaults():
    config = {
        # no sink provided
        "probes": [
            {
                "name": "example2",
                "url": "https://example.org",
                "schedule": "0 * * * *",
            }
        ],
    }

    res = _parse_config(config)
    match res:
        case Ok((kafka_cfg, topic, probes)):
            assert kafka_cfg == {}
            assert topic == ""
            assert probes == [Probe(name="example2", url="https://example.org", schedule="0 * * * *", checkCert=True)]
        case Err(e):
            pytest.fail(f"Expected Success but got Failure: {e}")
