"""Family 3 — Absence: "does not exist" must be a checkable state, never a
rendered value. The most under-served family in conventional testing, and
the one all four origin projects hit independently.

Origin incidents: an extractor filled an unanswered field with a "typical
value", which silently cancelled the question the host would otherwise have
asked; a clipped rho probe reported "absent" and "unmeasurable" with the
same 0.000; a scanner reported clean because the content was stripped
upstream (silence is not proof).
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from .findings import Finding, blocker


def required_absence(
    obj: Mapping,
    must_be_absent: Iterable[str],
    *,
    treat_none_as_absent: bool = True,
    path: str = "",
) -> list[Finding]:
    """Fields not yet answered must stay absent. A guessed value does not
    just fill a field wrong — it deletes the question downstream."""
    out: list[Finding] = []
    for key in must_be_absent:
        present = key in obj and not (treat_none_as_absent and obj[key] is None)
        if present:
            out.append(
                blocker(
                    "absence.required_absence",
                    f"field '{key}' was answered nowhere but carries a value; "
                    "an invented value silently cancels the question",
                    path,
                    value=repr(obj[key])[:100],
                )
            )
    return out


def pinned_at_bound(
    values_by_metric: Mapping[str, Sequence[float]],
    *,
    bounds: tuple[float, float] = (0.0, 1.0),
    exempt_suffixes: tuple[str, ...] = ("_measurable", "_headroom"),
    min_n: int = 4,
    min_frac: float = 0.25,
    validity_flags: Mapping[str, bool] | None = None,
) -> list[Finding]:
    """A clipped statistic reports "absent" and "unmeasurable" with the same
    number. Any derived metric sitting exactly on a bound for a run must be
    accompanied by a validity flag, and until it is, the value cannot be
    read. Flags themselves are exempt — they are meant to sit on a bound.
    """
    lo, hi = bounds
    flags = validity_flags or {}
    out: list[Finding] = []
    for name, values in values_by_metric.items():
        if name.endswith(exempt_suffixes):
            continue
        pinned = [v for v in values if v in (lo, hi)]
        if len(values) >= min_n and len(pinned) >= max(2, int(len(values) * min_frac)):
            if not flags.get(name, False):
                out.append(
                    blocker(
                        "absence.pinned_at_bound",
                        f"{len(pinned)}/{len(values)} values sit exactly on a bound "
                        "with no validity flag; the value cannot be read",
                        name,
                        pinned=pinned[:8],
                    )
                )
    return out


def silence_is_not_proof(
    expected_ids: Iterable[str],
    reported: Mapping[str, str],
    *,
    path: str = "",
) -> list[Finding]:
    """Every expected item must appear with an explicit status — including an
    explicit negative ("none_found", "lit_dark"). An item that is simply
    missing from the report is indistinguishable from one that was stripped
    before the scanner ever saw it."""
    out: list[Finding] = []
    for eid in expected_ids:
        if eid not in reported:
            out.append(
                blocker(
                    "absence.silence_is_not_proof",
                    "expected item absent from report with no explicit status; "
                    "silence is not proof it was checked",
                    path,
                    id=eid,
                )
            )
    return out
