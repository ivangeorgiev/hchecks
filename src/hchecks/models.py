from dataclasses import dataclass, field
from typing import Awaitable, Callable, TypedDict

class CheckResultDump(TypedDict):
    name: str
    passed: bool
    details: str | None
    duration_ms: float | None

class HealthCheckReportDump(TypedDict):
    name: str
    description: str | None
    healthy: bool
    duration_ms: float | None
    checks: list[CheckResultDump]



@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str | None = None
    duration_ms: float | None = None

    def dump(self) -> CheckResultDump:
        return {
            "name": self.name,
            "passed": self.passed,
            "details": self.details,
            "duration_ms": self.duration_ms,
        }


type Check = Callable[[], CheckResult | Awaitable[CheckResult]]

@dataclass
class HealthCheckReport:
    name: str
    healthy: bool
    checks: list[CheckResult] = field(default_factory=list)
    description: str | None = None
    duration_ms: float | None = None

    def dump(self) -> HealthCheckReportDump:
        return {
            "name": self.name,
            "description": self.description,
            "healthy": self.healthy,
            "duration_ms": self.duration_ms,
            "checks": [c.dump() for c in self.checks],
        }


@dataclass
class Probe:
    name: str
    checks: list[Check] = field(default_factory=list)
    description: str | None = None
