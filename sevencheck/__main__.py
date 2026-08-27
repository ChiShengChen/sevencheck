"""Family 7 in action: the harness distrusts itself.

``python -m sevencheck --selftest`` feeds every check a curated known-bad
input and exits non-zero unless every check raises a blocker. A verifier
that cannot fail known-bad data has no teeth; this is the runtime proof,
independent of the unit-test suite.
"""
from __future__ import annotations

import sys
import sevencheck as sc

KNOWN_BAD = [
    ("grounding.verbatim_quote",
     lambda: sc.verbatim_quote("the moon is basalt", "the moon is mostly anorthosite")),
    ("grounding.ids_resolvable",
     lambda: sc.ids_resolvable(["PMC000FAKE"], {"PMC9477501"})),
    ("rendering.numbers_have_provenance",
     lambda: sc.numbers_have_provenance("accuracy reached 93.7%", allowed=["81.9%"])),
    ("rendering.required_fields",
     lambda: sc.required_fields({"n": "3"}, {"n": int})),
    ("rendering.build_complete",
     lambda: sc.build_complete(["abstract", "intro"], ["abstract", "intro", "method"])),
    ("absence.required_absence",
     lambda: sc.required_absence({"pallet_mm": 1200}, must_be_absent=["pallet_mm"])),
    ("absence.pinned_at_bound",
     lambda: sc.pinned_at_bound({"rho": [0.0, 0.0, 0.41, 0.0]})),
    ("absence.silence_is_not_proof",
     lambda: sc.silence_is_not_proof(["n1", "n2"], {"n1": "supported"})),
    ("trajectory.ordered_subsequence",
     lambda: sc.ordered_subsequence(["ask_a", "ask_c"], ["ask_a", "ask_b", "ask_c"])),
    ("trajectory.mechanism_counter_moved",
     lambda: sc.mechanism_counter_moved({"rescued": 3}, {"rescued": 3}, ["rescued"])),
    ("trajectory.coverage_bidirectional",
     lambda: sc.coverage_bidirectional(referenced={"figX"}, defined={"fig1"})),
    ("reproduction.merge_gate",
     lambda: sc.merge_gate(sc.diff_runs({"edges": 3}, {"edges": 13}), adjudicated=0)),
    ("reproduction.replay_fidelity",
     lambda: sc.replay_fidelity({"c1": "TOPICALITY"}, {"c1": "CLAIM_ANCHOR"})),
    ("controls.placebo_pass_rate",
     lambda: sc.placebo_pass_rate({"astro": True}, ["astro"])),
    ("controls.rule_has_teeth",
     lambda: sc.rule_has_teeth(lambda x: True)),
    ("controls.degenerate_values",
     lambda: sc.degenerate_values([1.0, 1.0, 1.0, 1.0])),
    ("controls.identical_arms",
     lambda: sc.identical_arms({"baseline": b"x", "ours": b"x"})),
]


def selftest() -> int:
    failures = []
    for name, fn in KNOWN_BAD:
        findings = fn()
        if not sc.blockers(findings):
            failures.append(name)
            print(f"NO TEETH: {name} passed known-bad input")
        else:
            print(f"ok  {name}: blocked known-bad input")
    if failures:
        print(f"\nSELFTEST FAILED: {len(failures)} check(s) have no teeth")
        return 1
    print(f"\nselftest passed: {len(KNOWN_BAD)}/{len(KNOWN_BAD)} checks bite")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    print(__doc__)
    print("usage: python -m sevencheck --selftest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
