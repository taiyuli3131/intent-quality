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

## v0.3 Planning Baseline

Status: `v0.3 planning baseline accepted`

Date: 2026-06-18

Baseline file: `docs/v0.3-roadmap.md`

Scope: roadmap only; no code implementation.

Planning baseline notes:

- v0.3 should make `diagnose` trustworthy enough to become the main product entry point.
- P0 is diagnosis quality: finding-level evidence, confidence, premise status, targeted completion questions, authorization-scope analysis, learning notes, and preview-only diagnosis-derived candidates.
- P1 includes playbook expansion, confirmation-gated local profile memory suggestions, and human-review workflow for ambiguous eval results.
- P2 includes experimental/internal adapter export drafts and limited public registry maintenance below platform scope.
- The first implementation specialty should be diagnosis quality.

v0.3 planning non-goals:

- No hosted account system.
- No full dashboard.
- No platformization.
- No automatic public upload.
- No automatic public-sample adoption.
- No automatic profile, rule, dataset, casebook, rubric, contribution, or public sample mutation.
- No default LLM-as-judge scorer.
- No complete semantic evaluator claim for the heuristic scorer.
- No adapter export as a core runtime dependency.

v0.3 candidate acceptance target:

- Diagnosis reports expose evidence, confidence, premise status, missing-information questions, expected versus actual mode, and authorization scope.
- Diagnosis-derived case, eval, profile, rule, contribution, and public-sample actions remain preview-only or pending suggestions.
- Playbook pages cover the core concepts used in diagnosis reports.
- Local profile memory remains reviewable and confirmation-gated.
- Eval review can record human-review status and reviewer notes without changing the default scorer claim.
- Experimental adapter exports are clearly marked internal and optional.
- `intent-quality check` remains read-only and confirms the no-mutation boundary.

## v0.3-alpha Diagnosis Quality Baseline

Status: `v0.3-alpha diagnosis quality baseline accepted`

Date: 2026-06-18

Scope: diagnosis quality only; no playbook expansion, profile memory implementation, adapter export, LLM-as-judge, dashboard, hosted platform, or automatic mutation.

Acceptance notes:

- Manual and conversation diagnosis fixtures are covered by `intent-quality check`.
- Diagnosis YAML exposes finding-level evidence, confidence, premise status, targeted completion questions, expected versus actual mode, authorization scope, learning notes, and generated candidates.
- Markdown diagnosis reports render the v0.3-alpha diagnosis structure for user review.
- Generated case, eval, profile, rule, contribution, and public-sample actions remain preview-only and do not create accepted assets or apply changes.
- `check` remains read-only and reports `diagnosis quality fixtures` alongside the existing public sync and eval fixture checks.
- No v0.3-alpha implementation work adds platform features, default LLM-as-judge scoring, adapter runtime dependencies, or automatic local mutation.

Non-blocking notes:

- Example synchronization cleanup may be handled after the baseline if future edits need to better align generated example Markdown and YAML presentation details.

## v0.3 P1 Playbook And Learning Baseline

Status: `v0.3 P1 Playbook And Learning accepted baseline`

Date: 2026-06-18

Scope: local playbook and learning-link coverage only; no diagnosis core logic expansion, profile memory implementation, adapter export, LLM-as-judge, hosted platform, dashboard, or automatic mutation.

Acceptance notes:

- Playbook pages cover the core concepts used by diagnosis learning feedback: authorization boundary, context pollution, premise validation, response mode, diagnose versus eval, public sample trust, suggestions and confirmation, and contribution privacy.
- Diagnosis examples link learning concepts to local playbook pages.
- `intent-quality check` validates playbook links and remains read-only.
- The learning layer stays compact and local; it is not a generic AI course or platform documentation system.
- The baseline does not apply profile/rule/dataset/casebook/rubric/contribution/public-sample changes.

## v0.3 P1 Local Profile Memory Baseline

Status: `v0.3 P1 Local Profile Memory accepted baseline`

Date: 2026-06-18

Scope: diagnosis-derived local profile memory suggestions only; no confirmed profile writes, global memory, cross-project memory, broad personal memory, cloud sync, platformization, or automatic mutation.

Acceptance notes:

- Profile memory output is represented as pending `profile_update` suggestions only.
- Profile suggestions are project-local, evidence-backed, impact-scoped, rollback-described, and explicitly `requires_user_confirmation: true`.
- Stale-memory warnings are represented as reviewable suggestions and must not become confirmed preferences automatically.
- Unsafe profile memory fixtures block private information, global/cross-project memory, and auto-apply attempts.
- `intent-quality check` validates profile memory fixtures and remains read-only.
- `python -m compileall intent_quality` passes.
- The baseline does not modify profiles, rules, datasets, casebooks, rubrics, contributions, candidates, suggestions, or submissions during checks.

## Open Source Foundation Prep

Status: `open source foundation prep completed`

Date: 2026-06-18

Scope: open-source readiness files and metadata only; no core product feature expansion.

Acceptance notes:

- MIT license, contribution guide, security policy, privacy policy, and open-source foundation checklist are present.
- README includes install, quick start, verification commands, safety model, contribution guidance, and license pointer.
- `pyproject.toml` includes version `0.3.0`, MIT license metadata, contributors, keywords, and classifiers.
- `.intent-quality/` remains ignored as local runtime state.
- `python -m intent_quality.cli check` passes and remains read-only.
- `python -m compileall intent_quality` passes.
- `python -m intent_quality.cli --help` works.
- Sensitive-string scan found only policy text and deliberate unsafe/privacy fixtures, not real local credentials or private workspace paths.

