from __future__ import annotations
import asyncio
import signal
from datetime import datetime

from croniter import croniter

from src.common.logging import Logger, init_logging, get_logger
from src.infra.config_loader import get_config
from src.domain import Probe
from src.common.result import Err, Ok
from src.infra.publisher import KafkaPublisher, KafkaPublisherConfig
from src.infra.requestor import HttpRequestor
from src.probe_execution_service import ProbeExecutionService


def init_stop_event() -> asyncio.Event:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)
    return stop


def _get_timeout_seconds(schedule: str) -> float:
    now = datetime.now()
    next_run = croniter(schedule, now).get_next(datetime)
    return (next_run - now).total_seconds()


async def _job(probe: Probe, service: ProbeExecutionService, stop: asyncio.Event) -> None:
    first_run = True
    log: Logger = get_logger()
    while not stop.is_set():
        try:
            if not first_run:
                log.info("Executing periodic job {probe}", probe=probe.name)
                await service.execute(probe)
            else:
                first_run = False

            async with asyncio.timeout(_get_timeout_seconds(probe.schedule)):
                await stop.wait()
        except TimeoutError:
            pass


def create_probe_execution_service(kafka_cfg: dict[str, str], topic: str) -> ProbeExecutionService:
    return ProbeExecutionService(
        KafkaPublisher(
            get_logger(),
            KafkaPublisherConfig(
                kafka_cfg,
                topic
            )),
        HttpRequestor(),
        get_logger()
    )


async def start_probe_jobs(kafka_cfg, topic, probes: list[Probe],
                           stop: asyncio.Event) -> None:
    async with asyncio.TaskGroup() as tg:
        _ = [tg.create_task(_job(probe, create_probe_execution_service(kafka_cfg, topic), stop)) for probe in probes]


async def main() -> int:
    init_logging()
    log: Logger = get_logger()

    log.info("Starting application")

    config_result = get_config("config.yml")

    match config_result:
        case Err(e):
            log.error("Failed to load configuration", errors=e)
            return 1
        case Ok((kafka_cfg, topic, probes)):

            log.info("Configuration loaded successfully {probes}", probes=len(probes))

            stop = init_stop_event()
            await start_probe_jobs(kafka_cfg, topic, probes, stop)
            await stop.wait()

    log.info("Application exited")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
