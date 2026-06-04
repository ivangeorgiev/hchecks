import asyncio
import inspect
import time
from typing import Awaitable, cast

from .models import Check, CheckResult, HealthCheckReport, Probe


async def arun_probe(probe: Probe) -> HealthCheckReport:
    """
    Run the health check probe and return the result.

    :param probe: The health check probe to run.
    :return: The result of the health check probe.
    """
    start = time.monotonic()
    results: list[CheckResult] = await asyncio.gather(
        *(arun_check(check) for check in probe.checks)
    )
    duration_ms = (time.monotonic() - start) * 1000
    return HealthCheckReport(
        name=probe.name,
        healthy=all(r.passed for r in results),
        checks=results,
        description=probe.description,
        duration_ms=duration_ms,
    )


def run_probe(probe: Probe) -> HealthCheckReport:
    """
    Run a probe from synchronous code.

    :param probe: The health check probe to run.
    :return: The result of the health check probe.
    """

    return asyncio.run(arun_probe(probe))


async def arun_check(check: Check) -> CheckResult:
    """
    Run a single health check and return the result.

    :param check: The health check to run.
    :return: The result of the health check.
    """

    start = time.monotonic()
    try:
        is_async_callable = inspect.iscoroutinefunction(
            check
        ) or inspect.iscoroutinefunction(getattr(check, "__call__", None))

        if is_async_callable:
            result = check()
            if inspect.isawaitable(result):
                return await cast(Awaitable[CheckResult], result)
            return cast(CheckResult, result)

        result = await asyncio.to_thread(check)
        if inspect.isawaitable(result):
            return await cast(Awaitable[CheckResult], result)
        return cast(CheckResult, result)
    except Exception as e:
        duration_ms = (time.monotonic() - start) * 1000
        name = getattr(check, "name", None) or getattr(check, "__name__", repr(check))
        return CheckResult(
            name=name,
            passed=False,
            details=f"{e.__class__.__name__}: {e}",
            duration_ms=duration_ms,
        )
