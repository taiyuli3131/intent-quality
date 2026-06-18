# Playbook: Contribution Privacy

## Concept

Contribution privacy is the boundary between a useful reusable collaboration case and private project material.

Contribution packages are local drafts until the user reviews them and explicitly authorizes submission.

## Common Failure

A diagnosis finds a reusable issue and the system treats package generation as publication approval.

That is not safe. A local contribution package may still contain private paths, repository names, personal identifiers, proprietary excerpts, or too much verbatim conversation.

## Better Agent Behavior

The Agent should keep contribution steps separate:

```text
I can generate a local anonymized contribution candidate for review. It will not be submitted unless you authorize submission.
```

The privacy report should show what was generalized or redacted and what still needs review.

## Privacy Review Signals

Check for:

- private filesystem paths;
- repository URLs;
- secrets or tokens;
- personal identifiers;
- proprietary file contents;
- long verbatim logs;
- permission for documentation examples.

Documentation example permission should default to off because it has broader visibility.

## Healthy Contribution Flow

```text
diagnosis completed
-> local package generated
-> anonymization and privacy report
-> user review
-> allowed uses selected
-> submission only after explicit authorization
```

## Related Concepts

- suggestions and confirmation
- public sample trust
- authorization boundary
- diagnose versus eval
