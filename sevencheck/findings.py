"""Findings: every check returns a list of these. An empty list means pass.

Checks never raise on bad *content* — a raise can be swallowed by a retry
loop; a Finding is data that survives into the report. Raising is reserved
for misuse of the API itself. Fail-closed behaviour is opt-in and explicit
via ``assert_clean``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

BLOCKER = "blocker"  # downstream MUST NOT read the result as a result
WARN = "warn"        # surfaced for adjudication; does not void the result


@dataclass(frozen=True)
class Finding:
    check: str
    severity: str
    message: str
    path: str = ""              # where in the artifact (json path, section, id)
    evidence: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:  # pragma: no cover - convenience
        loc = f" @ {self.path}" if self.path else ""
        return f"[{self.severity.upper()}] {self.check}{loc}: {self.message}"


def blocker(check: str, message: str, path: str = "", **evidence: Any) -> Finding:
    return Finding(check, BLOCKER, message, path, dict(evidence))


def warn(check: str, message: str, path: str = "", **evidence: Any) -> Finding:
    return Finding(check, WARN, message, path, dict(evidence))


class VerificationError(AssertionError):
    """Raised by assert_clean when blockers are present."""

    def __init__(self, findings: list[Finding]):
        self.findings = findings
        lines = "\n".join(str(f) for f in findings)
        super().__init__(f"{len(findings)} blocking finding(s):\n{lines}")


def blockers(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings if f.severity == BLOCKER]


def assert_clean(findings: list[Finding]) -> None:
    """Fail-closed gate: raise if any blocker is present. Warns pass through."""
    b = blockers(findings)
    if b:
        raise VerificationError(b)
