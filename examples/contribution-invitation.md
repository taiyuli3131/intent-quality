# Contribution Invitation Copy

## Default Prompt

This diagnosis found a collaboration issue that may help other Codex users.

You can generate an anonymized contribution candidate for the public case pool. This is optional. You can review, edit, limit allowed uses, skip it, or turn off future prompts.

```text
[Generate candidate] [Keep local only] [Skip] [Turn off prompts]
```

## Review Screen Copy

Before anything is submitted, you can review the anonymized package.

Included:

- collaboration failure category;
- shortened scenario;
- expected Agent behavior;
- actual failure mode;
- teaching notes;
- privacy report;
- allowed-use settings.

Not included by default:

- private file contents;
- project secrets;
- personal identifiers;
- full conversation logs;
- repository URLs;
- documentation-example permission.

## Allowed Uses

```yaml
allowed_uses:
  public_candidate_pool: true
  eval_dataset: true
  docs_example: false
```

Recommended default:

- public candidate pool: on
- eval dataset candidate: on
- documentation example: off

Documentation example permission should stay off by default because it has broader visibility than a structured case candidate.

## Privacy Confirmation

```text
I reviewed the anonymized candidate and allowed-use settings.
```

```text
[Submit candidate] [Save as pending] [Edit package] [Withdraw]
```

## Dismissal Copy

No problem. This diagnosis will stay local. You can generate a contribution candidate later from the diagnosis report if you want to.

## Disabled Prompt Copy

Contribution prompts are now off for this project. You can re-enable them in the local collaboration profile.
