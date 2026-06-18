# Playbook: Premise Validation

## Concept

Premise validation is the habit of labeling important claims before using them to decide what to do.

A premise can be user-stated, inferred, assumed, verified, or unknown. The label matters most when the claim would change files, rules, profiles, datasets, casebooks, contributions, or public-sample decisions.

## Common Failure

The user says:

```text
The old approach is clearly worse. Update the docs around the new approach.
```

The Agent treats the claim as verified:

```text
Since the old approach is worse, I removed it from the docs.
```

The problem is not that the claim is false. The problem is that the Agent used an unverified premise as if it had been checked.

## Better Agent Behavior

The Agent should preserve the premise label:

```text
I'll treat "the old approach is worse" as a user-stated premise unless you want me to verify it first.
```

If verification would materially change the outcome, the Agent should ask or check:

```text
Do you want a quick evidence check before I rewrite the docs around that claim?
```

## Better User Prompting

Say whether the premise is settled or should be checked:

```text
Assume for this task that the new approach is better; do not re-litigate it.
```

Or:

```text
First verify whether the new approach is actually better before suggesting edits.
```

## Diagnosis Signals

Possible premise validation issue:

- a central claim is unsupported but drives the action;
- the Agent upgrades an assumption into a fact;
- evidence is missing for a decision-critical conclusion;
- verification was available but skipped.

Healthy behavior:

- premise status is visible;
- assumptions are named;
- verification questions are targeted;
- the Agent does not over-ask when the user explicitly authorizes an assumption.

## Related Concepts

- context pollution
- response mode
- authorization boundary
- diagnose versus eval
