# sevencheck

**Deterministic checks for LLM outputs — seven families of verification for
the failure mode that returns a number instead of raising.**

Conventional tests defend against crashes. LLM systems fail differently:
they hand you something *plausible but wrong* — a paraphrased "quote", a
minted citation, a typical value filling a question nobody answered, a
clipped statistic reporting "absent" and "unmeasurable" as the same 0.000.
`sevencheck` is a zero-dependency Python toolkit of checks for exactly that
failure mode, distilled from four production-grade agent projects (a
connectome×literature research pipeline, an autonomous research-execution
engine, a financial-research workbench, and an industrial robot-workcell
design platform, 2026).

## The criterion

> An LLM output is automatically verifiable **iff** you can write a
> function that declares FAIL without seeing the generation process — only
> the output plus pre-existing data.

If you can write that function, it belongs here. If you cannot, it belongs
in a human gate — never in a second model call pretending to be one.

Design question for every load-bearing number: *"If the thing I believe is
happening were not happening, what would this output look like?"* Then
check whether it already looks like that.

## The seven families

| # | Family | Rule | Checks |
|---|--------|------|--------|
| 1 | **Grounding** | evidence is a mechanically checkable relation, never semantic similarity | `verbatim_quote`, `quotes_regrep`, `ids_resolvable` |
| 2 | **Render separation** | values with a unique correct answer are rendered by code, never by the model | `numbers_have_provenance`, `required_fields`, `build_complete` |
| 3 | **Absence** | "does not exist" is a checkable state, never a rendered value | `required_absence`, `pinned_at_bound`, `silence_is_not_proof` |
| 4 | **Trajectory** | assert the behavioural trace — skipped steps are invisible in the output | `ordered_subsequence`, `mechanism_counter_moved`, `coverage_bidirectional` |
| 5 | **Independent reproduction** | final-artifact conclusions need a second independent source | `diff_runs` + `merge_gate`, `replay_fidelity` |
| 6 | **Negative controls** | before measuring the system, measure how easily you can be fooled | `placebo_pass_rate`, `rule_has_teeth`, `degenerate_values`, `identical_arms` |
| 7 | **Verifier self-checks** | the verifier is software that breaks too | not a module: every check ships a negative fixture; `--selftest` proves the teeth at runtime; a meta-test enforces bidirectional fixture coverage |

Family 3 deserves a highlight: it barely exists in conventional testing
literature, yet all four origin projects hit it independently. The most
expensive hallucination is not the wrong field — it is the question that
silently stops being asked.

## Quickstart

```bash
pip install -e .            # zero runtime dependencies, Python >= 3.10
python -m sevencheck --selftest   # every check must bite known-bad input
python -m unittest discover -s tests
```

```python
import sevencheck as sc

findings = []
findings += sc.verbatim_quote(claim["quote"], sources[claim["source_id"]])
findings += sc.numbers_have_provenance(draft_text, allowed=evidence_values)
findings += sc.required_absence(extracted_form, must_be_absent=unasked_fields)
findings += sc.replay_fidelity(replay_verdicts, production_verdicts)

sc.assert_clean(findings)   # fail-closed: blockers raise, warns pass through
```

Every check returns `list[Finding]` (empty = pass) and never raises on bad
content — a raise can be swallowed by a retry loop; a Finding survives into
the report. Fail-closed is explicit via `assert_clean`.

## For agents: the skills

`skills/llm-output-verification/` — the operating skill: dispatch reflex,
situation→check table, FORBIDDEN list, self-catch anti-patterns, one cost
knob. `skills/check-authoring/` — how an incident becomes a check:
docstring-is-the-precedent, same-commit test-binding, mandatory negative
fixture, false-positive budget. Drop the `skills/` directory into your
agent's skill path.

## Process laws (what the checks assume around them)

1. Fail-closed is the default shape: allowlists exact and complete, no
   wildcards, out-of-bounds means kill.
2. Human gates live in state machines, not in prompts.
3. Every number carries four-part provenance: denominator, granularity,
   path:line, live-run reproduction command.
4. Before changing a prompt, write the falsifiable prediction
   (rootCause / predicted / atRisk / rollback) — *then* look at the score.

## Rules this repo holds itself to

- **No rule without an incident.** Every check's docstring carries the
  failure that created it. PRs adding "best practice" rules are declined.
- **Test-binding.** A check and its enforcing test land in the same commit.
- **Negative fixtures.** `python -m sevencheck --selftest` feeds every
  check a known-bad input; a meta-test fails the build if any check lacks
  one (it already caught two during initial development).
- **Zero dependencies.** Verification code you cannot audit in one sitting
  is verification you are taking on faith.

## Honesty section

This taxonomy is itself single-run: distilled by one reviewer from four
single-operator projects, and not yet independently validated. Its own
cheapest next experiment: have someone who lived none of these incidents
adopt the checks on a real pipeline and record where they break. Issues
reporting exactly that are the most valuable kind.

Docs: [中文完整 checklist](docs/checklist.zh-TW.md).

## License

MIT © 2026 Chi-Sheng Chen
