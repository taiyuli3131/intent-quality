# Intent Quality Product Spec

> Updated: 2026-06-16
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
- automatic local rule/profile/dataset mutation;
- enterprise governance workflows;
- default cross-project global history analysis.

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
