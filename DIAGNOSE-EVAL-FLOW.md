# Diagnose And Eval Flow

> Updated: 2026-06-16
> Purpose: operational flow for diagnosis, evaluation, public sync, contribution, and learning

## 1. End-To-End Loop

The intended loop is:

```text
diagnose
-> casebook
-> eval dataset
-> eval
-> public sync
-> suggestions
-> skill prevention
-> contribution
```

This loop turns real Agent collaboration issues into reusable cases, tests, learning feedback, and optional public contributions.

v0.1 proves the loop with local files, a narrow CLI, heuristic eval, public index sync, reviewable suggestions, and local contribution packages.

v0.2 makes the same loop more reliable without turning the project into a hosted platform:

```text
diagnose with stronger evidence
-> generate better cases and eval samples
-> run inspectable marker-based eval scoring
-> fetch/stage public candidate content through local gates
-> generate previewable suggestions
-> apply only after confirmation
-> record rollback and learning state
```

## 2. Diagnose

`diagnose` analyzes real usage.

Supported inputs:

- project-level read-only scan;
- conversation or log file;
- manual description;
- diagnosis-derived follow-up.

Example commands:

```bash
intent-quality diagnose --project .
intent-quality diagnose --conversation conversation.md
intent-quality diagnose --manual
```

Diagnosis should produce:

- human-readable `.md` report;
- machine-readable `.yaml` report;
- findings with evidence and confidence;
- missing information questions;
- learning feedback;
- candidate case;
- candidate eval sample;
- optional contribution candidate;
- optional profile or rule suggestions.

Manual diagnosis should be allowed, but incomplete input must produce lower-confidence findings and targeted completion questions.

## 3. Eval

`eval` runs standardized collaboration-quality tests.

Example commands:

```bash
intent-quality eval datasets/auth-boundary.yaml
intent-quality eval datasets/context-pollution.yaml
intent-quality eval --from-diagnosis diagnoses/diag_20260616_001.yaml
```

Eval should report:

- score by dimension;
- pass/fail status;
- failed requirements;
- evidence from the Agent response;
- suggested rubric, prompt, skill, or case updates.

v0.2 eval additionally reports:

- rubric and dataset versions used for the run;
- required observations that passed;
- required observations that were missing;
- forbidden observations that were detected;
- blocking failures that were triggered;
- failure codes;
- evidence excerpts;
- matched semantic or violation markers when available;
- short rationale per scored dimension;
- stable result IDs for regression comparison;
- whether the scoring method was heuristic, semantic, human-reviewed, or mixed;
- `needs_review` when a hard case is close to the pass threshold without a blocking failure.

The current v0.2-beta scorer is heuristic and marker-based. It is designed for regression checks and inspectable evidence, not complete semantic evaluation.

Eval samples should be generated naturally from high-quality diagnosis outputs rather than maintained as an unrelated test system.

## 4. Difference Between Diagnose And Eval

`diagnose` is for discovery and learning.

It asks:

- What happened?
- Why did collaboration fail?
- What did the Agent misunderstand?
- What did the user need to express more clearly?
- What should change next time?

`eval` is for verification and regression.

It asks:

- Can an Agent pass this known scenario?
- Did a change improve behavior?
- Did a regression appear?
- Does the Agent respect the expected collaboration standard?

## 5. Public Sync

Public sync should be automated but non-mutating by default.

Default policy:

```yaml
public_sync:
  enabled: true
  cadence: weekly
  auto_download_index: true
  auto_apply_rules: false
  auto_modify_profile: false
  auto_add_eval_cases: false
  user_can_change: true
```

Sync flow:

```text
weekly check
-> fetch public index
-> compare with local profile and diagnosis history
-> run Schema + Rubric checks
-> mark trust and risk
-> generate local suggestions
-> wait for user confirmation
```

External samples stay in `external-candidates` until accepted.

The first local closed-loop sample is documented in `docs/public-sync-contribution-minimal-loop.md` and represented under `examples/local-loop/.intent-quality/`.

v0.2 public sync separates index discovery from candidate content staging:

```text
fetch index
-> validate sync policy hints
-> select relevant entries
-> fetch or stage candidate content
-> verify content_sha256
-> parse YAML
-> run schema and rubric compatibility checks
-> run privacy and poisoning checks
-> require relevance explanation
-> cache candidate content
-> write untrusted external candidate
-> generate pending suggestions only if gates pass
```

