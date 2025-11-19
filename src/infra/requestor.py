from __future__ import annotations

import asyncio
import socket
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final, Mapping, Sequence, Tuple, Optional, cast, assert_never, Protocol

import httpx
from urllib.parse import urlparse

from src.common.result import Result, Err, Ok
from src.domain import CertInfo, HttpResult

CERT_TIME_FMT: Final[str] = "%b %d %H:%M:%S %Y %Z"  # e.g. 'Nov  9 12:34:56 2025 GMT'


class Requestor(Protocol):
    async def get_response(self, url: str) -> Result[HttpResult, str]: ...

    def get_cert_info(self, url: str, timeout: float = 10.0) -> Result[CertInfo, str]: ...


class HttpRequestor:
    def __init__(self):
        pass

    def get_cert_info(self, url: str, timeout: float = 10.0) -> Result[CertInfo, str]:
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname or url
            port = parsed.port or (443 if parsed.scheme == "https" else 80)

            ctx = ssl.create_default_context()
            ctx.check_hostname = True
            ctx.verify_mode = ssl.CERT_REQUIRED

            with socket.create_connection((hostname, port), timeout=timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_raw = ssock.getpeercert()

            if not cert_raw:
                return Err("Peer did not provide a certificate")

            cert: Mapping[str, Any] = cast(Mapping[str, Any], cert_raw)

            subject = _name_to_dict(cert.get("subject", ()))
            issuer = _name_to_dict(cert.get("issuer", ()))

            not_before_raw = cert.get("notBefore")
            not_after_raw = cert.get("notAfter")

            if not isinstance(not_before_raw, str) or not isinstance(not_after_raw, str):
                return Err("Certificate missing notBefore/notAfter")

            return Ok(CertInfo(
                subject_cn=subject.get("commonName"),
                issuer_cn=issuer.get("commonName"),
                not_before=_parse_cert_datetime(not_before_raw),
                not_after=_parse_cert_datetime(not_after_raw),
            ))
        except (socket.error, ssl.SSLError) as e:
            return Err(f"Network/SSL error: {e}")

    async def get_response(self, url: str) -> Result[HttpResult, str]:
        try:
            async with httpx.AsyncClient(http2=False, verify=True) as client:
                response = await client.get(url)
                return Ok(_response_to_http_result(response))
        except httpx.HTTPError as e:
            return Err(f"HTTP error: {e}")


def _parse_cert_datetime(value: str) -> datetime:
    dt = datetime.strptime(value, CERT_TIME_FMT)
    return dt.replace(tzinfo=timezone.utc)


def _name_to_dict(
        name: Sequence[Sequence[Tuple[str, str]]] | object,
) -> dict[str, str]:
    try:
        seq = cast(Sequence[Sequence[Tuple[str, str]]], name)
        return {k: v for rdn in seq for (k, v) in rdn}
    except Exception:
        return {}


def _response_to_http_result(
        response: httpx.Response,
) -> HttpResult:
    return HttpResult(
        status_code=response.status_code,
        body=response.content,
        elapsed_ms=int(response.elapsed.microseconds / 1000),
    )
