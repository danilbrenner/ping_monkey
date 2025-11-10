import datetime
import time
from dataclasses import dataclass
from typing import assert_never


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


@dataclass(frozen=True, slots=True)
class CertInfo:
    subject_cn: str | None
    issuer_cn: str | None
    not_before: datetime.datetime
    not_after: datetime.datetime


@dataclass(frozen=True, slots=True)
class HttpResult:
    status_code: int
    body: bytes
    elapsed_ms: int


def calc_outcome(result: HttpResult, cert_info: CertInfo | None, check: ProbeCheck) -> CheckOutcome:
    match check:
        case StatusCodeCheck() as c if result.status_code == c.expected_status_code:
            return CheckOutcome(
                check_type="StatusCodeCheck",
                timestamp=int(time.time()),  # request.elapsed.total_seconds(),
                success=True,
                details=f"Status code {result.status_code} as expected"
            )
        case StatusCodeCheck():
            return CheckOutcome(
                check_type="StatusCodeCheck",
                timestamp=int(time.time()),
                success=False,
                details=f"Expected status code {check.expected_status_code}, got {result.status_code}"
            )
        case SslValidityCheck() as c if cert_info is not None and (
                cert_info.not_after - datetime.datetime.now(datetime.timezone.utc)).days >= c.min_days_valid:
            return CheckOutcome(
                check_type="SslValidityCheck",
                timestamp=int(time.time()),
                success=True,
                details=f"Certificate validity({cert_info.not_after}) meets minimum of {c.min_days_valid} days"
            )
        case SslValidityCheck() as c if cert_info is not None:
            return CheckOutcome(
                check_type="SslValidityCheck",
                timestamp=int(time.time()),
                success=False,
                details=f"Certificate validity({cert_info.not_after}) below minimum of {c.min_days_valid} days"
            )
        case SslValidityCheck():
            return CheckOutcome(
                check_type="SslValidityCheck",
                timestamp=int(time.time()),
                success=False,
                details="No certificate info available"
            )
        case ResponseTimeCheck() as c if result.elapsed_ms / 1000 <= c.threshold_ms:
            return CheckOutcome(
                check_type="ResponseTimeCheck",
                timestamp=int(time.time()),
                success=True,
                details=f"Response time within threshold"
            )
        case ResponseTimeCheck():
            return CheckOutcome(
                check_type="ResponseTimeCheck",
                timestamp=int(time.time()),
                success=False,
                details=f"Response time exceeded threshold"
            )
        case HashCheck():
            return CheckOutcome(
                check_type="HashCheck",
                timestamp=int(time.time()),
                success=True,
                details="HashCheck not implemented"
            )
        case _ as unreachable:
            assert_never(unreachable)
