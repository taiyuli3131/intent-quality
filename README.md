# intent-quality

`intent-quality` is a local-first collaboration quality system for Codex and file-capable Agent users.

It helps you diagnose, test, and improve how an Agent understands your goal, respects authorization boundaries, avoids stale context, validates premises, and chooses the right response mode before taking action.

Use it when you need local-first Agent evaluation, collaboration-quality regression checks, intent diagnosis, prompt quality review, Codex workflow safety, or confirmation-gated learning from real AI coding sessions.

This project is not a hosted eval platform, a prompt collection, or a generic answer grader. It is a practical quality layer for people who use Agents to read projects, edit files, run commands, and carry long-running work.

## Current Status

`intent-quality` is in the v0.3 local candidate stage, with v0.4 P0 diagnosis-quality calibration work underway. The core local loop is usable for project-local diagnosis, fixtures, regression checks, playbook learning, public candidate gating, pending profile-memory suggestions, local eval review metadata, experimental/internal adapter export drafts, and read-only diagnosis calibration fixtures.

The current package version is `0.3.0`.

## Install

Repository:

```text
https://github.com/taiyuli3131/intent-quality
```

Clone and install the Python CLI:

```bash
git clone https://github.com/taiyuli3131/intent-quality.git
cd intent-quality
python -m pip install -e .
```

From a local checkout:

```bash
python -m pip install -e .
```

For local development without installation, use:

```bash
python -m intent_quality.cli --help
```

## Codex Plugin

This repository also includes a Codex plugin manifest and an `intent-quality` skill.

Plugin source:

```text
https://github.com/taiyuli3131/intent-quality.git
```

Skill directory:

```text
https://github.com/taiyuli3131/intent-quality/tree/master/skills/intent-quality
```

After installing the plugin in Codex, use:

```text
Use $intent-quality to check whether this task preserves intent and authorization.
```

The skill guides Codex through local collaboration-quality checks, diagnosis, evals, suggestions, and release verification while preserving the project's confirmation-gated safety model.

## Quick Start

Run the read-only project check:

```bash
python -m intent_quality.cli check
```

Run a focused eval sample:

```bash
python -m intent_quality.cli eval datasets/collaboration-quality.v0.1.yaml --response examples/eval-response-auth-boundary-pass.md --eval-id eval_auth_boundary_direction_001
```

Create a manual diagnosis report:

```bash
python -m intent_quality.cli diagnose --manual --description "The user wanted to discuss direction, but the Agent edited files."
```

Verify Python files compile:

```bash
python -m compileall intent_quality
```

## Why It Exists

Agent collaboration often fails before the code or prose is wrong.

Common failures look like this:

- you wanted to discuss direction, but the Agent edited files;
- old conversation context leaked into a new task;
- the Agent accepted an unsupported premise as fact;
- a request for advice was treated as execution approval;
- a useful failure happened once, but never became a reusable test or habit.

`intent-quality` turns those moments into structured diagnosis, local learning, repeatable eval cases, and optional contribution candidates.

## Use Cases

- Agent collaboration quality checks for Codex and file-capable AI assistants.
- Local-first LLM eval fixtures for authorization, response mode, stale context, and premise validation failures.
- Intent diagnosis for conversations where the Agent misunderstood the user's goal or acted too early.
- Regression testing for prompt, rules, skill, profile, or workflow changes.
- Privacy-preserving contribution review for reusable collaboration-quality cases.

## Core Loop

```text
diagnose real collaboration issues
-> create local casebook entries
-> generate eval samples
-> run repeatable checks
-> review suggestions
-> improve pre-action behavior
-> optionally contribute anonymized cases
```

The first user-facing entry point is `diagnose`.

## What Diagnose Produces

A diagnosis should create both a human-readable Markdown report and a machine-readable YAML file.

The report answers:

- What went wrong in the interaction?
- Was the user's goal preserved?
- Was execution authorized?
- Did old context affect the current task?
- Did the Agent rely on an unsupported premise?
- What should the user and Agent do differently next time?

See [examples/diagnose-report.md](examples/diagnose-report.md) for a report sample.

## What Suggestions Are

Suggestions are reviewable local proposals. They may recommend a learning note, profile change, rule candidate, casebook entry, eval sample, or contribution package.

Suggestions do not mutate local state by default. Anything that changes rules, profiles, datasets, casebooks, or contribution status requires user confirmation.

Profile memory is deliberately narrow in v0.3 P1: diagnosis-derived `profile_update` suggestions are pending, project-local, evidence-backed, rollback-described, and explicitly awaiting user confirmation. They must not become confirmed preferences, global memory, cross-project memory, broad personal memory, or automatic profile edits.

