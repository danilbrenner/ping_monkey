import json
from dataclasses import dataclass
from typing import Protocol

from confluent_kafka import Producer

from src.common.logging import Logger
from src.domain import CheckOutcome


class Publisher(Protocol):
    async def publish(self, probe_name: str, outcome: CheckOutcome) -> None: ...


@dataclass(frozen=True, slots=True)
class KafkaPublisherConfig:
    kafka_cfg: dict[str, str]
    topic: str


class KafkaPublisher:
    def __init__(self, logger: Logger, cfg: KafkaPublisherConfig) -> None:
        self._logger = logger
        self._producer = Producer(cfg.kafka_cfg)
        self._topic = cfg.topic

    async def publish(self, probe_name: str, outcome: CheckOutcome) -> None:
        payload = json.dumps({
            "probe_name": probe_name,
            "check_type": outcome.check_type,
            "timestamp": outcome.timestamp,
            "success": outcome.success,
            "details": outcome.details,
        })

        try:
            self._producer.produce(self._topic, payload.encode('utf-8'))
            self._producer.flush()
            self._logger.info("Published probe outcome to Kafka",
                              probe=probe_name,
                              topic=self._topic,
                              check_type=outcome.check_type)
        except Exception as e:
            self._logger.error("Failed to publish probe outcome to Kafka", error=str(e))
