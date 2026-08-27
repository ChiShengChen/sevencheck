"""Family 2 — Typing / render separation: any value with a unique correct
answer is rendered by code from data; the model supplies prose or a patch,
never the number itself.

Origin incidents: of 15 numbers copied by a model between artifacts, 14 were
stale; a build shipped with a required section silently missing. When the
answer can be computed, do not ask the model.
"""
from __future__ import annotations

import math
import re
from collections.abc import Iterable, Mapping
from .findings import Finding, blocker

_NUM = re.compile(r"(?<![\w.])[-+]?\d[\d,]*(?:\.\d+)?%?(?![\w])")


def numbers_have_provenance(
    text: str,
    allowed: Iterable[str | float | int],
    *,
    ignore: Iterable[str] = (),
    tolerance: float = 0.0,
    path: str = "",
) -> list[Finding]:
    """Every numeric token in the prose must correspond to a value from the
    evidence source. A number with no provenance is a blocker: broken
    pipelines do not raise — they return a number.

    ``allowed`` may mix exact strings ("81.9%") and numerics (0.819).
    ``ignore`` is for literals that are not measurements (years, ids).
    """
    allowed_str = {str(a) for a in allowed}
    allowed_num: list[float] = []
    for a in allowed:
        try:
            allowed_num.append(float(str(a).replace(",", "").rstrip("%")))
        except ValueError:
            pass
    ign = set(ignore)
    out: list[Finding] = []
    for m in _NUM.finditer(text):
        tok = m.group(0)
        if tok in ign or tok in allowed_str:
            continue
        try:
            v = float(tok.replace(",", "").rstrip("%"))
        except ValueError:
            v = math.nan
        if any(abs(v - a) <= tolerance for a in allowed_num):
            continue
        out.append(
            blocker(
                "rendering.numbers_have_provenance",
                "numeric token has no provenance in the evidence set",
                path or f"char {m.start()}",
                token=tok,
            )
        )
    return out


def required_fields(
    obj: Mapping,
    required: Mapping[str, type | tuple[type, ...]],
    *,
    forbid_extra: bool = False,
    path: str = "",
) -> list[Finding]:
    """Minimal, dependency-free structural contract. The validator — not the
    generator — is the single source of truth for shape."""
    out: list[Finding] = []
    for key, typ in required.items():
        if key not in obj:
            out.append(blocker("rendering.required_fields", f"missing required field '{key}'", path))
        elif not isinstance(obj[key], typ):
            out.append(
                blocker(
                    "rendering.required_fields",
                    f"field '{key}' has type {type(obj[key]).__name__}, expected {typ}",
                    path,
                )
            )
    if forbid_extra:
        for key in obj:
            if key not in required:
                out.append(blocker("rendering.required_fields", f"unexpected field '{key}'", path))
    return out


def build_complete(
    present_sections: Iterable[str],
    required_sections: Iterable[str],
    *,
    path: str = "build",
) -> list[Finding]:
    """Fail-loud assembly: a missing required section is a blocker, not a
    quietly shorter artifact."""
    present = set(present_sections)
    return [
        blocker("rendering.build_complete", f"required section missing: '{s}'", path, section=s)
        for s in required_sections
        if s not in present
    ]
