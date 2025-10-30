import os
import logging
from typing import Protocol
import sys
import structlog
from typing import Any, cast, Callable, Iterable, Mapping, MutableMapping

class Logger(Protocol):
    def info(self, event: str, **kwargs: Any) -> None: ...

    def warning(self, event: str, **kwargs: Any) -> None: ...

    def error(self, event: str, **kwargs: Any) -> None: ...

    def debug(self, event: str, **kwargs: Any) -> None: ...


def init_logging() -> None:
    # Determine environment
    env = (os.getenv("ENV") or "development").lower()
    log_level_name = os.getenv("LOG_LEVEL") or "debug"
    level = getattr(logging, log_level_name.upper())

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    Processor = Callable[
        [Any, str, MutableMapping[str, Any]],
        Mapping[str, Any] | str | bytes | bytearray | tuple[Any, ...],
    ]

    processors = cast(
        Iterable[Processor],
        [
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer() if env == "production" else structlog.dev.ConsoleRenderer(),
        ],
    )

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=cast(Any, structlog.stdlib.BoundLogger),
        cache_logger_on_first_use=True,
    )

def get_logger() -> Logger:
    return structlog.get_logger()
