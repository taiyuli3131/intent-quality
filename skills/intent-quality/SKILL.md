---
name: intent-quality
description: Local-first Agent collaboration quality workflow for Codex. Use when checking whether a Codex/Agent task preserved user intent, respected authorization boundaries, avoided stale context, validated premises, chose the right response mode, ran local collaboration-quality evals, reviewed pending suggestions, or prepared confirmation-gated learning from real AI coding sessions.
---

# Intent Quality

Use this skill to keep Codex collaboration aligned before, during, and after work in a repository that uses `intent-quality`.

## Core Rules

- Preserve the user's current goal over stale thread context or inferred motives.
- Treat discussion, brainstorming, and review requests as non-execution unless the user authorizes changes.
- Validate important premises before relying on them, especially dates, release state, remote state, and claims about what has already happened.
- Keep local learning confirmation-gated. Do not apply rules, profiles, datasets, casebooks, rubrics, contribution status, or profile memory automatically.
- Prefer read-only checks before mutation. Say clearly when a command writes files.
- Before push or release work, run the repository's required checks:

```bash
git status --short
python -m intent_quality.cli check
python -m compileall intent_quality
```

## Repository Workflow

When using this skill in the `intent-quality` repository:

1. Inspect local state with `git status --short`.
2. Classify the user's request as discussion, review, diagnosis, eval, implementation, release, or publication.
3. If the request is ambiguous or high-impact, state the key assumption before acting.
4. Use the existing CLI where possible:

```bash
python -m intent_quality.cli check
python -m intent_quality.cli diagnose --manual --description "..."
python -m intent_quality.cli eval datasets/collaboration-quality.v0.1.yaml --response path/to/response.md --eval-id eval_id
python -m intent_quality.cli suggest list
python -m intent_quality.cli contribute review
```

5. For code or docs changes, keep edits narrow and consistent with the current local-first safety model.
6. After changes, run the required verification commands and report any failures plainly.

## Diagnosis Workflow

Use diagnosis when a real collaboration interaction went wrong or felt risky.

- Identify expected response mode and actual response mode.
- Check authorization scope: advice, planning, file edits, commands, git, release, or external action.
- Check stale context, unsupported premises, goal replacement, and premature execution.
- Produce concrete next behavior: what the user should ask for, and what the Agent should do differently.
- If a reusable pattern appears, recommend a pending suggestion or eval case; do not apply it without user confirmation.

## Eval Workflow

Use evals for repeatable regression checks.

- Pick the closest dataset case under `datasets/` or `cases/`.
- Run the CLI eval with an explicit response file and eval id.
- Treat heuristic scorer output as a regression signal, not a complete semantic judge.
- When adding fixtures, include both pass and fail examples when useful.

## Release And GitHub Workflow

For publishing, tags, releases, assets, repo description, topics, or README discovery work:

- Check local cleanliness before changing anything.
- Verify `origin`, branch, tag, and release state before assuming remote status.
- Before each push, run:

```bash
git status --short
python -m intent_quality.cli check
python -m compileall intent_quality
```

- Upload release assets only after confirming they match the current intended commit.
- Do not move an accepted release tag unless the user explicitly asks.

## Safety Boundaries

`intent-quality` is not a hosted eval platform and must not automatically upload local data, submit contribution packages, accept public samples, apply profile memory, or mutate accepted local assets. Keep all meaningful learning and adoption reviewable by the user.
