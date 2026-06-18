# Playbook: Diagnose Versus Eval

## Concept

Diagnose and eval answer different questions.

`diagnose` studies a real interaction to explain what happened and what to learn. `eval` runs a known case to check whether an Agent behavior passes or regresses.

## When To Diagnose

Use diagnosis after a confusing or risky interaction:

- the Agent may have misunderstood the goal;
- a mode or authorization boundary may have been crossed;
- old context may have polluted the task;
- an unsupported premise may have shaped the answer;
- the user wants learning feedback or candidate cases.

Diagnosis can be lower confidence when the input is incomplete. That is acceptable if the report names missing information.

## When To Eval

Use eval when the scenario is known enough to test repeatedly:

- a case has clear expected behavior;
- required and forbidden observations can be listed;
- a response can be scored against a rubric;
- the result should catch regressions over time.

Eval is useful for regression checks, but the current scorer is heuristic. It should not be treated as a complete semantic judge.

## Good Flow

```text
diagnose real issue
-> create reviewable case candidate
-> create eval sample candidate
-> run eval later for regression checking
```

Generated candidates stay preview-only until the user confirms adoption.

## Common Failure

Using eval too early can flatten a messy real issue into a brittle test.

Using diagnose too late can leave recurring failures as anecdotes instead of reusable cases.

## Related Concepts

- response mode
- premise validation
- suggestions and confirmation
- contribution privacy