## Open Source Foundation

Status: `open source foundation accepted`

Date: 2026-06-18

Accepted baseline:

- `aa07b46` prepares open-source foundation files and metadata.

Final acceptance notes:

- No blocking issues were found in the final open-source foundation review.
- README, license, contribution guide, security policy, privacy policy, package metadata, examples, and local-first safety boundaries are ready for public repository use.
- `python -m intent_quality.cli check` passes and confirms read-only behavior.
- `python -m compileall intent_quality` passes.
- `python -m intent_quality.cli --help` works.
- Package version metadata is aligned at `0.3.0`.

Recommended tag:

- `v0.3-open-source-foundation`

## v0.3 P1 Eval Review Baseline

Status: `v0.3 P1 Eval Review accepted baseline`

Date: 2026-06-22

Scope: local human-review metadata for `needs_review` eval results only; no default scorer change, LLM-as-judge, adapter export, dashboard, platformization, or automatic mutation.

Acceptance notes:

- `needs_review` eval results include a pending human-review slot.
- Eval review fixtures cover `confirmed_pass`, `confirmed_fail`, and `remains_uncertain`.
- Reviewer notes and false-positive / false-negative calibration notes are local metadata only.
- Eval review records preserve the heuristic scorer limitation language and do not claim full semantic evaluation.
- Eval review validation confirms records do not apply results, change the default scorer, or mutate datasets, rubrics, profiles, rules, casebooks, suggestions, candidates, contributions, or submissions.
- `intent-quality check` validates eval review fixtures and remains read-only.
- `python -m compileall intent_quality`, `python -m intent_quality.cli --help`, and `python -m intent_quality.cli --version` pass.

## v0.3 P2 Adapter Export Baseline

Status: `v0.3 P2 Adapter Export local baseline`

Date: 2026-06-22

Scope: experimental/internal adapter export drafts only; no external framework execution, no core runtime dependency, no default scorer replacement, no LLM-as-judge, no dashboard, no platformization, and no automatic mutation.

Acceptance notes:

- `adapter export` supports draft output for `promptfoo`, `deepeval`, and `pydantic-evals`.
- Exported drafts include source dataset metadata, schema/rubric versions, scorer limitations, and explicit experimental/internal status.
- Export safety metadata states that the draft does not run external frameworks, does not become a core runtime dependency, does not change the default scorer, does not apply results, and does not mutate assets.
- Adapter fixtures preserve `<response under test>` placeholders and are intended for review before any external use.
- `intent-quality check` validates adapter export fixtures and remains read-only.

## v0.3 Candidate-Ready Baseline

Status: `v0.3 candidate-ready baseline`

Date: 2026-06-22

Scope: documentation consistency cleanup and final local validation for v0.3 candidate readiness; no new product capability, no platformization, no external framework runtime integration, no default LLM-as-judge scoring, and no automatic mutation.

Acceptance notes:

- README, PROJECT-INFO, PRODUCT-SPEC, DIAGNOSE-EVAL-FLOW, and v0.3-roadmap consistently describe v0.3 as a local-first, file-based, confirmation-gated candidate.
- Eval Review is documented as local human-review metadata for `needs_review` outputs only. It does not change the default heuristic scorer, apply results, or mutate datasets, rubrics, profiles, rules, casebooks, suggestions, candidates, contributions, or submissions.
- Adapter Export is documented as experimental/internal draft output for Promptfoo, DeepEval, and Pydantic Evals. It does not run external frameworks, add core runtime dependencies, replace the heuristic scorer, apply results, or mutate local assets.
- Public sync remains untrusted candidate + local gate + pending suggestion, not automatic adoption.
- Profile memory remains project-local pending suggestion, not automatic memory or global/cross-project memory.
- `intent-quality check` remains read-only and covers public sync fixtures, eval response fixtures, eval review fixtures, diagnosis quality fixtures, profile memory fixtures, adapter export fixtures, and playbook links.

Verification:

- `python -m intent_quality.cli check` passed.
- `python -m compileall intent_quality` passed.
- `python -m intent_quality.cli --help` passed.
- `python -m intent_quality.cli --version` returned `intent-quality 0.3.0`.

## v0.3 Candidate Accepted

Status: `v0.3 candidate accepted`

Date: 2026-06-22

Scope: final acceptance of the v0.3 candidate-ready baseline; no remote push, no release tag movement, no platformization, no dashboard, no automatic upload/adoption/mutation, no default LLM-as-judge, no complete semantic evaluator, and no external eval framework core dependency.

Acceptance notes:

- The v0.3 candidate-ready baseline is acceptable.
- Documentation and implementation remain aligned around local-first, file-based, confirmation-gated boundaries.
- Eval Review remains local human-review metadata only.
- Adapter Export remains an experimental/internal draft only.
- Profile memory remains a project-local pending suggestion.
- Public sync remains untrusted candidate + local gate + pending suggestion.
- `intent-quality check` remains read-only.
- No blocking issue was found for v0.3 candidate acceptance.
- The uncommitted planning brief control-rule change is non-blocking and intentionally not included in this acceptance commit.

Verification:

- `python -m intent_quality.cli check` passed.
- `python -m compileall intent_quality` passed.
- `python -m intent_quality.cli --help` passed.
- `python -m intent_quality.cli --version` returned `intent-quality 0.3.0`.

Local tag:

- `v0.3-candidate-accepted`
