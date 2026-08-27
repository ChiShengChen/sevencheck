"""Family 5 — Independent reproduction: a conclusion that reaches the final
artifact needs a second, independent source.

Origin incidents: a blind dual-run caught category-level evidence promoted
to leaf level (+330% edges) that a single run could not see about itself; a
hand-reconstructed replay indicted the wrong gate — numbers from an
unfaithful replay are worse than no numbers: they look like measurements.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from .findings import Finding, blocker, warn


def _leaves(obj: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(obj, Mapping):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            out.update(_leaves(v, f"{prefix}.{k}" if prefix else str(k)))
        return out
    if isinstance(obj, (list, tuple)):
        out = {}
        for i, v in enumerate(obj):
            out.update(_leaves(v, f"{prefix}[{i}]"))
        return out
    return {prefix: obj}


def diff_runs(run_a: Mapping, run_b: Mapping, *, path: str = "dual-run") -> list[Finding]:
    """Machine-diffable comparison of two independently produced run reports.
    Divergences are where the bugs hide; each one is surfaced for line-item
    human adjudication (the harness never auto-picks a winner)."""
    a, b = _leaves(run_a), _leaves(run_b)
    out: list[Finding] = []
    for key in sorted(set(a) | set(b)):
        if key not in a or key not in b:
            out.append(
                warn("reproduction.diff_runs", "key present in only one run", f"{path}.{key}",
                     in_a=key in a, in_b=key in b)
            )
        elif a[key] != b[key]:
            out.append(
                warn("reproduction.diff_runs", "runs diverge; adjudicate before merge",
                     f"{path}.{key}", a=repr(a[key])[:80], b=repr(b[key])[:80])
            )
    return out


def merge_gate(divergences: list[Finding], adjudicated: int) -> list[Finding]:
    """Fail-closed merge rule: every divergence must be adjudicated (count
    supplied by the human process) before the runs may be merged."""
    n = len(divergences)
    if adjudicated < n:
        return [
            blocker(
                "reproduction.merge_gate",
                f"{n - adjudicated} of {n} divergences unadjudicated; merge is forbidden",
            )
        ]
    return []


def replay_fidelity(
    replay_verdicts: Mapping[str, Any],
    production_verdicts: Mapping[str, Any],
    *,
    path: str = "replay",
) -> list[Finding]:
    """Fidelity comes first: the replay must reproduce production's own
    verdicts on the recorded cases (e.g. 31/31) or every downstream
    conclusion is void. Missing cases count as infidelity."""
    out: list[Finding] = []
    mismatches = []
    for cid, pv in production_verdicts.items():
        rv = replay_verdicts.get(cid, "<missing>")
        if rv != pv:
            mismatches.append((cid, pv, rv))
    if mismatches:
        out.append(
            blocker(
                "reproduction.replay_fidelity",
                f"replay failed to reproduce {len(mismatches)}/{len(production_verdicts)} "
                "production verdicts; all replay-derived conclusions are void",
                path,
                mismatches=mismatches[:10],
            )
        )
    return out
