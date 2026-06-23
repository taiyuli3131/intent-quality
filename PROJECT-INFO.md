# Intent Quality Project Info

> Updated: 2026-06-22
> Status: public project overview

## Overview

`intent-quality` is a local-first Agent collaboration quality system for Codex and file-capable Agent users.

It helps users diagnose, test, and improve how Agents:

- understand the user's goal;
- respect authorization boundaries;
- avoid stale context and context pollution;
- validate important premises before acting on them;
- choose the right response mode before reading files, editing files, running commands, or creating durable local state.

The project is not a hosted eval platform, prompt collection, or generic answer grader. It is a practical quality layer for people who use Agents to work inside local projects.

## Audience

The first audience is developers and project owners who:

- use Codex-like Agents to inspect and change local projects;
- need clearer control over discussion, drafting, verification, execution, and persistence;
- want repeatable collaboration-quality checks;
- want reusable diagnosis and eval fixtures for Agent behavior;
- want local learning and reviewable suggestions without automatic mutation.

## Product Loop

The project centers on a local, confirmation-gated loop:

```text
diagnose real collaboration issues
-> create reviewable local candidates
-> run repeatable eval checks
-> review suggestions
-> improve future Agent behavior
-> optionally prepare anonymized contribution candidates
```

Public samples and local suggestions are useful leads, not trusted or applied assets. They become durable local state only after user confirmation.

## Current Public Scope

Included:

- local diagnosis reports in Markdown and YAML;
- eval cases and response fixtures for collaboration-quality regressions;
- public candidate sync gates with privacy, poisoning, schema, rubric, and hash checks;
- pending, project-local profile-memory suggestions;
- local human-review metadata for ambiguous eval results;
- experimental adapter export drafts for Promptfoo, DeepEval, and Pydantic Evals;
- synthetic v0.4 P0 diagnosis calibration fixtures and read-only validation;
- playbook pages that explain the concepts surfaced by diagnosis reports;
- read-only verification checks.

Not included:

- hosted accounts;
- dashboards;
- automatic uploads;
- automatic public-sample adoption;
- automatic profile, rule, dataset, casebook, rubric, contribution, suggestion, or accepted-asset mutation;
- default LLM-as-judge scoring;
- complete semantic evaluation;
- external eval frameworks as core runtime dependencies.

## Document Map

- [README.md](README.md): public entry point, install instructions, quick start, use cases, and safety model.
- [PRODUCT-SPEC.md](PRODUCT-SPEC.md): active product specification and first-phase boundaries.
- [ACCEPTANCE.md](ACCEPTANCE.md): public acceptance summary.
- [SCHEMAS.md](SCHEMAS.md): YAML-first local file schemas.
- [DIAGNOSE-EVAL-FLOW.md](DIAGNOSE-EVAL-FLOW.md): operational flow for diagnosis, eval, public sync, suggestions, contribution, and learning feedback.
- [docs/release-v0.3.md](docs/release-v0.3.md): v0.3 release notes.
- [docs/release-v0.2.md](docs/release-v0.2.md): v0.2 reliability release notes.
- [docs/v0.3-roadmap.md](docs/v0.3-roadmap.md): public roadmap for the v0.3 product direction.
- [docs/v0.4-diagnosis-quality.md](docs/v0.4-diagnosis-quality.md): v0.4 P0 diagnosis calibration scope and acceptance.
- [docs/public-sync-contribution-minimal-loop.md](docs/public-sync-contribution-minimal-loop.md): design note for public sync and contribution review.
- [docs/playbook/](docs/playbook/): short learning pages for recurring Agent collaboration concepts.
- [examples/](examples/): synthetic examples and regression fixtures.
- [public-registry/](public-registry/): sample public registry structure.

## Verification

Before publishing or contributing changes, run:

```bash
python -m intent_quality.cli check
python -m compileall intent_quality
```

`check` is expected to remain read-only. It must not apply suggestions, accept public samples, mutate profiles, change rules, edit datasets or casebooks, submit contributions, apply adapter results, generate real fixtures, write feedback, or adopt diagnosis candidates.
