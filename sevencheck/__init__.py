"""sevencheck — deterministic checks for LLM outputs.

Seven families of verification for the failure mode that returns a number
instead of raising. Family 7 (verifier self-checks) is not a module: it is
the repo's own discipline — every check ships with a negative fixture that
proves it FAILs on known-bad input (run ``python -m sevencheck --selftest``),
and every rule's docstring carries the incident that created it.
"""
from .findings import (
    BLOCKER,
    WARN,
    Finding,
    VerificationError,
    assert_clean,
    blocker,
    blockers,
    warn,
)
from .grounding import ids_resolvable, quotes_regrep, verbatim_quote
from .rendering import build_complete, numbers_have_provenance, required_fields
from .absence import pinned_at_bound, required_absence, silence_is_not_proof
from .trajectory import coverage_bidirectional, mechanism_counter_moved, ordered_subsequence
from .reproduction import diff_runs, merge_gate, replay_fidelity
from .controls import degenerate_values, identical_arms, placebo_pass_rate, rule_has_teeth

__version__ = "0.1.0"

__all__ = [
    "BLOCKER", "WARN", "Finding", "VerificationError",
    "assert_clean", "blocker", "blockers", "warn",
    "verbatim_quote", "quotes_regrep", "ids_resolvable",
    "numbers_have_provenance", "required_fields", "build_complete",
    "required_absence", "pinned_at_bound", "silence_is_not_proof",
    "ordered_subsequence", "mechanism_counter_moved", "coverage_bidirectional",
    "diff_runs", "merge_gate", "replay_fidelity",
    "placebo_pass_rate", "rule_has_teeth", "degenerate_values", "identical_arms",
]
