# Intent Quality Project Info

> Updated: 2026-06-22
> Status: v0.3 open source foundation accepted; project overview and document index

## 1. Current Positioning

`intent-quality` is a local-first Agent collaboration quality system for Codex users.

Its purpose is to help users diagnose, test, and improve how file-capable AI Agents understand goals, respect authorization boundaries, avoid context pollution, validate premises, and choose the right response mode before acting.

The project is not just prompt optimization, answer evaluation, or an eval platform. It is a collaboration-quality layer for Agent users who rely on Codex-like tools to read projects, edit files, run commands, and maintain long-running work.

## 2. Primary Audience

The first audience is Codex users and adjacent Agent users who:

- use Agents to inspect and change local projects;
- need stronger control over discussion, drafting, execution, and persistence;
- want to diagnose recurring collaboration failures;
- want reusable tests for Agent behavior;
- want to learn better Agent collaboration habits over time.

Enterprise governance and full cloud platforms are future expansion paths, not the first product shape.

## 3. Core Product Loop

The project is organized around this loop:

```text
diagnose real collaboration issues
-> turn findings into casebook entries
-> convert cases into eval dataset samples
-> run eval to verify Agent behavior
-> sync public cases as untrusted candidates
-> generate local suggestions
-> use skill rules for pre-action prevention
-> optionally contribute anonymized cases back to the public pool
```

## 4. Fixed First-Phase Decisions

- Local-first implementation.
- No full eval platform in the first phase.
- `diagnose` and `eval` are both required.
- `diagnose` is the first user-facing entry point.
- Reports should be generated as both `.md` and `.yaml`.
- Schemas should use YAML.
- Local project state should live under `.intent-quality/`.
- Public samples are untrusted by default.
- Public samples require local Schema + Rubric checks before use.
- Rules, profile, dataset, casebook, and contribution changes require user confirmation.
- Contribution prompts are lightweight, optional, reviewable, and dismissible.
- Public library sync is automated by default on a weekly cadence, but only downloads indexes and generates suggestions.
- The learning module uses a two-layer design: short feedback inside diagnosis reports plus local playbook concept pages.

## 5. Document Map

- `README.md`: user-facing project entry, CLI overview, v0.2 reliability baseline, and safety model.
- `ACCEPTANCE.md`: version acceptance record, including v0.1 and v0.2 candidate acceptance.
- `PRODUCT-SPEC.md`: current product specification, scope, modules, trust boundaries, and first-phase behavior.
- `SCHEMAS.md`: YAML schemas for diagnosis, case, eval dataset, profile, public candidate, suggestion, and contribution files.
- `DIAGNOSE-EVAL-FLOW.md`: operational flow for diagnose, eval, public sync, suggestions, contribution, and learning feedback.
- `docs/release-v0.2.md`: current v0.2 capability summary and non-goals.
- `docs/launch-copy.md`: GitHub/social launch copy and short project descriptions.
- `docs/open-source-foundation-checklist.md`: open-source readiness checklist and verification commands.
- `docs/v0.3-planning-brief.md`: seed brief for v0.3 planning.
- `docs/v0.3-roadmap.md`: v0.3 planning baseline, including priorities, scope, non-goals, acceptance criteria, and follow-up workstreams.
- `docs/public-sync-contribution-minimal-loop.md`: first local closed-loop design for public sync, external candidate checks, suggestions, contribution packages, anonymization, withdrawal, and prompt controls.
- `public-registry/`: sample public registry structure and index format.
- `intent-quality-direction.md`: early English direction record. Keep as historical source; do not use it as the active product spec.
- `intent-quality-followups.md`: charger ranking case follow-up and rule source. Keep as a concrete case record, not as the overall roadmap.

## 6. Current Accepted Baseline

Current accepted tag:

- `v0.3-open-source-foundation`

Baseline commits:

