# intent-quality

`intent-quality` is a local-first collaboration quality system for Codex and file-capable Agent users.

It helps you diagnose, test, and improve how an Agent understands your goal, respects authorization boundaries, avoids stale context, validates premises, and chooses the right response mode before taking action.

This project is not a hosted eval platform, a prompt collection, or a generic answer grader. It is a practical quality layer for people who use Agents to read projects, edit files, run commands, and carry long-running work.

## Why It Exists

Agent collaboration often fails before the code or prose is wrong.

Common failures look like this:

- you wanted to discuss direction, but the Agent edited files;
- old conversation context leaked into a new task;
- the Agent accepted an unsupported premise as fact;
- a request for advice was treated as execution approval;
- a useful failure happened once, but never became a reusable test or habit.

`intent-quality` turns those moments into structured diagnosis, local learning, repeatable eval cases, and optional contribution candidates.

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
intent-quality check
```

For local development without installing the package, use:

```bash
python -m intent_quality.cli eval datasets/collaboration-quality.v0.1.yaml --response examples/eval-response-auth-boundary-pass.md --eval-id eval_auth_boundary_direction_001
python -m intent_quality.cli public fetch
python -m intent_quality.cli public suggest
python -m intent_quality.cli contribute create --description "Discussion was treated as file update authorization."
python -m intent_quality.cli contribute review
python -m intent_quality.cli check
```

The MVP keeps mutating behavior narrow. `diagnose` writes only diagnosis reports under `.intent-quality/diagnoses/`. `public fetch` writes only the public index and fetch metadata. `public suggest` writes external candidates and pending suggestions only. `contribute create` writes a local pending contribution package only. `check`, `eval`, `suggest list`, and `contribute review` are read-only. No profile, rules, accepted dataset, casebook, rubric, public upload, or contribution state change is applied automatically.

## v0.2 Roadmap

v0.1 proves the local loop. v0.2 should make that loop more inspectable, stricter, and more useful on real Agent work.

Planned focus:

- stronger diagnosis evidence, confidence, and missing-information handling;
- eval results with explicit evidence mapping, blocking failures, dimension rationales, and regression-friendly result files;
- real public candidate content staging after index discovery, with hash checks where available;
- stricter schema, rubric, privacy, poisoning, and relevance checks before suggestions are generated;
- suggestion preview/apply/rollback records for any local mutation;
- clearer contribution privacy review, allowed-use controls, submission gates, and withdrawal records;
- more playbook pages for response mode, context pollution, premise validation, public sample trust, diagnose versus eval, suggestions, and contribution privacy.

v0.2 does not change the safety model:

- no hosted accounts;
- no full dashboard;
- no automatic public uploads;
- no automatic public-sample adoption;
- no automatic profile, rule, dataset, casebook, rubric, or contribution mutation.

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
- adapter-ready eval structure;
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

See [docs/playbook/authorization-boundary.md](docs/playbook/authorization-boundary.md) for a first concept page draft.

## Current Project Documents

- [PROJECT-INFO.md](PROJECT-INFO.md): product overview and document map.
- [PRODUCT-SPEC.md](PRODUCT-SPEC.md): active product specification.
- [SCHEMAS.md](SCHEMAS.md): YAML-first local file schemas.
- [DIAGNOSE-EVAL-FLOW.md](DIAGNOSE-EVAL-FLOW.md): operational flow.

Historical notes are kept as context, but the active product shape is defined by the files above.
