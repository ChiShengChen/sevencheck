---
name: llm-output-verification
description: >
  MANDATORY whenever an LLM output will be treated as fact: quotes,
  citations, ids, numbers, extracted fields, experiment metrics, replayed
  evaluations. Use BEFORE trusting, merging, or publishing any such output.
  Provides the dispatch reflex (check vs. skill vs. human) and maps each
  situation to a deterministic check in the `sevencheck` package. Never
  verify by re-asking the model.
---

# LLM output verification

## The criterion (read first)

An output is automatically verifiable iff you can write a function that
declares FAIL **without seeing the generation process** — only the output
plus pre-existing data. If you can write that function, write it (or find
it below). If you cannot, this is judgment work: escalate to a human gate;
do not fake verification with a second model call.

The design question for every number that carries an argument:
**"If the thing I believe is happening were not happening, what would this
output look like?" Then check whether it already looks like that.**

## Dispatch reflex

1. Can the failure be detected from the artifact alone?
   → run the matching check below; wire `assert_clean` fail-closed.
2. It cannot, but a human must decide every time?
   → route to a human gate held in a state machine, not in a prompt.
3. It has never actually failed?
   → do NOT add a rule. No rule without an incident.

## Situation → check (run these, do not re-derive)

| You are about to trust… | Run |
| --- | --- |
| a quote or citation | `verbatim_quote` / `quotes_regrep` — byte-strict; a failed quote is a dead claim |
| an identifier (PMID, ticker, body id) | `ids_resolvable` against a local authority |
| prose containing numbers | `numbers_have_provenance` with the evidence values |
| a structured object | `required_fields`; the validator is the only truth |
| an assembled artifact | `build_complete` — missing section = non-zero exit |
| an extracted form | `required_absence` for every not-yet-asked field |
| a metric sitting on 0.0 / 1.0 / chance | `pinned_at_bound` — unreadable without a validity flag |
| a "clean" scan report | `silence_is_not_proof` over the expected id set |
| an interactive agent's behaviour | `ordered_subsequence` on the event trace, not the final doc |
| a claimed fix | `mechanism_counter_moved` — aggregates are noise, not evidence |
| cross-references | `coverage_bidirectional` — both directions |
| a conclusion headed for the final artifact | `diff_runs` + `merge_gate` (blind dual-run) |
| offline-replay conclusions | `replay_fidelity` FIRST; infidelity voids everything |
| the framework itself | `placebo_pass_rate`, `rule_has_teeth`, `degenerate_values`, `identical_arms` |

Smoke: `python -m sevencheck --selftest` must print `N/N checks bite`.

## FORBIDDEN

- NEVER patch a failed quote to make re-grep pass. The claim is dropped.
- NEVER fill an absent field with a typical/catalog value. Absence is the signal.
- NEVER read a bound-pinned value (0.000, 1.000, chance) without its validity flag.
- NEVER credit a fix by an aggregate metric. Only its own mechanism counter counts.
- NEVER let the model mint an id, a number, or a citation into the artifact.
- NEVER verify a model's output by asking a model whether it looks right.
- NEVER treat a clean report as proof before confirming the content reached the scanner.

## Anti-patterns (self-catch triggers)

- If you find yourself rewording a quote so the substring match passes — stop; the claim is dead.
- If you find yourself explaining why this 0.000 is "probably a real zero" — stop; add the flag or drop the value.
- If you find yourself citing the overall pass-rate to justify a change — stop; show the mechanism counter.
- If you find yourself adding a rule for something that never happened — stop; incidents only.

## Cost knob (one)

`STRICTNESS`: default = byte-strict everywhere (`normalize_ws=False`,
`tolerance=0`). Loosen only per-call, only with the weakening recorded next
to the result. Default equals the previous version's behaviour.

## What this skill cannot catch

Semantic wrongness inside a verbatim, well-formed, well-provenanced claim;
collusion between generator and the data source; anything whose ground truth
lives only in a human's head. Those go to human gates — this skill's job is
to make sure nothing else does.