See [examples/suggestion-display.md](examples/suggestion-display.md) for a suggestion display sample.

## Contribution Is Optional

If a diagnosis finds a reusable collaboration issue, `intent-quality` may invite you to create an anonymized contribution candidate.

You can review it, edit it, limit allowed uses, keep it local, skip it, or turn off future prompts. Nothing is uploaded automatically.

See [examples/contribution-invitation.md](examples/contribution-invitation.md) for the lightweight contribution copy.

## Public Samples Are Untrusted By Default

Public case sync is designed to be useful without being dangerous.

The default behavior is:

- fetch or refresh the public index;
- compare public cases with local project patterns;
- run local schema and rubric checks;
- generate suggestions;
- wait for user confirmation before adoption.

Public samples must not automatically change profiles, rules, eval datasets, casebooks, rubrics, or contribution settings.

See [docs/public-sync-contribution-minimal-loop.md](docs/public-sync-contribution-minimal-loop.md) and [public-registry/index.yaml](public-registry/index.yaml) for the first local closed-loop design and sample public index.

Run the read-only sample check with:

```bash
python tools/local_loop_check.py
```

## Safety Model

`intent-quality` is local-first and confirmation-gated.

By default:

- diagnosis writes only diagnosis reports;
- public sync writes only external candidates and pending suggestions;
- contribution creation writes only local pending contribution packages;
- profile memory is represented as pending suggestions only;
- `check`, `eval`, `suggest list`, and contribution review are read-only.

The project must not automatically:

- upload local data;
- submit contribution packages;
- accept public samples;
- apply profile memory;
- mutate rules, datasets, casebooks, rubrics, contribution settings, or accepted local assets.

See [PRIVACY.md](PRIVACY.md) and [SECURITY.md](SECURITY.md) for open-source safety boundaries.

## CLI MVP

This repository includes a minimal local CLI for the first-phase flow.

```bash
intent-quality diagnose --manual
intent-quality diagnose --conversation conversation.md
intent-quality eval datasets/collaboration-quality.v0.1.yaml --response response.md
intent-quality suggest list
intent-quality public fetch
intent-quality public suggest
intent-quality contribute create --diagnosis .intent-quality/diagnoses/diag_YYYYMMDD_NNN.yaml
intent-quality contribute review
intent-quality adapter export datasets/collaboration-quality.v0.1.yaml --format promptfoo
intent-quality check
```

For local development without installing the package, use:

```bash
python -m intent_quality.cli eval datasets/collaboration-quality.v0.1.yaml --response examples/eval-response-auth-boundary-pass.md --eval-id eval_auth_boundary_direction_001
python -m intent_quality.cli public fetch
python -m intent_quality.cli public suggest
python -m intent_quality.cli contribute create --description "Discussion was treated as file update authorization."
python -m intent_quality.cli contribute review
python -m intent_quality.cli adapter export datasets/collaboration-quality.v0.1.yaml --format deepeval
python -m intent_quality.cli check
```

The MVP keeps mutating behavior narrow. `diagnose` writes only diagnosis reports under `.intent-quality/diagnoses/`. `public fetch` writes only the public index and fetch metadata. `public suggest` writes external candidates and pending suggestions only. `contribute create` writes a local pending contribution package only. `adapter export` writes only an optional experimental draft when `--output` is supplied. `check`, `eval`, `suggest list`, and `contribute review` are read-only. No profile, rules, accepted dataset, casebook, rubric, public upload, contribution state change, or profile memory is applied automatically.

`adapter export` can emit experimental/internal draft mappings for `promptfoo`, `deepeval`, and `pydantic-evals`. These files are for inspection and future integration planning only. They do not run external frameworks, do not add core runtime dependencies, do not replace the default heuristic scorer, and do not apply results automatically.

## v0.3 Release Scope

v0.3 keeps the same local-first safety model while adding the user-facing diagnosis and review layers needed for a candidate release:

- diagnosis reports expose finding-level evidence, confidence, premise status, targeted completion questions, expected versus actual mode, authorization scope, learning feedback, and preview-only generated candidates;
- playbook pages cover the core concepts surfaced by diagnosis reports;
- profile memory remains project-local, pending, evidence-backed, rollback-described, and confirmation-gated;
- eval review adds local human-review metadata for `needs_review` outputs, including reviewer notes and calibration notes, without changing the default heuristic scorer;
- adapter export emits experimental/internal draft mappings for Promptfoo, DeepEval, and Pydantic Evals without running those frameworks or making them core runtime dependencies;
- `check` remains read-only and validates the public sync, eval response, eval review, diagnosis quality, diagnosis calibration, profile memory, adapter export, and playbook fixtures.

