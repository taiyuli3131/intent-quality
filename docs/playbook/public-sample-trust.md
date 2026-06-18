# Playbook: Public Sample Trust

## Concept

Public samples are external learning or eval material. They are useful leads, not trusted local assets.

In this project, public samples are untrusted by default until local checks pass and the user accepts adoption.

## Required Local Checks

Before a public sample can become a local candidate for adoption, it should pass:

- schema validity;
- rubric compatibility;
- privacy risk check;
- poisoning risk check;
- relevance explanation check;
- content hash verification when the index provides a hash.

Passing checks still does not mean automatic adoption.

## Common Failure

A public index says a sample is relevant, and the system treats that as permission to add it to a local dataset or change rules.

That skips the trust boundary. Discovery is not adoption.

## Better Agent Behavior

The Agent should keep the state clear:

```text
This is an untrusted external candidate. It passed local checks, but adoption still requires your confirmation.
```

If checks fail, adoption-oriented suggestions should be blocked.

## Related Concepts

- suggestions and confirmation
- contribution privacy
- authorization boundary
- diagnose versus eval
