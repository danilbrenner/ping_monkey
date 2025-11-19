from pathlib import Path
from typing import Any, assert_never

import yaml

from src.domain import (
    Probe,
    ProbeCheck,
    StatusCodeCheck,
    ResponseTimeCheck,
    HashCheck,
    SslValidityCheck
)
from src.common.result import Result, Err, Ok, bind_result


def _parse_check(c: Any) -> ProbeCheck | str:
    if not isinstance(c, dict):
        return "Check entry must be a mapping"

    match c.get("type", ""):
        case "status_code":
            if "expected_status_code" not in c:
                return "Missing expected_status_code in status_code check"
            return StatusCodeCheck(
                expected_status_code=int(c.get("expected_status_code", ""))
            )

        case "response_time":
            if "threshold_ms" not in c:
                return "Missing threshold_ms in response_time check"
            return ResponseTimeCheck(
                threshold_ms=int(c.get("threshold_ms", ""))
            )

        case "hash":
            if "expected_hash" not in c:
                return "Missing expected_hash in hash check"
            return HashCheck(
                expected_hash=str(c.get("expected_hash", ""))
            )

        case "ssl_validity":
            if "min_days_valid" not in c:
                return "Missing min_days_valid in ssl_validity check"
            return SslValidityCheck(
                min_days_valid=int(c.get("min_days_valid", ""))
            )

        case t:
            return f"Unknown check type: {t}"


def _parse_probe(p: Any) -> Result[Probe, list[str]]:
    if not isinstance(p, dict):
        return Err(["Probe entry must be a mapping"])

    errors: list[str] = []
    checks: list[ProbeCheck] = []

    name = p.get("name", "")
    url = p.get("url", "")
    schedule = p.get("schedule", "")

    if not name:
        errors.append("Probe name is required")
    if not url:
        errors.append("Probe url is required")
    if not schedule:
        errors.append("Probe schedule is required")

    for idx, c in enumerate(p.get("checks", [])):
        v = _parse_check(c)
        match v:
            case str() as e:
                errors.append(e)
            case HashCheck() | SslValidityCheck() | ResponseTimeCheck() | StatusCodeCheck() as check:
                checks.append(check)
            case _ as unreachable:
                assert_never(unreachable)

    return Err(errors) if errors else Ok(Probe(
        name=name,
        url=url,
        schedule=schedule,
        checks=checks,
    ))


def _parse_config(config: dict[str, Any]) -> Result[tuple[dict[str, str], str, list[Probe]], list[str]]:
    sink = config.get("sink", {}).get("kafka", {})
    kafka_cfg = sink.get("cfg", {})
    topic = sink.get("topic", "")
    
    probes_raw = config.get("probes", [])

    probes: list[Probe] = []
    errors: list[str] = []

    for idx, rp in enumerate(probes_raw):
        match _parse_probe(rp):
            case Ok(v):
                probes.append(v)
            case Err(e):
                errors.extend(e)
            case _ as unreachable:
                assert_never(unreachable)

    return Ok((kafka_cfg, topic, probes)) if not errors else Err(errors)


def _read_config_file(file_name: str) -> Result[dict[str, Any], list[str]]:
    config_path: Path = Path.cwd() / file_name

    if not config_path.exists():
        return Err([f"Config file not found. Path: {config_path.resolve()}"])

    with config_path.open("r", encoding="utf-8") as f:
        try:
            yml = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return Err([f"Error parsing YAML file {config_path}: {e}"])

    if yml:
        return Ok(yml)
    else:
        return Err(["Failed to load yaml config"])


def get_config(file_name: str) -> Result[tuple[dict[str, str], str, list[Probe]], list[str]]:
    return bind_result(
        _parse_config,
        _read_config_file(file_name)
    )


if __name__ == "__main__":
    print(get_config("config.yml"))
