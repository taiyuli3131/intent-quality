# Security Policy

`intent-quality` is designed as a local-first tool. It should not upload local project data, profile data, contribution packages, public-sample adoption decisions, or diagnosis reports automatically.

## Reporting Security Issues

If this repository is published on a hosting platform, please report security issues through the repository's private security advisory channel when available. If no private channel exists yet, avoid posting sensitive details publicly; open a minimal issue asking for a private contact path.

## Security Boundaries

The project should preserve these boundaries:

- Public samples are untrusted by default.
- Public sync may fetch or stage candidates, but adoption remains user-confirmation gated.
- Contribution package generation is not submission authorization.
- Profile memory suggestions are pending, project-local, and review-only.
- `check`, `eval`, `suggest list`, and contribution review flows should remain read-only.
- No command should silently upload, publish, or apply local state changes.

## Sensitive Data

Do not include the following in issues, examples, fixtures, public candidates, or contribution packages:

- API keys, tokens, credentials, or private keys.
- Private filesystem paths.
- Personal email addresses or identifiers.
- Proprietary conversation excerpts.
- Customer, employer, or repository data that has not been anonymized.

## Verification

Before publishing or reviewing a security-sensitive change, run:

```bash
python -m intent_quality.cli check
python -m compileall intent_quality
```
