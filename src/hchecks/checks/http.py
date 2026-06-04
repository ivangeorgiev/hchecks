import time
from http import HTTPStatus
from traceback import format_exc

from ..models import CheckResult

try:
    from aiohttp import (
        BasicAuth,
        ClientResponseError,
        ClientSession,
        ClientTimeout,
        TCPConnector,
    )
except ImportError as exc:
    raise ImportError(f"Using {__name__} module requires the aiohttp library.") from exc


class HttpCheck:
    _url: str
    _username: str | None
    _password: str | None
    _verify_ssl: bool
    _timeout: float
    _name: str

    def __init__(
        self,
        url: str,
        username: str | None = None,
        password: str | None = None,
        verify_ssl: bool = True,
        timeout: float = 60.0,
        name: str | None = None,
    ) -> None:
        self._url = url
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._name = name or f"{self.__class__.__name__} to {self._url}"

    async def __call__(self) -> CheckResult:
        start = time.monotonic()
        try:
            async with (
                ClientSession(
                    connector=TCPConnector(
                        verify_ssl=self._verify_ssl, enable_cleanup_closed=True
                    ),
                    auth=BasicAuth(self._username, self._password or "")
                    if self._username
                    else None,
                    timeout=ClientTimeout(self._timeout),
                ) as session,
                session.get(self._url) as response,
            ):
                if response.status >= HTTPStatus.INTERNAL_SERVER_ERROR or (
                    self._username
                    and response.status
                    in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
                ):
                    response.raise_for_status()
                duration_ms = (time.monotonic() - start) * 1000
                return CheckResult(
                    name=self._name, passed=response.ok, duration_ms=duration_ms
                )
        except ClientResponseError as response_error:
            duration_ms = (time.monotonic() - start) * 1000
            return CheckResult(
                name=self._name,
                passed=False,
                details=str(response_error),
                duration_ms=duration_ms,
            )
        except Exception:
            duration_ms = (time.monotonic() - start) * 1000
            details: str = format_exc()
            return CheckResult(
                name=self._name, passed=False, details=details, duration_ms=duration_ms
            )
