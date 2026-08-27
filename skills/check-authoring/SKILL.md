---
name: check-authoring
description: >
  Use when turning an incident (a "plausible but wrong" LLM output that
  slipped through) into a new deterministic check. Enforces the format:
  docstring-is-the-precedent, same-commit test-binding, negative fixture,
  false-positive budget. Use BEFORE writing any new verification rule.
---

# Authoring a new check

## Preconditions

- A real incident exists. No rule without an incident — if it has not
  happened, do not write it.
- The failure is detectable from the artifact alone (the criterion). If
  not, this is a human gate, not a check.

## The format (all four, same commit)

1. **Docstring is the precedent.** First line = the law in one sentence.
   Body = the incident: what looked like success, what was actually
   happening, the consequence. The docstring and the mechanization live in
   one place — future readers should not need the tracker.
2. **The check.** Returns `list[Finding]`; empty = pass. Never raises on
   bad content. Blocker means "downstream must not read this as a result".
3. **Test-binding.** The same commit carries the unit test that enforces
   the rule. A rule without a test is a comment.
4. **Negative fixture.** The test suite AND `__main__.KNOWN_BAD` both get
   a known-bad input this check must block. The meta-coverage test will
   fail your commit if you forget — that is it working.

## False-positive budget

Before merging, write down: what will this check wrongly flag, and how
often? A check that cries wolf gets disabled, and a disabled check is worse
than none — it looks like coverage. If you cannot bound the false-positive
rate, narrow the check until you can.

## Also write "what it cannot catch"

Every check's docstring (or the family header) names its blind spot. The
second half is more important than the first: readers must know where the
guarantee ends.

## Anti-patterns

- If you find yourself writing a rule from a best-practices list — stop; find the incident or drop the rule.
- If you find yourself widening a check "while you're in there" — stop; one incident, one check, one commit.
- If the negative fixture feels hard to construct — good; that difficulty is the check's spec. Do not ship without it.
