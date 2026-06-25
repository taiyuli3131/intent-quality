# Acceptance Summary

This file records the public acceptance state for `intent-quality`.

For user-facing release details, see [docs/release-v0.3.md](docs/release-v0.3.md).

## Current Status

`intent-quality` is accepted as a v0.3 local candidate. v0.4 P0 diagnosis calibration is implemented as an unpublished, read-only development-line candidate baseline on top of that candidate; it is not a complete v0.4 release.

The v0.3 candidate keeps the project in its intended first-phase product shape:

- local-first;
- file-based;
- confirmation-gated;
- focused on Agent collaboration quality;
- explicit about scorer limitations and trust boundaries.

## Accepted Product Surface

The public repository includes:

- a local CLI for diagnosis, eval, suggestion review, public sync, contribution review, adapter export drafts, and read-only checks;
- diagnosis reports with finding-level evidence, confidence, premise status, targeted completion questions, expected versus actual mode, authorization scope, learning feedback, and preview-only generated candidates;
- playbook pages for authorization boundary, response mode, context pollution, premise validation, diagnose versus eval, public sample trust, suggestions and confirmation, and contribution privacy;
- profile-memory suggestions represented as pending, project-local, evidence-backed, rollback-described, and confirmation-gated proposals;
- eval review metadata for ambiguous `needs_review` outputs without changing the default heuristic scorer;
- experimental adapter export drafts for Promptfoo, DeepEval, and Pydantic Evals without running those frameworks or adding them as core runtime dependencies;
- public candidate fixtures and local gates that treat public samples as untrusted until checked and accepted.
- diagnosis calibration candidate fixtures that validate ready, needs-review, privacy/redaction-blocked, and candidate-gate-blocked diagnosis-quality cases without promoting them into accepted release material.

## Safety Boundaries

The accepted candidate does not add:

- hosted accounts;
- dashboards;
- automatic public upload;
- automatic public-sample adoption;
- automatic profile, rule, dataset, casebook, rubric, contribution, suggestion, or accepted-asset mutation;
- default LLM-as-judge scoring;
- complete semantic evaluation claims;
- external eval frameworks as core runtime dependencies.
- automatic sample backfill or candidate promotion.

All meaningful local adoption, profile or rule changes, accepted dataset or casebook changes, contribution submission, public-sample adoption, and future collaboration-behavior changes require user confirmation.

## Verification

The public acceptance bar is:

```bash
python -m intent_quality.cli check
python -m compileall intent_quality
python -m intent_quality.cli --help
python -m intent_quality.cli --version
```

Expected behavior:

- `check` remains read-only;
- no profile, rule, dataset, casebook, rubric, suggestion, candidate, contribution, or submission is mutated automatically;
- scorer output remains described as heuristic regression support, not complete semantic evaluation;
- adapter exports remain drafts for review.
- diagnosis calibration checks do not generate or approve real fixtures, write feedback, adopt candidates, or mutate protected local assets.
- diagnosis calibration gate reports include fixture counts, status counts, legacy coverage booleans, an independent coverage matrix, case/eval eligibility, reasons, blockers, `requires_confirmation`, and `auto_apply_allowed: false`.
- diagnosis calibration remains structural candidate gating, not a semantic evaluator, LLM-as-judge, automatic sample generator, or candidate-promotion mechanism.

## Version History

- v0.1 established the local MVP: diagnosis reports, local cases and eval datasets, heuristic scoring, public index fetch, pending suggestions, contribution package drafts, and read-only checks.
- v0.2 strengthened public sync and eval reliability while preserving the same safety model.
- v0.3 makes diagnosis, learning, profile-memory suggestions, eval review, and adapter export drafts coherent enough for a local candidate release.
- v0.4 P0 is an unpublished development-line candidate baseline, not a full v0.4 release.
- v0.4 P0 alpha candidate baseline: calibration fixtures and validator logic are aligned to the target schema/gate shape, including ready, needs-human-review, privacy blocked, and candidate-gate blocked fixtures. The baseline validates `confidence_range` and `diagnosis_quality_gate` fields. `check` remains read-only and does not generate, adopt, or mutate protected assets, write feedback, enable automatic adoption, use LLM-as-judge scoring, or claim complete semantic evaluation.
- v0.4 P0 candidate acceptance criteria: structural comparison, independent coverage matrix checks, and synthetic fixtures cover authorization boundary, premature execution, premise validation, context pollution, response-mode mismatch, goal/intent preservation, confidence overstatement, forbidden inference or motive attribution, missing completion questions, and blocked candidate gates. The coverage matrix is report-layer only: it includes `covered`, `fixture_ids`, `status_mix`, and `approved_sample_count`; blocked fixtures may count toward blocked coverage but do not count as approved samples. `check` remains read-only: it does not generate samples, write feedback, adopt candidates, modify protected assets, act as a semantic evaluator, use LLM-as-judge, automatically fill samples, or promote candidates. Public fixtures remain synthetic, redacted, or derived; real samples remain private local material by default unless separately generalized and explicitly approved.
