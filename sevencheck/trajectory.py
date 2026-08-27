"""Family 4 — Trajectory: assert the behavioural trace, not only the final
output. A skipped step is invisible in the artifact; a fabricated value
looks exactly like an answer.

Origin incidents: an interview replay had to assert *question order* because
invented values delete their own questions; five figures shipped with zero
references; fixes were credited by aggregate metrics whose run-to-run noise
was wider than any single change.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from .findings import Finding, blocker, warn


def ordered_subsequence(
    events: Sequence[str],
    expected: Sequence[str],
    *,
    path: str = "trace",
) -> list[Finding]:
    """``expected`` must occur within ``events`` in order (gaps allowed).
    Missing or out-of-order expected events are blockers: this is how a
    silently cancelled question becomes visible."""
    out: list[Finding] = []
    it = iter(events)
    for step in expected:
        for ev in it:
            if ev == step:
                break
        else:
            out.append(
                blocker(
                    "trajectory.ordered_subsequence",
                    f"expected event never occurred (or occurred out of order): '{step}'",
                    path,
                )
            )
            it = iter(())  # everything after the first miss is also unproven
    return out


def mechanism_counter_moved(
    before: Mapping[str, int],
    after: Mapping[str, int],
    counters: Iterable[str],
    *,
    min_delta: int = 1,
    path: str = "",
) -> list[Finding]:
    """A change is credited only by its own mechanism counters (triggered N
    times, rescued M items). If the counter did not move, the fix is not
    proven effective — whatever the aggregate metric did."""
    out: list[Finding] = []
    for c in counters:
        delta = after.get(c, 0) - before.get(c, 0)
        if delta < min_delta:
            out.append(
                blocker(
                    "trajectory.mechanism_counter_moved",
                    f"mechanism counter '{c}' moved by {delta} (< {min_delta}); "
                    "the change is unproven by its own mechanism",
                    path,
                    before=before.get(c, 0),
                    after=after.get(c, 0),
                )
            )
    return out


def coverage_bidirectional(
    referenced: Iterable[str],
    defined: Iterable[str],
    *,
    path: str = "",
) -> list[Finding]:
    """Coverage must be checked both ways: every reference resolves AND every
    defined artifact is referenced. 'All cited tables exist' once shipped
    alongside five figures nobody cited."""
    ref, dfn = set(referenced), set(defined)
    out: list[Finding] = []
    for r in sorted(ref - dfn):
        out.append(blocker("trajectory.coverage_bidirectional", f"referenced but not defined: '{r}'", path))
    for d in sorted(dfn - ref):
        out.append(warn("trajectory.coverage_bidirectional", f"defined but never referenced: '{d}'", path))
    return out
