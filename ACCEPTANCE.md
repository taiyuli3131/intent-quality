# Acceptance Record

## v0.1 Candidate

Status: `v0.1 candidate accepted`

Date: 2026-06-16

## Acceptance Summary

The v0.1 candidate is accepted across the current product delivery, internal quality assets, CLI baseline, and safe self-improvement/public-library loop.

## Non-Blocking Notes

- The current eval scorer is an MVP heuristic scorer, not a full semantic evaluator.
- The public sync minimal loop generates candidate suggestions from index metadata. This is acceptable for v0.1, but later versions should strengthen real candidate content retrieval and stricter schema validation.

## v0.2 Direction

Status: `v0.2 scoped for next iteration`

Date: 2026-06-16

## v0.2 Acceptance Target

v0.2 should preserve the v0.1 local-first safety model while making the loop more trustworthy and useful in real projects.

The next candidate should be accepted only when:

- diagnosis reports produce clearer evidence, confidence, missing-information, and learning sections across manual, conversation, and project inputs;
- eval scoring is upgraded beyond the MVP heuristic baseline, with explicit evidence mapping and regression-friendly result records;
- public sync can fetch or stage real candidate content, not only index metadata, while keeping external samples untrusted by default;
- schema and rubric validation failures are visible, explainable, and blocking where adoption would be unsafe;
- suggestions include preview, impact scope, confirmation state, and rollback guidance before any local mutation;
- contribution packages include reviewable anonymization and privacy reports, with submission still blocked until explicit user authorization;
- playbook pages cover the core concepts users need to understand diagnosis results and safer Agent collaboration.

## v0.2 Non-Goals

- No hosted account system.
- No full dashboard.
- No automatic public upload.
- No automatic acceptance of public samples.
- No automatic mutation of profile, rules, accepted datasets, casebooks, rubrics, or contribution settings.
- No enterprise governance workflow.

## v0.2 Review Checklist

- The v0.1 CLI remains narrow and local.
- Any new mutating operation has preview, confirmation, and rollback language.
- Public samples remain untrusted until locally checked and user accepted.
- Eval improvements do not pretend to be a complete semantic judge unless the implementation supports that claim.
- Documentation distinguishes implemented v0.1 behavior from planned v0.2 work.

## v0.2-alpha Public Sync Baseline

Status: `v0.2-alpha public sync baseline accepted`

Date: 2026-06-18

Commit: `1dcc977`

Scope: public sync reliability hardening only.

Acceptance notes:

- Public index validation blocks unsafe sync policy hints, including automatic candidate download, rule application, profile mutation, dataset/casebook adoption, rubric override, and contribution setting changes.
- Candidate fetch verifies `content_sha256` before caching or suggestion generation.
- Public candidate gate blocks invalid YAML, missing required fields, schema/rubric mismatch, privacy flags, poisoning flags, and prompt-injection or auto-apply language.
- Good public candidate fixtures can become untrusted external candidates and pending suggestions.
- Failed public candidate fixtures are blocked before adoption suggestions are produced.
- Generated suggestions remain pending, reversible, previewable, and `requires_user_confirmation: true`.
- The alpha baseline does not add automatic acceptance, automatic local mutation, or public upload.

## v0.2-beta Scorer Baseline

Status: `v0.2-beta scorer baseline accepted`

Date: 2026-06-18

Commit: `ee050c9`

Baseline file: `.intent-quality/eval-results/v0.2-beta-scorer-baseline.yaml`

Scope: eval scorer reliability regression fixtures only.

Acceptance notes:

- The five core risk fixtures cover authorization boundary, context pollution, advice-only premature execution, unverified premise handling, and growth-goal preservation.
- Pass, fail, and hard `needs_review` response fixtures match expected statuses.
- Pass fixtures produce evidence without failure codes, forbidden observations, or blocking failures.
- Failing fixtures produce stable failure codes and evidence mapping.
- The hard fixture produces `needs_review` rather than a false pass or automatic failure when marker-based scoring cannot judge the case confidently enough.
- The scorer remains a heuristic marker-based regression scorer, not a complete semantic evaluator.

## v0.2 Candidate Readiness Notes

The accepted alpha and beta baselines cover the two main v0.2 reliability goals:

- safer public sync gates before any public candidate can become a suggestion;
- more inspectable eval scorer output for regression checks.

Remaining v0.2-candidate review should focus on documentation consistency, fixture coverage visibility, and confirmation language. It should not require platform features, hosted accounts, dashboards, or a full semantic evaluator.

## v0.2 Candidate

Status: `v0.2 candidate accepted`

Date: 2026-06-18

Accepted baseline:

- `1dcc977` establishes the v0.2-alpha public sync reliability baseline.
- `ee050c9` establishes the v0.2-beta scorer reliability baseline.
- `fb927ff` documents v0.2 candidate readiness and product boundaries.

Final acceptance notes:

- Public sync no longer relies only on index metadata before candidate suggestion generation.
- Public sync gates block hash mismatch, schema invalidity, privacy flags, poisoning flags, prompt-injection language, and auto-apply attempts before adoption-oriented suggestions are produced.
- Eval scorer fixtures cover the five core collaboration risks with pass/fail responses, plus a hard `needs_review` case.
- Eval results expose failure codes, evidence mapping, blocking failures, scorer limitations, and review status.
- All suggestion, candidate, contribution, profile/rule, dataset, casebook, and accepted public-sample changes remain confirmation-gated.
- `check` remains read-only and does not mutate rules, profiles, datasets, casebooks, candidates, suggestions, or submissions.
- v0.2 does not add hosted platform services, cloud accounts, dashboards, automatic public upload, automatic public-sample adoption, or full semantic evaluation.

Non-blocking notes:

- The eval scorer is stronger than v0.1 but remains a heuristic marker-based regression scorer, not a complete semantic evaluator.
- Adapter-ready output can be explored after v0.2, but DeepEval, Promptfoo, and Pydantic Evals are not core runtime dependencies in this candidate.
