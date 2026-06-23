# intent-quality v0.3 Release Notes

> Status: local candidate
> Date: 2026-06-22

## Summary

v0.3 turns the local-first collaboration-quality loop into a more complete candidate workflow.

The release improves diagnosis quality, local learning, profile-memory suggestions, eval review metadata, and adapter export drafts while preserving the original safety model: local files first, public samples untrusted by default, and no meaningful mutation without user confirmation.

## Highlights

- Diagnosis reports now expose finding-level evidence, confidence, premise status, targeted completion questions, expected versus actual mode, authorization scope, learning feedback, and preview-only generated candidates.
- Playbook pages explain the core concepts used by diagnosis reports: authorization boundary, response mode, context pollution, premise validation, diagnose versus eval, public sample trust, suggestions and confirmation, and contribution privacy.
- Profile memory is represented as pending, project-local suggestions with source evidence, impact scope, confirmation state, and rollback notes.
- Eval review can record local human-review metadata for ambiguous `needs_review` outputs without changing the default heuristic scorer.
- Adapter export can emit experimental draft mappings for Promptfoo, DeepEval, and Pydantic Evals for review.
- `intent-quality check` remains read-only and validates public sync, eval response, eval review, diagnosis quality, profile memory, adapter export, and playbook fixtures.

## Safety Model

v0.3 keeps the project local-first and confirmation-gated.

The release does not automatically:

- upload local data;
- submit contribution packages;
- accept public samples;
- apply profile memory;
- mutate rules, datasets, casebooks, rubrics, suggestions, candidates, contributions, or accepted assets;
- run external eval frameworks;
- replace the default heuristic scorer.

Public samples remain untrusted until local checks pass and the user explicitly accepts adoption.

## What Changed Since v0.2

v0.2 focused on reliability hardening for public sync and eval scoring.

v0.3 adds the user-facing review layers around that reliable base:

- richer diagnosis output;
- local concept learning through playbook pages;
- reviewable project-local profile-memory suggestions;
- local human-review records for uncertain eval outcomes;
- adapter export drafts for external-tool comparison planning.

## Known Limits

- The default scorer is still heuristic and marker-based. It is useful for regression checks, but it is not a complete semantic evaluator.
- Adapter exports are drafts for inspection and future integration work. They do not run Promptfoo, DeepEval, or Pydantic Evals.
- Profile-memory output remains pending suggestion data. It is not confirmed memory and is not global or cross-project memory.
- Public registry support is a local trust and fixture workflow, not hosted registry governance.

## Verification

Recommended release checks:

```bash
python -m intent_quality.cli check
python -m compileall intent_quality
python -m intent_quality.cli --help
python -m intent_quality.cli --version
```

Expected result:

- checks complete without mutating local assets;
- the CLI reports version `0.3.0`;
- documentation continues to describe the local-first, confirmation-gated safety model.
