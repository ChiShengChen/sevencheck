"""Test-binding rule: every check lands in the same commit as the test that
enforces it, and every check has a negative fixture proving it FAILs on
known-bad input. A rule without a test is a comment.
"""
import unittest

import sevencheck as sc
from sevencheck import __main__ as cli


class TestGrounding(unittest.TestCase):
    def test_verbatim_pass(self):
        self.assertEqual(sc.verbatim_quote("mostly anorthosite", "the moon is mostly anorthosite"), [])

    def test_verbatim_blocks_paraphrase(self):
        f = sc.verbatim_quote("made of anorthosite", "the moon is mostly anorthosite")
        self.assertTrue(sc.blockers(f))

    def test_verbatim_ws_mode_is_explicitly_weaker(self):
        q, s = "mostly  anorthosite", "mostly anorthosite"
        self.assertTrue(sc.blockers(sc.verbatim_quote(q, s)))          # strict bites
        self.assertEqual(sc.verbatim_quote(q, s, normalize_ws=True), [])

    def test_ids(self):
        allow = {"PMC9477501"}
        self.assertEqual(sc.ids_resolvable(["PMC9477501"], allow), [])
        self.assertTrue(sc.blockers(sc.ids_resolvable(["PMC000FAKE"], allow)))

    def test_regrep_missing_source(self):
        f = sc.quotes_regrep([{"quote": "x", "source_id": "S9"}], {"S1": "x y"})
        self.assertTrue(sc.blockers(f))


class TestRendering(unittest.TestCase):
    def test_numbers_pass_with_provenance(self):
        f = sc.numbers_have_provenance("corroboration reached 81.9% over 934 edges",
                                       allowed=["81.9%", 934])
        self.assertEqual(f, [])

    def test_numbers_block_unprovenanced(self):
        f = sc.numbers_have_provenance("accuracy reached 93.7%", allowed=["81.9%"])
        self.assertTrue(sc.blockers(f))
        self.assertEqual(f[0].evidence["token"], "93.7%")

    def test_numbers_ignore_list(self):
        f = sc.numbers_have_provenance("in 2026 we saw 81.9%", allowed=["81.9%"], ignore=["2026"])
        self.assertEqual(f, [])

    def test_required_fields(self):
        self.assertEqual(sc.required_fields({"n": 3}, {"n": int}), [])
        self.assertTrue(sc.blockers(sc.required_fields({"n": "3"}, {"n": int})))
        self.assertTrue(sc.blockers(sc.required_fields({}, {"n": int})))

    def test_build_complete(self):
        self.assertEqual(sc.build_complete(["a", "b"], ["a"]), [])
        self.assertTrue(sc.blockers(sc.build_complete(["a"], ["a", "method"])))


class TestAbsence(unittest.TestCase):
    def test_required_absence(self):
        self.assertEqual(sc.required_absence({"asked": 1}, ["not_asked"]), [])
        self.assertEqual(sc.required_absence({"not_asked": None}, ["not_asked"]), [])
        self.assertTrue(sc.blockers(sc.required_absence({"not_asked": 1200}, ["not_asked"])))

    def test_pinned_at_bound_blocks(self):
        f = sc.pinned_at_bound({"rho": [0.0, 0.0, 0.41, 0.0]})
        self.assertTrue(sc.blockers(f))

    def test_pinned_flag_and_exemption(self):
        ok = sc.pinned_at_bound({"rho": [0.0, 0.0, 0.41, 0.0]}, validity_flags={"rho": True})
        self.assertEqual(ok, [])
        ok2 = sc.pinned_at_bound({"rho_measurable": [0.0, 0.0, 0.0, 0.0]})
        self.assertEqual(ok2, [])

    def test_silence(self):
        self.assertEqual(sc.silence_is_not_proof(["a"], {"a": "lit_dark"}), [])
        self.assertTrue(sc.blockers(sc.silence_is_not_proof(["a", "b"], {"a": "supported"})))


