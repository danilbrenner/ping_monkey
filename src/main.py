from __future__ import annotations
import asyncio
from src import worker
from src.common.logging import Logger, init_logging, get_logger
from src.infra.config_loader import get_config
from src.domain import Probe
from src.infra.publisher import publish
from src.common.result import Err, Ok


async def main() -> int:
    init_logging()
    log: Logger = get_logger()

    log.info("Starting application")

    config_result = get_config("config.yml")

    match config_result:
        case Err(e):
            log.error("Failed to load configuration", errors=e)
            return 1
        case Ok(config):
            
            cfg: list[Probe] = config
            
            log.info("Configuration loaded successfully {probes}", probes=len(cfg))

            worker_dependencies = worker.WorkerDependencies(
                publish=lambda a, b: publish("", "", a, b)
            )

            stop = worker.init_stop_event()
            await worker.start_probe_jobs(worker_dependencies, cfg, stop)
            await stop.wait()

    log.info("Application exited")

    return 0

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
