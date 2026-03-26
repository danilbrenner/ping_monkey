from typing import Protocol

from src.domain import HttpResult, CertInfo


class Publisher(Protocol):
    async def publish(self, probe_name: str, result: HttpResult, cert_info: CertInfo | None) -> None: ...