class TestTrajectory(unittest.TestCase):
    def test_order_pass(self):
        self.assertEqual(sc.ordered_subsequence(["a", "x", "b", "c"], ["a", "b", "c"]), [])

    def test_order_blocks_skip(self):
        f = sc.ordered_subsequence(["ask_a", "ask_c"], ["ask_a", "ask_b", "ask_c"])
        self.assertTrue(sc.blockers(f))

    def test_counters(self):
        self.assertEqual(
            sc.mechanism_counter_moved({"r": 0}, {"r": 3}, ["r"]), [])
        self.assertTrue(sc.blockers(
            sc.mechanism_counter_moved({"r": 3}, {"r": 3}, ["r"])))

    def test_coverage_both_directions(self):
        f = sc.coverage_bidirectional(referenced={"fig1", "figX"}, defined={"fig1", "fig2"})
        self.assertTrue(sc.blockers(f))                       # figX referenced, undefined
        self.assertTrue(any(x.severity == sc.WARN for x in f))  # fig2 defined, unreferenced


class TestReproduction(unittest.TestCase):
    def test_diff_and_gate(self):
        d = sc.diff_runs({"edges": 3, "same": 1}, {"edges": 13, "same": 1})
        self.assertEqual(len(d), 1)
        self.assertTrue(sc.blockers(sc.merge_gate(d, adjudicated=0)))
        self.assertEqual(sc.merge_gate(d, adjudicated=1), [])

    def test_replay_fidelity(self):
        self.assertEqual(sc.replay_fidelity({"c1": "G"}, {"c1": "G"}), [])
        f = sc.replay_fidelity({"c1": "TOPICALITY"}, {"c1": "CLAIM_ANCHOR"})
        self.assertTrue(sc.blockers(f))


class TestControls(unittest.TestCase):
    def test_placebo(self):
        self.assertEqual(sc.placebo_pass_rate({"astro": False}, ["astro"]), [])
        self.assertTrue(sc.blockers(sc.placebo_pass_rate({"astro": True}, ["astro"])))

    def test_teeth(self):
        self.assertEqual(sc.rule_has_teeth(lambda x: False), [])
        self.assertTrue(sc.blockers(sc.rule_has_teeth(lambda x: True)))

    def test_degenerate(self):
        self.assertTrue(sc.blockers(sc.degenerate_values([1.0, 1.0, 1.0, 1.0])))
        self.assertTrue(sc.blockers(sc.degenerate_values([0.5, 0.5, 0.5, 0.7], prior=0.5)))
        self.assertEqual(sc.degenerate_values([0.4, 0.5, 0.6, 0.7]), [])

    def test_identical_arms(self):
        self.assertTrue(sc.blockers(sc.identical_arms({"a": b"x", "b": b"x"})))
        self.assertEqual(sc.identical_arms({"a": b"x", "b": b"y"}), [])


class TestFailClosed(unittest.TestCase):
    def test_assert_clean(self):
        with self.assertRaises(sc.VerificationError):
            sc.assert_clean([sc.blocker("t", "boom")])
        sc.assert_clean([sc.warn("t", "fine")])  # warns pass through


class TestMetaCoverage(unittest.TestCase):
    """Family 7 applied to the harness itself: the runtime selftest must
    cover every check family bidirectionally — no check without a
    known-bad fixture, no fixture for a check that does not exist."""

    def test_selftest_covers_all_checks(self):
        fixture_names = {name for name, _ in cli.KNOWN_BAD}
        check_names = set()
        for mod in ("grounding", "rendering", "absence", "trajectory",
                    "reproduction", "controls"):
            m = __import__(f"sevencheck.{mod}", fromlist=["*"])
            for attr in dir(m):
                fn = getattr(m, attr)
                if callable(fn) and getattr(fn, "__module__", "").endswith(mod) \
                        and not attr.startswith("_"):
                    check_names.add(f"{mod}.{attr}")
        # quotes_regrep and diff_runs are exercised through their composites
        exempt = {"grounding.quotes_regrep", "reproduction.diff_runs"}
        f = sc.coverage_bidirectional(referenced=fixture_names,
                                      defined=check_names - exempt)
        self.assertFalse(sc.blockers(f), msg="\n".join(map(str, sc.blockers(f))))
        self.assertFalse([x for x in f if x.severity == sc.WARN],
                         msg="check without a known-bad fixture:\n" +
                             "\n".join(map(str, f)))


if __name__ == "__main__":
    unittest.main()
