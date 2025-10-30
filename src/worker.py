import asyncio
import signal

from datetime import datetime
from typing import Callable, Awaitable

from croniter import croniter

from src.common.logging import Logger, get_logger
from src.domain import Probe, CheckOutcome
from src.executor import execute_probe

class WorkerDependencies:
    def __init__(self, publish: Callable[[str, CheckOutcome], Awaitable[None]]) -> None:
        self.publish = publish

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

async def _job(dependencies: WorkerDependencies, probe: Probe, stop: asyncio.Event) -> None:
    first_run = True
    log: Logger = get_logger()
    while not stop.is_set():
        try:
            if not first_run:
                log.info("Executing periodic job {probe}", probe=probe.name)
                result = await execute_probe(probe)
                for outcome in result:
                    log.info(
                        "Probe check outcome: {probe} - {outcome}",
                        probe=probe.name,
                        outcome=outcome
                    )
                    await dependencies.publish(probe.name, outcome)
            else:
                first_run = False

            async with asyncio.timeout(_get_timeout_seconds(probe.schedule)):
                await stop.wait()
        except TimeoutError:
            pass

async def start_probe_jobs(dependencies: WorkerDependencies, probes: list[Probe], stop: asyncio.Event) -> None:
    async with asyncio.TaskGroup() as tg:
        _ = [tg.create_task(_job(dependencies, probe, stop)) for probe in probes]
