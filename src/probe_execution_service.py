from src.common.logging import Logger
from src.common.result import Err
from src.domain import Probe
from src.infra.publisher_protocol import Publisher
from src.infra.requestor import Requestor


class ProbeExecutionService:
    def __init__(self, publisher: Publisher, requestor: Requestor, logger: Logger) -> None:
        self._logger = logger
        self._publisher = publisher
        self._requestor = requestor

    async def execute(self, probe: Probe) -> None:
        self._logger.info("Executing probe {probe}", probe=probe.name)
        response = await self._requestor.get_response(probe.url)
        if isinstance(response, Err):
            self._logger.error(
                "Error getting response for probe {probe}: {error}",
                probe=probe.name,
                error=response.error,
            )
            return

        self._logger.info("Fetched response for probe {probe}", probe=probe.name)

        cert_info = self._requestor.get_cert_info(probe.url) if probe.checkCert else None

        if isinstance(cert_info, Err):
            self._logger.error(
                "Error getting cert info for probe {probe}: {error}",
                probe=probe.name,
                error=cert_info.error,
            )
            return

        self._logger.info("Fetched cert info for probe {probe}", probe=probe.name)

        await self._publisher.publish(probe.name, response.value, cert_info.value if cert_info else None)

        self._logger.info("Published outcomes for probe {probe}", probe=probe.name)
