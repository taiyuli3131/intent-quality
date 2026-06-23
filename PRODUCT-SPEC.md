# Intent Quality Product Spec

> Updated: 2026-06-22
> Product shape: local-first Agent collaboration quality system for Codex users

## 1. Product Definition

`intent-quality` helps Codex users improve Agent collaboration quality before and after action.

It focuses on five recurring failure classes:

- goal misunderstanding;
- unauthorized execution or persistence;
- context pollution from long conversations or old project assumptions;
- unsupported premise acceptance;
- wrong response mode, such as treating discussion as file-edit authorization.

The product should help the user both complete tasks more safely and become a better Agent user over time.

## 2. First-Phase Scope

First phase includes:

- local project diagnosis;
- standardized diagnosis reports;
- local casebook entries;
- eval dataset samples;
- lightweight eval execution and adapter-ready structure;
- local eval review metadata for ambiguous `needs_review` outputs;
- experimental/internal adapter export drafts;
- public case index sync;
- local suggestions;
- anonymized contribution packages;
- Codex skill rules for pre-action prevention;
- project/user collaboration profile options;
- learning feedback and playbook pages.

First phase excludes:

- hosted account system;
- full eval dashboard;
- automatic public uploads;
- automatic local profile, rule, dataset, casebook, rubric, contribution, suggestion, or accepted-asset mutation;
- external eval frameworks as core runtime dependencies;
- default LLM-as-judge scoring;
- enterprise governance workflows;
- default cross-project global history analysis.

## 2.1 Version Roadmap

v0.1 establishes the local MVP:

- diagnosis report generation;
- local cases and eval datasets;
- heuristic eval scoring;
- public index fetch and suggestion generation;
- local pending contribution packages;
- read-only safety checks;
- user-facing examples and initial playbook pages.

v0.2 strengthens the same local-first loop rather than changing the product category.

v0.2 is a reliability hardening version, not a platformization version. It improves public sync gates and eval scorer output while keeping the product local, file-based, and confirmation-driven.

v0.2 reliability scope:

- public sync validates index policy before use;
- public sync fetches or stages candidate content only through a local gate;
- candidate content is checked against `content_sha256` when listed by the index;
- schema, rubric, privacy, poisoning, and relevance checks block unsafe candidates;
- generated public-sync suggestions remain pending and require confirmation;
- eval output records stable result IDs, observation groups, failure codes, evidence, marker matches, dimension rationales, and `needs_review` cases;
- the scorer is explicitly described as heuristic marker-based regression scoring, not complete semantic evaluation.

v0.2 remains out of scope:

- hosted accounts;
- full dashboards;
- automatic public uploads;
- automatic public-sample adoption;
- automatic profile, rule, dataset, casebook, rubric, or contribution mutation;
- a complete semantic evaluator;
- enterprise governance workflows.

v0.3 turns the reliable v0.2 loop into a candidate-ready local workflow by improving diagnosis quality, learning support, local profile suggestions, eval review, and adapter-ready output without changing the product category.

v0.3 scope:

- diagnosis reports include finding-level evidence, confidence, premise status, targeted completion questions, expected versus actual mode, authorization scope, learning feedback, and preview-only generated candidates;
- playbook pages cover the concepts used by diagnosis learning feedback;
- local profile memory appears only as pending, project-local, evidence-backed suggestions with confirmation state and rollback notes;
- eval review records local human-review status, reviewer notes, review decisions, and false-positive / false-negative calibration notes for `needs_review` outputs;
- adapter export emits experimental/internal draft mappings for Promptfoo, DeepEval, and Pydantic Evals;
- read-only checks validate public sync, eval responses, eval review, diagnosis quality, profile memory, adapter export, and playbook coverage.

v0.3 remains out of scope:

- hosted accounts or dashboards;
- automatic public upload or public-sample adoption;
- automatic profile, rule, dataset, casebook, rubric, contribution, suggestion, or accepted-asset mutation;
- default LLM-as-judge scoring;
- complete semantic evaluation;
- external eval frameworks as core runtime dependencies.

v0.4 P0 adds diagnosis calibration fixtures for the diagnosis-quality gate without changing the product category.

v0.4 P0 scope:

- synthetic read-only diagnosis calibration fixtures;
- fixture schema checks for readiness, required fields, finding coverage, confidence ranges, premise status, completion questions, authorization scope, privacy/redaction blockers, and candidate-gate blockers;
- `check` integration with protected snapshots to confirm no protected local assets are modified.

v0.4 P0 remains out of scope:

- real fixture generation or approval;
- feedback writing;
- automatic candidate adoption;
- hosted dashboards or platform behavior;
- default LLM-as-judge scoring;
- complete semantic evaluation claims;
- automatic profile, rule, dataset, casebook, rubric, contribution, public state, suggestion, candidate, or accepted-asset mutation.

## 3. Diagnose And Eval

`diagnose` is for real user work. It answers:

- What went wrong in this Agent interaction?
- Was the goal preserved?
- Was execution authorized?
- Did old context affect the current task?
- Did the Agent treat an unverified premise as fact?
- What should the user and Agent do differently next time?

`eval` is for repeatable verification. It answers:

- Does an Agent pass a known collaboration-quality case?
- Did a rule change reduce or increase failures?
- Does the Agent respect authorization boundaries?
- Does the Agent avoid goal replacement and context pollution?

Eval review is a local human-review layer for ambiguous `needs_review` results. It records reviewer notes and calibration metadata, but it does not change the default heuristic scorer, apply results, or mutate datasets, rubrics, profiles, rules, casebooks, suggestions, or contributions.

