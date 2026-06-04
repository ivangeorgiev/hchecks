import asyncio
import time

from ..models import CheckResult


class HostConnectivityCheck:
    def __init__(
        self, hostname: str, port: int, timeout: int = 5, name: str | None = None
    ):
        self.hostname = hostname
        self.port = port
        self.timeout = timeout
        self.name = name or f"{self.__class__.__name__} to {self.hostname}:{self.port}"

    async def __call__(self) -> CheckResult:
        name = self.name
        start = time.monotonic()
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(self.hostname, self.port),
                timeout=self.timeout,
            )
            writer.close()
            await writer.wait_closed()

            duration_ms = (time.monotonic() - start) * 1000
            return CheckResult(name=name, passed=True, duration_ms=duration_ms)
        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000
            return CheckResult(
                name=name, passed=False, details=str(e), duration_ms=duration_ms
            )
