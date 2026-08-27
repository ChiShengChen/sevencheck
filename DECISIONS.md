# DECISIONS (append-only; supersede, never delete)

| id | date | decision | rationale | status |
|----|------|----------|-----------|--------|
| D1 | 2026-08-27 | Zero runtime dependencies; stdlib only | Verification code you cannot audit in one sitting is taken on faith; also removes supply-chain surface from the verifier itself | active |
| D2 | 2026-08-27 | Checks return `list[Finding]`; never raise on bad content; fail-closed only via explicit `assert_clean` | A raise can be swallowed by a retry loop; a Finding is data that survives into the report | active |
| D3 | 2026-08-27 | Family 7 is not a module: it is `--selftest` (runtime negative fixtures) + a meta-test enforcing bidirectional fixture coverage | The verifier must be treated as software that breaks; the meta-test caught 2 missing fixtures on day one | active |
| D4 | 2026-08-27 | `verbatim_quote` default is byte-strict; only whitespace-collapse is offered as an explicit, recorded weakening | Every normalization step is a place for a fabricated quote to hide | active |
| D5 | 2026-08-27 | v0.1 ships one combined test file rather than one file per contract | Pragmatic for a single-module release; revisit (supersede) when a second module lands | active |
