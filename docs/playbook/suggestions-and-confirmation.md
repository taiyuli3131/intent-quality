# Playbook: Suggestions And Confirmation

## Concept

Suggestions are reviewable proposals. They may recommend a learning note, profile update, rule candidate, casebook entry, eval sample, contribution package, or public-sample action.

A suggestion is not authorization to apply itself.

## Common Failure

The system finds a useful pattern and immediately changes local behavior:

```text
I updated your project profile to require confirmation before edits.
```

Even if the update is reasonable, it crosses from recommendation into mutation.

## Better Agent Behavior

The Agent should show a small proposal first:

```text
I can create a pending suggestion with source evidence, impact scope, rollback notes, and confirmation state.
```

For any mutating action, the default state should be pending or preview-only.

## What Good Suggestions Include

- source and evidence;
- target files or local state;
- proposed change summary;
- impact scope;
- non-goals;
- rollback plan;
- confirmation state;
- whether the action is reversible.

## Confirmation Boundary

User confirmation is required before applying changes to:

- profiles or rules;
- datasets or casebooks;
- rubrics;
- contribution submission or settings;
- accepted public samples;
- other durable project state.

## Related Concepts

- authorization boundary
- public sample trust
- contribution privacy
- response mode
