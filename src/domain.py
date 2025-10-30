from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class StatusCodeCheck:
    expected_status_code: int

@dataclass(frozen=True, slots=True)
class ResponseTimeCheck:
    threshold_ms: int

@dataclass(frozen=True, slots=True)
class HashCheck:
    expected_hash: str

@dataclass(frozen=True, slots=True)
class SslValidityCheck:
    min_days_valid: int

ProbeCheck = HashCheck | SslValidityCheck | ResponseTimeCheck | StatusCodeCheck

@dataclass(frozen=True, slots=True)
class Probe:
    name: str
    url: str
    schedule: str
    checks: list[ProbeCheck]

@dataclass(frozen=True, slots=True)
class CheckOutcome:
    check_type: str
    timestamp: int
    success: bool
    details: str | None = None

@dataclass(frozen=True, slots=True)
class Setup:
    probes: list[Probe]

def get_name(check: ProbeCheck) -> str:
    if isinstance(check, StatusCodeCheck):
        return "StatusCodeCheck"
    elif isinstance(check, ResponseTimeCheck):
        return "ResponseTimeCheck"
    elif isinstance(check, HashCheck):
        return "HashCheck"
    elif isinstance(check, SslValidityCheck):
        return "SslValidityCheck"
    else:
        return "UnknownCheck"