v0.3 does not add a hosted platform, dashboard, automatic public upload, automatic public-sample adoption, automatic profile/rule/dataset/casebook/rubric/contribution mutation, default LLM-as-judge scoring, or complete semantic evaluation.

See [docs/release-v0.3.md](docs/release-v0.3.md) for release notes and [docs/release-v0.2.md](docs/release-v0.2.md) for the v0.2 reliability baseline.

## v0.4 P0 Diagnosis Calibration

v0.4 P0 adds a synthetic, read-only calibration fixture layer for diagnosis quality.

It checks whether diagnosis-like examples are `ready`, `needs_review`, or `blocked` based on schema coverage, readiness, confidence range, finding structure, premise status, completion questions, authorization scope, privacy/redaction blockers, and candidate-gate blockers.

The calibration layer does not generate or approve real fixtures, write feedback, auto-adopt candidates, add LLM-as-judge scoring, or mutate fixture, candidate, memory, profile, rule, dataset, casebook, rubric, contribution, public, suggestion, or accepted local state.

See [docs/v0.4-diagnosis-quality.md](docs/v0.4-diagnosis-quality.md).

## Diagnose Versus Eval

`diagnose` is for discovery and learning. It studies real usage and explains what happened.

`eval` is for repeatable verification. It checks whether an Agent passes a known collaboration-quality case and whether changes introduce regressions.

The two are connected:

```text
diagnose real issue -> create case -> create eval sample -> run eval -> update suggestions
```

## First-Phase Scope

Included:

- local project diagnosis;
- standardized diagnosis reports;
- local casebook entries;
- eval dataset samples;
- eval review metadata for ambiguous `needs_review` results;
- experimental/internal adapter export drafts;
- public index sync;
- local suggestions;
- anonymized contribution packages;
- Codex skill rules for pre-action prevention;
- project/user collaboration profile options;
- learning feedback and playbook pages.

Not included in the first phase:

- hosted accounts;
- full eval dashboards;
- automatic public uploads;
- automatic mutation of local rules, profiles, datasets, or casebooks;
- enterprise governance workflows;
- default cross-project global history analysis.

## Local Project Shape

First-phase local state is expected to live under `.intent-quality/`.

```text
.intent-quality/
  diagnoses/
  cases/
  datasets/
  rubrics/
  suggestions/
  contributions/
  public/
  profile/
  playbook/
```

See [SCHEMAS.md](SCHEMAS.md) for the proposed YAML structures.

## Learning Layer

The product teaches better Agent collaboration in two ways:

- short feedback inside diagnosis reports;
- local playbook concept pages for recurring topics.

Current local playbook pages:

- [authorization boundary](docs/playbook/authorization-boundary.md)
- [response mode](docs/playbook/response-mode.md)
- [context pollution](docs/playbook/context-pollution.md)
- [premise validation](docs/playbook/premise-validation.md)
- [diagnose versus eval](docs/playbook/diagnose-vs-eval.md)
- [public sample trust](docs/playbook/public-sample-trust.md)
- [suggestions and confirmation](docs/playbook/suggestions-and-confirmation.md)
- [contribution privacy](docs/playbook/contribution-privacy.md)

## Current Project Documents

- [PROJECT-INFO.md](PROJECT-INFO.md): product overview and document map.
- [PRODUCT-SPEC.md](PRODUCT-SPEC.md): active product specification.
- [ACCEPTANCE.md](ACCEPTANCE.md): public acceptance summary.
- [SCHEMAS.md](SCHEMAS.md): YAML-first local file schemas.
- [DIAGNOSE-EVAL-FLOW.md](DIAGNOSE-EVAL-FLOW.md): operational flow.
- [docs/release-v0.3.md](docs/release-v0.3.md): v0.3 release notes.
- [docs/v0.3-roadmap.md](docs/v0.3-roadmap.md): public v0.3 roadmap.
- [docs/v0.4-diagnosis-quality.md](docs/v0.4-diagnosis-quality.md): v0.4 P0 diagnosis calibration scope.

Historical notes are kept as context, but the active product shape is defined by the files above.

## Contributing

Contributions are welcome when they preserve the local-first safety model.

Before proposing changes, run:

```bash
python -m intent_quality.cli check
python -m compileall intent_quality
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT. See [LICENSE](LICENSE).
