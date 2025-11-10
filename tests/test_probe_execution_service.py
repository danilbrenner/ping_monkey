import asyncio
from typing import cast
from unittest.mock import AsyncMock, Mock

from src.common.logging import Logger
from src.infra.publisher import Publisher
from src.infra.requestor import Requestor
from src.probe_execution_service import ProbeExecutionService
from src.domain import (
    Probe,
    StatusCodeCheck,
    SslValidityCheck,
    HttpResult,
    CertInfo,
)
from src.common.result import Ok, Err


def _make_http_result(status_code: int = 200, body: bytes = b"", elapsed_ms: int = 100) -> HttpResult:
    return HttpResult(status_code=status_code, body=body, elapsed_ms=elapsed_ms)


def _make_cert_info() -> CertInfo:
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    return CertInfo(subject_cn="example.com", issuer_cn="CA", not_before=now - timedelta(days=10),
                    not_after=now + timedelta(days=30))


def test_execute_happy_path_with_ssl_check():
    # Arrange
    probe = Probe(name="p1", url="https://example.com", schedule="@daily",
                  checks=[StatusCodeCheck(expected_status_code=200), SslValidityCheck(min_days_valid=5)])

    publisher = cast(Publisher, AsyncMock())
    requestor = cast(Requestor, Mock())
    logger = cast(Logger, Mock())

    requestor.get_response = AsyncMock(return_value=Ok(_make_http_result(200)))
    requestor.get_cert_info = Mock(return_value=Ok(_make_cert_info()))

    svc = ProbeExecutionService(publisher, requestor, logger)

    # Act
    asyncio.run(svc.execute(probe))

    # Assert
    requestor.get_response.assert_awaited_once_with(probe.url)
    requestor.get_cert_info.assert_called_once_with(probe.url)

    assert cast(AsyncMock, publisher.publish).await_count == len(probe.checks)

    first_call = cast(AsyncMock, publisher.publish).await_args_list[0]
    assert first_call.args[0] == probe.name
    assert hasattr(first_call.args[1], "check_type")


def test_execute_no_ssl_check():
    # Arrange: probe with only a status code check
    probe = Probe(name="p2", url="https://no-ssl.example", schedule="@hourly",
                  checks=[StatusCodeCheck(expected_status_code=200)])

    publisher = cast(Publisher, AsyncMock())
    requestor = cast(Requestor, Mock())
    logger = cast(Logger, Mock())

    requestor.get_response = AsyncMock(return_value=Ok(_make_http_result(200)))
    requestor.get_cert_info = Mock()

    svc = ProbeExecutionService(publisher, requestor, logger)

    # Act
    asyncio.run(svc.execute(probe))

    # Assert
    requestor.get_response.assert_awaited_once_with(probe.url)
    requestor.get_cert_info.assert_not_called()
    assert cast(AsyncMock, publisher.publish).await_count == len(probe.checks)


def test_execute_response_err_stops_processing():
    # Arrange
    probe = Probe(name="p3", url="https://down.example", schedule="@daily",
                  checks=[StatusCodeCheck(expected_status_code=200)])

    publisher = cast(Publisher, AsyncMock())
    requestor = cast(Requestor, Mock())
    logger = cast(Logger, Mock())

    requestor.get_response = AsyncMock(return_value=Err("network error"))
    requestor.get_cert_info = Mock()

    svc = ProbeExecutionService(publisher, requestor, logger)

    # Act
    asyncio.run(svc.execute(probe))

    # Assert: cert_info should not be called and publish should not be awaited
    requestor.get_response.assert_awaited_once_with(probe.url)
    requestor.get_cert_info.assert_not_called()
    assert cast(AsyncMock, publisher.publish).await_count == 0


def test_execute_cert_err_stops_processing():
    # Arrange: probe with SSL check where cert retrieval fails
    probe = Probe(name="p4", url="https://badcert.example", schedule="@daily",
                  checks=[SslValidityCheck(min_days_valid=10)])

    publisher = cast(Publisher, AsyncMock())
    requestor = cast(Requestor, Mock())
    logger = cast(Logger, Mock())

    requestor.get_response = AsyncMock(return_value=Ok(_make_http_result(200)))
    requestor.get_cert_info = Mock(return_value=Err("cert error"))

    svc = ProbeExecutionService(publisher, requestor, logger)

    # Act
    asyncio.run(svc.execute(probe))

    # Assert
    requestor.get_response.assert_awaited_once_with(probe.url)
    requestor.get_cert_info.assert_called_once_with(probe.url)
    assert cast(AsyncMock, publisher.publish).await_count == 0
