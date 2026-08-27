# Contributing

One law: **no rule without an incident.**

A PR adding or widening a check must contain, in the same commit:

1. **The incident** — in the check's docstring: what looked like success,
   what was actually happening, the consequence. Anonymize freely; the
   mechanism matters, the names do not.
2. **The check** — returns `list[Finding]`, never raises on bad content,
   blocker semantics = "downstream must not read this as a result".
3. **The enforcing test** — same commit (test-binding). A rule without a
   test is a comment.
4. **A negative fixture** — added to both the test suite and
   `sevencheck/__main__.py::KNOWN_BAD`. The meta-coverage test will fail
   your build if you forget; that is it working, not a nuisance.
5. **A false-positive budget** — one paragraph in the PR: what will this
   wrongly flag, how often, and why that is acceptable. A check that cries
   wolf gets disabled, and a disabled check is worse than none.
6. **"What it cannot catch"** — the blind spot, named in the docstring.

PRs that add rules from best-practice lists, widen a check "while in
there", or verify model output by calling another model are declined with a
pointer to this file.

Bug reports of the form "I adopted check X on a real pipeline and it broke
in way Y" are the most valuable contribution this repo can receive — see
the Honesty section of the README.
