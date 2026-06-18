# intent-quality v0.2 Release Summary

> Status: `v0.2 candidate accepted`
> Date: 2026-06-18
> Tag: `v0.2-candidate-accepted`

## Summary

v0.2 is a reliability hardening release for the local Agent collaboration quality loop.

It does not turn `intent-quality` into a hosted platform, dashboard, or full semantic eval system. The release strengthens the two main gaps left by v0.1:

- public sync now checks real candidate content before adoption-oriented suggestions can be generated;
- eval scoring now produces more inspectable regression output for collaboration-quality cases.

## Accepted Baselines

- `1dcc977`: v0.2-alpha public sync reliability baseline.
- `ee050c9`: v0.2-beta scorer reliability baseline.
- `fb927ff`: v0.2 candidate readiness documentation.
- `1e8b414`: v0.2 candidate acceptance record.

## Public Sync Reliability

Public sync now:

- validates public index policy hints;
- fetches or stages candidate content through local gates;
- verifies `content_sha256`;
- parses candidate YAML before generating suggestions;
- checks schema and rubric compatibility;
- blocks privacy flags, poisoning flags, prompt-injection language, and auto-apply attempts;
- writes only untrusted external candidates and pending suggestions.

Public samples remain untrusted until the user explicitly accepts them.

## Eval Scorer Reliability

Eval scoring now reports:

- stable result IDs;
- `pass`, `fail`, and `needs_review` status;
- passed, missing, forbidden, and blocking observations;
- failure codes;
- evidence excerpts and matched markers;
- dimension rationales;
- scorer limitations.

The scorer is still heuristic and marker-based. It is useful for repeatable regression checks, but it is not a complete semantic evaluator.

## Fixtures And Checks

`intent-quality check` remains read-only and now covers:

- public index validation;
- public case validation;
- external candidates;
- pending suggestions;
- contribution packages;
- public sync fixtures;
- eval response fixtures.

The v0.2 eval fixtures cover five core collaboration risks:

- authorization boundary;
- context pollution;
- advice-only premature execution;
- unverified premise handling;
- growth-goal preservation.

## Safety Model

v0.2 keeps the same safety model:

- no hosted account system;
- no full dashboard;
- no automatic public upload;
- no automatic public-sample adoption;
- no automatic profile, rule, dataset, casebook, rubric, or contribution mutation;
- no full semantic evaluator claim.

All local adoption, suggestion application, contribution submission, profile/rule changes, and accepted dataset/casebook changes require user confirmation.

## Next Step

The next phase should begin with v0.3 planning. It should decide priorities before implementation, with special care not to dilute the local-first product shape.
