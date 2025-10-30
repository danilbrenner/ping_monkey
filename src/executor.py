import time

from src.domain import Probe, CheckOutcome, get_name


async def execute_probe(probe: Probe) -> list[CheckOutcome]:
    return [CheckOutcome(check_type=get_name(c), timestamp=int(time.time() * 1000), success=True) for c in probe.checks]