Candidate content retrieval must not imply trust or adoption. Failed gates block suggestion generation for adoption-oriented actions. Passing gates still produce only untrusted external candidates and pending suggestions.

The public sync gate blocks:

- unsafe sync policy hints such as `auto_apply_rules: true`;
- missing required index or case fields;
- invalid or mismatched `content_sha256`;
- invalid YAML;
- schema or rubric mismatch;
- private paths, URLs, emails, secrets, or other privacy flags;
- prompt-injection or auto-apply language;
- candidates without relevance explanation.

## 6. Public Sample Trust

All public samples are untrusted by default.

Before local adoption, each sample should pass:

- schema validity check;
- rubric compatibility check;
- privacy risk check;
- poisoning risk check;
- relevance explanation check.

Public samples must not automatically:

- change profile;
- change rules;
- enter eval datasets;
- enter casebooks;
- override rubrics;
- change contribution settings.

## 7. Suggestions

Suggestions are generated from:

- diagnosis findings;
- public candidates;
- failed eval runs;
- repeated local patterns;
- user-approved contribution feedback.

Suggestion types:

- learning note;
- prompt/use habit advice;
- profile update candidate;
- local rule candidate;
- casebook entry candidate;
- eval sample candidate;
- contribution candidate.

All suggestions that mutate local state require preview and confirmation. Public sync suggestions start as pending proposals; they must not apply rules, update profiles, add accepted eval cases, add casebook entries, override rubrics, upload contributions, or change contribution settings.

v0.2 suggestions should be reviewable as small local change proposals.

Each mutating suggestion should show:

- source and evidence;
- target files or local state;
- proposed change summary;
- impact scope;
- non-goals;
- rollback plan;
- confirmation state;
- whether the action is reversible.

## 8. Contribution

Contribution is optional, lightweight, and shown at the end of a useful diagnosis.

Default prompt:

```text
This diagnosis found a collaboration issue that may help other Codex users.

You can generate an anonymized contribution candidate for the public case pool. This is optional. You can review, edit, limit allowed uses, skip it, or turn off future prompts.
```

Contribution flow:

```text
diagnosis completed
-> reusable pattern detected
-> lightweight invitation at report end
-> local contribution package generated
-> anonymization and privacy report generated
-> user reviews and edits
-> user selects allowed uses
-> user submits or keeps local
```

Contribution states:

- `pending_user_review`;
- `submitted_candidate`;
- `needs_revision`;
- `accepted_case`;
- `accepted_eval`;
- `rejected`;
- `withdrawn`.

v0.2 contribution review should make the privacy and authorization boundary clearer:

- show what was generalized or redacted;
- flag private paths, repository URLs, secrets, personal identifiers, and long verbatim logs;
- keep documentation-example permission off by default;
- require explicit submission authorization even after package generation;
- record withdrawal requests without rewriting diagnosis history.

## 9. Learning Feedback

Learning should help the user become a stronger Agent collaborator.

Every diagnosis should include a short learning section when relevant:

- what concept appeared in this case;
- why it matters for Codex;
- how the user can phrase tasks next time;
- how the Agent should respond next time;
- related playbook pages.

Examples of playbook topics:

- authorization boundary;
- context pollution;
- premise validation;
- response mode;
- public sample trust;
- diagnose versus eval.

v0.2 playbook coverage should include at least:

- authorization boundary;
- response mode;
- context pollution;
- premise validation;
- public sample trust;
- diagnose versus eval;
- suggestions and confirmation;
- contribution privacy.

## 10. Pre-Action Skill Behavior

The Codex skill should support light, standard, and strict modes.

Light mode:

- mostly invisible;
- only surfaces warnings when risk is material.

Standard mode:

- checks goal, premise, risk, authorization, and response mode for complex tasks.

Strict mode:

- requires explicit confirmation before file writes, memory updates, rule updates, dataset changes, casebook changes, public contribution, or public-sample adoption.

Direction discussions, project positioning discussions, and memory/rule updates should default to discussion unless execution is explicitly authorized.

## 11. Review Checks

After documentation or tooling changes, review:

- whether current decisions are covered;
- whether the same positioning is repeated across too many documents;
- whether historical principles are absorbed;
- whether public samples remain untrusted by default;
- whether every mutating action requires confirmation;
- whether diagnosis and eval are clearly separated but connected.
