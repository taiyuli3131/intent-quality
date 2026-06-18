# Playbook: Context Pollution

## Concept

Context pollution happens when old, unrelated, or lower-quality context influences the current Agent task without being checked against the user's present goal.

Long-running Codex work benefits from memory and continuity, but only when the Agent can tell what is still relevant.

## Common Failure

The user starts a new scoped task:

```text
Ignore the previous direction discussion. Review this file only.
```

The Agent still uses an earlier assumption:

```text
I updated the roadmap to match the marketing plan we discussed earlier.
```

The Agent may be using real history, but it is using it outside the current scope.

## Better Agent Behavior

The Agent should treat explicit topic switches as scope resets:

```text
I'll use only the file you named and will not carry over the earlier direction discussion unless you ask me to.
```

If older context seems useful, the Agent should label it:

```text
There is a prior assumption that may matter, but I will treat it as unverified for this task.
```

## Better User Prompting

Reset scope directly when continuity is risky:

```text
For this task, ignore earlier positioning discussions and use only the current README.
```

Name allowed context when continuity is useful:

```text
Use the v0.3 roadmap as context, but do not use older v0.2 planning notes.
```

## Diagnosis Signals

Possible context pollution:

- old project direction appears in a new task without being requested;
- the Agent cites prior conversation as current fact;
- stale assumptions change the requested outcome;
- a scope reset is ignored.

Healthy behavior:

- the Agent states which context it is using;
- stale context is treated as a possible lead, not proof;
- explicit resets are respected;
- unclear continuity is turned into a small question.

## Related Concepts

- authorization boundary
- premise validation
- response mode
- diagnose versus eval
