# Playbook: Response Mode

## Concept

Response mode is the kind of help the user is asking for: discussion, advice, draft, verification, execution, or persistence.

For file-capable Agents, mode is a safety boundary. A good answer in discussion mode can be a bad action in execution mode.

## Common Failure

The user asks:

```text
Tell me whether this plan is sound.
```

The Agent acts as if execution was requested:

```text
I rewrote the plan and updated the project files.
```

The Agent answered the broader topic, but not the requested mode.

## Better Agent Behavior

The Agent should name the mode when risk is material:

```text
I'll keep this as verification and will not edit files.
```

When switching modes would help, ask first:

```text
I can turn this into a patch after the review. Do you want that now?
```

## Better User Prompting

Use mode words when a task could be ambiguous:

```text
Discussion only: compare these options, no edits.
```

```text
Draft in chat first, then wait.
```

```text
Execution allowed: update the file and run the check.
```

## Diagnosis Signals

Possible response-mode mismatch:

- advice is treated as approval to change files;
- verification becomes implementation;
- a draft is persisted without confirmation;
- a discussion request creates durable local state.

Healthy behavior:

- the Agent preserves the requested mode;
- mode changes are explicit;
- execution and persistence require clear authorization;
- the response fits the user's current phase of work.

## Related Concepts

- authorization boundary
- suggestions and confirmation
- context pollution
- diagnose versus eval
