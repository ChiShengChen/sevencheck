"""Family 6 — Negative controls & known-answer injection: before measuring
the system, measure how easily you can be fooled.

Origin incidents: 11 divination agents kept as placebo controls exposed that
the backtest framework would flatter random rules; random four-decimal
numbers once passed a loose reconciliation 100% of the time; two baselines
were byte-identical for three review rounds; ten seeds at exactly 1.0000
turned out to be leakage.
"""
from __future__ import annotations

import random
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any
from .findings import Finding, blocker


def placebo_pass_rate(
    results: Mapping[str, bool],
    known_ineffective: Iterable[str],
    *,
    max_pass_rate: float = 0.0,
    path: str = "placebo",
) -> list[Finding]:
    """Keep a cohort of generators known to be ineffective. If the framework
    passes them, the framework flatters garbage — its positives on real
    candidates cannot be read."""
    names = list(known_ineffective)
    passed = [n for n in names if results.get(n, False)]
    rate = len(passed) / len(names) if names else 0.0
    if rate > max_pass_rate:
        return [
            blocker(
                "controls.placebo_pass_rate",
                f"{len(passed)}/{len(names)} known-ineffective generators passed "
                f"(rate {rate:.2f} > {max_pass_rate:.2f}); framework false-positive alarm",
                path,
                passed=passed[:10],
            )
        ]
    return []


def rule_has_teeth(
    validator: Callable[[Any], bool],
    junk: Iterable[Any] | None = None,
    *,
    n: int = 200,
    min_reject_rate: float = 0.99,
    seed: int = 7,
    path: str = "fuzz",
) -> list[Finding]:
    """Throw random junk at a validation rule and measure whether it bites.
    Random four-decimal floats once passed a loose reconciliation 100% of
    the time. Default junk: random floats and short random strings."""
    rng = random.Random(seed)
    if junk is None:
        junk = [rng.uniform(-1e6, 1e6) for _ in range(n // 2)] + [
            "".join(rng.choices("abcdef0123456789 .", k=12)) for _ in range(n - n // 2)
        ]
    junk = list(junk)
    accepted = [x for x in junk if validator(x)]
    reject_rate = 1 - len(accepted) / len(junk) if junk else 1.0
    if reject_rate < min_reject_rate:
        return [
            blocker(
                "controls.rule_has_teeth",
                f"validator rejected only {reject_rate:.2%} of random junk "
                f"(< {min_reject_rate:.0%}); the rule has no teeth",
                path,
                sample_accepted=[repr(a)[:40] for a in accepted[:5]],
            )
        ]
    return []


def degenerate_values(
    values: Sequence[float],
    *,
    prior: float | None = None,
    min_n: int = 4,
    path: str = "",
) -> list[Finding]:
    """Know what a broken result looks like, and check for it: zero variance
    across seeds (all 1.0000 was leakage) or accuracy equal to the class
    prior (the arm measures the prior, not the pipeline)."""
    out: list[Finding] = []
    if len(values) >= min_n and len(set(values)) == 1:
        out.append(
            blocker("controls.degenerate_values",
                    f"zero variance across {len(values)} runs (all {values[0]}); "
                    "suspect leakage or a constant path", path)
        )
    if prior is not None:
        hits = sum(1 for v in values if v == prior)
        if len(values) >= min_n and hits >= len(values) - 1:
            out.append(
                blocker("controls.degenerate_values",
                        f"{hits}/{len(values)} runs equal the prior exactly; "
                        "this arm measures the prior, not the pipeline", path)
            )
    return out


def identical_arms(arms: Mapping[str, str | bytes], *, path: str = "") -> list[Finding]:
    """Two experimental arms that are byte-identical are one arm wearing two
    names — it once survived three review rounds."""
    seen: dict[str | bytes, str] = {}
    out: list[Finding] = []
    for name, payload in arms.items():
        if payload in seen:
            out.append(
                blocker("controls.identical_arms",
                        f"arms '{seen[payload]}' and '{name}' are byte-identical", path)
            )
        else:
            seen[payload] = name
    return out
