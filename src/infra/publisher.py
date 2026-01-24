import json
from dataclasses import dataclass
from typing import Protocol

from confluent_kafka import Producer

from src.common.logging import Logger
from src.domain import HttpResult, CertInfo


class Publisher(Protocol):
    async def publish(self, probe_name: str, result: HttpResult, cert_info: CertInfo | None) -> None: ...


@dataclass(frozen=True, slots=True)
class KafkaPublisherConfig:
    kafka_cfg: dict[str, str]
    topic: str


class KafkaPublisher:
    def __init__(self, logger: Logger, cfg: KafkaPublisherConfig) -> None:
        self._logger = logger
        self._producer = Producer(cfg.kafka_cfg)
        self._topic = cfg.topic

    async def publish(self, probe_name: str, result: HttpResult, cert_info: CertInfo | None) -> None:
        payload = json.dumps({
            "probeName": probe_name,
            "httpResult": {
                "statusCode": result.status_code,
                "elapsedMs": result.elapsed_ms,
            },
            "certInfo": {
                "subjectCN": cert_info.subject_cn,
                "issuerCN": cert_info.issuer_cn,
                "notBefore": cert_info.not_before.isoformat(),
                "notAfter": cert_info.not_after.isoformat(),
            } if cert_info else None
        })

        try:
            self._producer.produce(self._topic, payload.encode('utf-8'))
            self._producer.flush()
            self._logger.info("Published probe outcome to Kafka",
                              probe=probe_name,
                              topic=self._topic)
        except Exception as e:
            self._logger.error("Failed to publish probe outcome to Kafka", error=str(e))