Adapter export is an experimental/internal bridge for future external-tool comparison. It can draft Promptfoo, DeepEval, and Pydantic Evals mappings, but it does not run those frameworks, make them required dependencies, replace the heuristic scorer, or apply any result.

The preferred flow is:

```text
diagnose real issue -> create case -> create eval sample -> run eval -> update suggestions
```

## 4. Before-Action And After-Action Loops

The system needs both prevention and diagnosis.

Before-action loop:

- detect the intended mode: discussion, advice, draft, verification, execution, or persistence;
- identify the real goal;
- classify goal, path, premise, and permission risks;
- check whether file writes, memory updates, or rule changes are authorized;
- ask only the minimum decisive questions;
- define acceptance criteria and verification route when useful.

After-action loop:

- inspect a conversation, project, or manual report;
- identify actual failure modes;
- cite evidence;
- assign confidence;
- ask for missing information when needed;
- generate case, eval, profile, and contribution candidates.

## 5. Diagnose Report Requirements

Every diagnosis should include:

- summary of primary and secondary issues;
- expected interaction state versus actual Agent behavior;
- goal alignment check;
- authorization boundary check;
- context pollution check;
- premise validation check;
- findings with evidence and confidence;
- missing information and targeted follow-up questions;
- learning feedback;
- generated candidate actions.

Manual inputs can produce useful structural analysis, but conclusions must be confidence-scored. If the input is incomplete, the report should separate:

- what can be judged now;
- what cannot be judged;
- which 2-4 questions would improve accuracy most.

Diagnosis calibration fixtures are separate from real diagnosis reports. They are synthetic check inputs used to verify whether diagnosis-quality gates classify examples as `ready`, `needs_review`, or `blocked`.

## 6. Public Library And Trust Model

Public case sync is automated, but public samples are not trusted by default.

Default behavior:

- check the public index weekly;
- download or refresh the public index;
- match new cases against local project profile and diagnosis history;
- run local Schema + Rubric checks;
- generate suggestions with relevance explanations;
- wait for user confirmation before local adoption.

Public samples must not automatically:

- modify profile files;
- modify rules;
- enter local eval datasets;
- enter local casebooks;
- override rubrics;
- change contribution settings.

External samples can become local assets only after user confirmation.

## 7. Contribution Flow

Contribution is optional and lightweight.

After a diagnosis finds a reusable issue, the report may show a short contribution invitation:

```text
This diagnosis found a collaboration issue that may help other Codex users.

You can generate an anonymized contribution candidate for the public case pool. This is optional. You can review, edit, limit allowed uses, skip it, or turn off future prompts.
```

Contribution flow:

```text
diagnosis completed
-> reusable issue detected
-> optional prompt at report end
-> local contribution package generated
-> anonymization and privacy report
-> user review and allowed-use selection
-> public candidate submission only after confirmation
```

Allowed-use options:

- public candidate pool;
- eval dataset candidate;
- documentation example.

Documentation example permission should default to off because it has broader visibility.

## 8. User Learning And Profile

The product should guide the user to become a better Agent user.

Learning has two layers:

- short feedback inside diagnosis reports;
- local playbook pages for concepts such as authorization boundary, context pollution, premise validation, response mode, public sample trust, and diagnose versus eval.

Profiles should be limited to Agent collaboration behavior, not broad personality records.

Supported profile scopes:

- no memory;
- project profile;
- collaboration pattern profile;
- future global profile.

Profile updates are suggestions by default and require user confirmation.

## 9. Gradual Adoption Principle

The first usable version should keep the core workflow simple:

1. Preserve the user's real outcome.
2. Identify information that materially changes the answer.
3. Separate goal risk, path risk, premise risk, and permission risk.
4. Ask decisive questions or proceed with labeled assumptions.
5. Define acceptance criteria and verification when useful.

Memory updates, domain overlays, automated regression tests, public sync, and adapter integrations should be added progressively after the core loop works across enough real cases.

## 10. Future Evaluation Direction

Future tests should compare:

- ordinary model behavior;
- prompt-only clarification behavior;
- post-output evaluation behavior;
- `intent-quality` pre-action and post-action behavior.

For v0.2, eval should focus on inspectable evidence and regression usefulness before attempting a broad semantic evaluator.

v0.2 eval outputs should include:

- the evaluated case and rubric versions;
- observed evidence from the Agent response;
- passed and failed required observations;
- forbidden observations and blocking failures;
- failure codes;
- matched semantic markers or violation markers when available;
- dimension scores with short rationales;
- `needs_review` when marker-based scoring is insufficient for a hard case near the pass threshold;
- a stable result file suitable for comparing later runs.

v0.2 scorer language must stay restrained: it can support regression checks and expose evidence, but it must not claim to fully understand intent, replace human review, or provide general semantic evaluation.

The automatic update loop should eventually:

1. collect real and public test samples;
2. run responses against collaboration rubrics;
3. detect regressions such as over-questioning, goal replacement, unsupported premise acceptance, unauthorized execution, or missed verification;
4. generate candidate documentation, rubric, profile, or test updates;
5. request user or maintainer approval;
6. rerun affected tests after updates.

## 11. Quality Principles

- The system should not ask more questions by default.
- The system should not treat risk detection as an accusation.
- The system should not replace a legitimate user goal with a safer goal.
- The system should not mutate rules, memory, casebooks, datasets, or contributions without confirmation.
- The system should be able to explain why a diagnosis or suggestion was made.
- The user should always be able to skip, reject, edit, or withdraw contribution-related actions.
- Public candidate adoption, suggestion application, contribution submission, profile/rule changes, and accepted dataset/casebook changes require user confirmation.
