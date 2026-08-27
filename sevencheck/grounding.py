"""Family 1 — Grounding: evidence must be a mechanically checkable relation,
never semantic similarity.

Origin incidents (2026, four independent projects): fabricated PMIDs and
synapse counts in a connectome pipeline; quotes that drifted from their
sources across redrafts. Doctrine: a failed quote is a dead claim — it is
dropped, never patched.
"""
from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping
from .findings import Finding, blocker

_WS = re.compile(r"\s+")


def verbatim_quote(
    quote: str,
    source: str,
    *,
    normalize_ws: bool = False,
    path: str = "",
) -> list[Finding]:
    """The quote must be a literal substring of the source.

    Default is byte-strict. ``normalize_ws=True`` collapses runs of
    whitespace on both sides before matching — a documented weakening.
    Never enable smarter normalization than this: every normalization step
    is a place for a fabricated quote to hide.
    """
    q, s = quote, source
    if normalize_ws:
        q, s = _WS.sub(" ", q).strip(), _WS.sub(" ", s)
    if q and q in s:
        return []
    return [
        blocker(
            "grounding.verbatim_quote",
            "quote is not a verbatim substring of its source; drop the claim, do not patch the quote",
            path,
            quote=quote[:200],
            normalized=normalize_ws,
        )
    ]


def quotes_regrep(
    claims: Iterable[Mapping[str, str]],
    sources: Mapping[str, str],
    *,
    quote_key: str = "quote",
    source_key: str = "source_id",
    normalize_ws: bool = False,
) -> list[Finding]:
    """Batch verbatim check: each claim carries a quote and a source id."""
    out: list[Finding] = []
    for i, claim in enumerate(claims):
        sid = claim.get(source_key, "")
        src = sources.get(sid)
        p = f"claims[{i}] -> {sid or '?'}"
        if src is None:
            out.append(
                blocker("grounding.quotes_regrep", "source id not found in corpus", p, source_id=sid)
            )
            continue
        out.extend(
            verbatim_quote(claim.get(quote_key, ""), src, normalize_ws=normalize_ws, path=p)
        )
    return out


def ids_resolvable(
    ids: Iterable[str],
    resolver: Callable[[str], bool] | Iterable[str],
    *,
    kind: str = "id",
    path: str = "",
) -> list[Finding]:
    """Every identifier must resolve against an authority the model cannot
    influence (a local index, an allowlist). An unresolvable id is treated
    as model-minted: the claim carrying it is dropped, never repaired.
    """
    if not callable(resolver):
        allow = set(resolver)
        resolver = allow.__contains__
    out: list[Finding] = []
    for x in ids:
        if not resolver(x):
            out.append(
                blocker(
                    "grounding.ids_resolvable",
                    f"unresolvable {kind} (model-minted?); drop the carrying claim",
                    path,
                    id=x,
                )
            )
    return out
