import datetime
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Probe:
    name: str
    url: str
    schedule: str
    checkCert: bool = False


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
    elapsed_ms: int