- `cc97e94`: v0.1 candidate accepted.
- `1dcc977`: v0.2-alpha public sync reliability baseline.
- `ee050c9`: v0.2-beta scorer reliability baseline.
- `fb927ff`: v0.2 candidate readiness and product boundary documentation.
- `1e8b414`: v0.2 candidate acceptance record.
- `88937d9`: v0.3-alpha diagnosis quality baseline.
- `cc29d00`: v0.3 playbook baseline.
- `606eaad`: v0.3 profile memory baseline.
- `aa07b46`: open-source foundation preparation.
- `28fcde4`: open-source foundation acceptance.

The current public baseline is an open-source local foundation, not a platformization release.

Accepted current capabilities:

- project-local diagnosis with Markdown and YAML reports;
- finding-level evidence, confidence, premise status, completion questions, expected/actual mode, authorization scope, and generated candidate previews;
- public sync fetches or stages real candidate content before suggestion generation;
- public sync verifies `content_sha256` and blocks unsafe candidate gates;
- eval scorer output includes failure codes, evidence mapping, blocking failures, scorer limitations, and `needs_review`;
- local playbook pages cover recurring Agent collaboration concepts;
- profile memory is represented as pending, project-local, confirmation-gated suggestions only;
- public candidate, suggestion, contribution, profile/rule, dataset, and casebook changes remain user-confirmation gated;
- `check` remains read-only and covers public sync fixtures, eval response fixtures, diagnosis quality fixtures, profile memory fixtures, and playbook links.

Accepted non-goals:

- hosted accounts;
- full dashboard;
- automatic public upload;
- automatic public-sample adoption;
- automatic profile/rule/dataset/casebook/rubric/contribution mutation;
- full semantic evaluation.

## 7. Historical Content Integration

Historical project notes contained several useful principles that are now absorbed into the formal specs:

- gradual adoption: start with a compact core loop, then add memory, regression tests, domain overlays, and automation progressively;
- comparison tests: future evaluations should compare ordinary model behavior, prompt-only clarification, and post-output evaluation;
- automatic update target: collect samples, run rubric checks, detect regressions, generate candidate updates, request user approval, then rerun affected tests;
- acceptance criteria and verification should be defined before action when the task requires it.

Older historical content that was only a subset of the current charger-ranking follow-up is not retained separately.

## 8. Next Planning Direction

v0.3 planning has a baseline roadmap in `docs/v0.3-roadmap.md`.

The v0.3 product goal is to make `diagnose` trustworthy enough to become the main product entry point while preserving the v0.2 local-first, file-based, confirmation-gated safety model.

Priority order:

- P0: diagnosis quality, including finding-level evidence, confidence, premise status, targeted completion questions, authorization-scope analysis, learning notes, and preview-only diagnosis-derived candidates.
- P1: learning and playbook expansion for the concepts users see in diagnosis reports.
- P1: local profile memory as reviewable suggestions only, including recurring failure summaries, stale-memory warnings, impact scope, and rollback notes.
- P1: eval review through human-review status and reviewer notes for ambiguous `needs_review` cases.
- P2: adapter export as experimental/internal draft output only.
- P2: public registry maintenance below platform scope.

v0.3 should not add hosted accounts, dashboards, automatic public upload, automatic public-sample adoption, automatic profile/rule/dataset/casebook/rubric/contribution mutation, production registry trust infrastructure, default LLM-as-judge scoring, or a complete semantic evaluator.

The first implementation specialty should be diagnosis quality.

## 9. First-Phase Deliverables

The next implementation stage should create the local file base and lightweight tooling around:

- project-level `diagnose`;
- diagnosis report generation;
- local casebook generation;
- eval dataset generation and execution;
- public library index sync;
- suggestion review and application;
- anonymized contribution packages;
- Codex skill rules for pre-action prevention.

The first phase should prove the underlying logic and document structure before building dashboards, accounts, cloud storage, or a complete hosted eval platform.
