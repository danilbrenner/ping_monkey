import json
from azure.storage.queue.aio import QueueClient
from src.domain import CheckOutcome
from src.common.logging import get_logger


async def publish(conn_str: str, queue_name: str, probe_name: str, outcome: CheckOutcome) -> None:
    log = get_logger()

    if not queue_name:
        log.warning("Azure queue name not configured; skipping publish")
        return

    if not conn_str:
        log.warning("Azure storage connection string not provided; skipping publish")
        return

    payload = json.dumps(
        {
            "probe_name": probe_name,
            "check_type": outcome.check_type,
            "timestamp": outcome.timestamp,
            "success": outcome.success,
            "details": outcome.details,
        }
    )

    try:
        client = QueueClient.from_connection_string(conn_str, queue_name)

        async with client:
            await client.send_message(payload)
            log.info("Published check outcome", queue=queue_name)
    except Exception as e:
        log.error("Failed to publish check outcome", error=e)
