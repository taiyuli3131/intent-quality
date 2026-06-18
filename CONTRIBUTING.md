# Contributing

Thanks for considering a contribution to `intent-quality`.

This project is a local-first Agent collaboration quality system. Contributions should preserve the safety model: suggestions and generated candidates may be created for review, but profile, rule, dataset, casebook, rubric, contribution, and public-sample changes must not be applied automatically.

## Useful Contribution Areas

- Diagnosis quality fixtures and report examples.
- Collaboration-quality eval cases.
- Playbook pages for recurring Agent collaboration concepts.
- Public candidate safety fixtures.
- Documentation that makes local-first behavior clearer.
- Small CLI improvements that keep mutation boundaries explicit.

## Before Opening A Change

Run:

```bash
python -m intent_quality.cli check
python -m compileall intent_quality
```

The check command must remain read-only. It should not modify rules, profiles, datasets, casebooks, candidates, suggestions, submissions, rubrics, contribution state, or public-sample adoption state.

## Contribution Rules

- Keep examples synthetic or anonymized.
- Do not include private repository paths, API keys, tokens, emails, customer data, proprietary excerpts, or personal identifiers.
- Mark user claims as user-stated or unverified unless evidence is included.
- Do not add automatic mutation of profile, rules, datasets, casebooks, rubrics, contribution settings, or public samples.
- Do not describe the current marker-based scorer as a complete semantic evaluator.
- Do not add hosted platform, account, cloud sync, dashboard, or upload behavior without an accepted roadmap update.

## Suggested PR Shape

- Explain the collaboration-quality issue being addressed.
- List changed files.
- Include fixture coverage when behavior changes.
- State whether the change is product delivery, internal test coverage, or documentation.
- Include the output of the two verification commands above.

## License

By contributing, you agree that your contribution will be licensed under the MIT License.
