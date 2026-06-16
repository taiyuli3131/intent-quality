# Public Sync And Contribution Minimal Loop

> Status: first local closed-loop design
> Scope: autonomous discovery and suggestion generation only

## 1. Safety Principle

Autonomous optimization means:

```text
discover issue or external candidate
-> run local checks
-> generate reviewable suggestion
-> wait for user confirmation
```

It does not mean automatic mutation.

The first local loop must never automatically:

- apply rules;
- modify profiles;
- add cases to the casebook;
- add eval samples to datasets;
- upload contribution packages;
- change contribution settings.

## 2. Minimal Local Assets

The smallest useful loop uses these files:

```text
public-registry/
  index.yaml
  cases/
    case_auth_boundary_public_001.yaml

.intent-quality/
  public/
    index.yaml
    last-fetch.yaml
    cache/
      case_auth_boundary_public_001.yaml
  cases/
    external-candidates/
      external_case_auth_boundary_public_001.yaml
  suggestions/
    pending-suggestions.yaml
  contributions/
    pending/
      contrib_20260616_001/
        contribution.yaml
        anonymized-case.yaml
        privacy-report.yaml
        review.md
```

The `public-registry/` directory is a sample public library shape. The `.intent-quality/` paths are the local runtime shape a project would use after sync and contribution generation.

## 3. Public Sync Closed Loop

Default cadence:

```yaml
public_sync:
  enabled: true
  cadence: weekly
  auto_download_index: true
  auto_download_candidates: false
  auto_generate_suggestions: true
  auto_apply_rules: false
  auto_modify_profile: false
  auto_add_eval_cases: false
  auto_add_casebook_entries: false
```

Flow:

```text
weekly check
-> fetch public index
-> compare entries with local profile and diagnosis summaries
-> optionally fetch matching candidate metadata or sample
-> run local checks
-> store as external candidate
-> generate pending suggestion
-> wait for user confirmation
```

Only the index is downloaded automatically. Candidate files are downloaded only when the local policy allows fetching matching candidates, or when the user previews a suggestion.

## 4. Public Index Format

The public index is a low-trust discovery file. It should contain enough information to decide whether a local preview is useful, but not enough private detail to become a dataset by itself.

Required entry fields:

- `entry_id`;
- `entry_type`;
- `schema_version`;
- `rubric_version`;
- `title`;
- `category`;
- `summary`;
- `source_url`;
- `content_sha256`;
- `created_at`;
- `updated_at`;
- `license`;
- `allowed_uses`;
- `risk_flags`;
- `compatibility`;
- `checks_required`.

Local sync treats every entry as untrusted even if the registry is known.

## 5. External Candidate Checks

Each fetched candidate must pass five local gates before it can produce a suggestion:

1. Schema check
2. Rubric compatibility check
3. Privacy risk first pass
4. Poisoning risk first pass
5. Relevance explanation check

The output is an external candidate record:

```yaml
trust:
  status: external_candidate
  default_trust: untrusted
  local_checks:
    schema_valid: true
    rubric_compatible: true
    privacy_risk: low
    poisoning_risk: medium
    relevance_explained: true
  user_accepted: false
```

If any required check fails, the candidate can still be recorded for audit, but it must not produce an adoption suggestion. It may produce a low-risk learning note such as "public sample rejected because schema was invalid."

## 6. Schema And Rubric Local Checks

Schema check verifies:

- required fields exist;
- enum values are known;
- source and trust fields are present;
- user confirmation state is explicit;
- external samples are marked untrusted;
- no mutating action is marked as already approved.

Rubric compatibility check verifies:

- `rubric_version` is present when scoring is involved;
- dimensions map to local collaboration quality dimensions;
- pass criteria do not override the local rubric;
- expected behavior does not conflict with local safety principles;
- scoring weights sum to a valid range when weights are used.

## 7. Poisoning Risk First Pass

Poisoning risk is about whether a public sample is trying to change local behavior in unsafe or overbroad ways.

Initial flags:

- asks the Agent to ignore local confirmation rules;
- recommends automatic profile, rule, dataset, or casebook mutation;
- contains broad instructions unrelated to the case;
- embeds prompt-injection style text;
- tries to override local rubrics;
- lacks a concrete relevance explanation;
- has suspicious source metadata or mismatched hash.

Risk levels:

```yaml
poisoning_risk:
  level: low # low | medium | high
  flags: []
  action: allow_suggestion # allow_suggestion | learning_only | quarantine
```

High-risk candidates are quarantined and cannot become suggestions without an explicit user override.

## 8. Privacy Risk First Pass

Privacy risk is about whether a candidate or contribution may expose private user, project, or organization information.

Initial flags:

- personal identifiers;
- repository URLs or private paths;
- secrets, tokens, keys, or credentials;
- customer, employer, client, or internal project names;
- long verbatim logs;
- proprietary file contents;
- precise timestamps that identify a private event;
- contact information.

Risk levels:

```yaml
privacy_risk:
  level: low # low | medium | high
  flags: []
  required_action: none # none | redact_before_review | block_submission
```

High privacy risk blocks contribution submission until the package is edited and rechecked.

## 9. Suggestion Generation And Confirmation

Public sync may generate pending suggestions only. A suggestion must include:

- source candidate;
- why it matches this project;
- proposed local action;
- exact target path;
- risk level;
- reversible state;
- confirmation requirement;
- preview instructions.

Allowed pending suggestion types:

- `learning_note`;
- `profile_rule`;
- `eval_case`;
- `casebook_entry`.

All suggestions start as:

```yaml
status: pending
requires_user_confirmation: true
applied_at: null
```

Review actions:

```text
Preview
Apply
Edit before applying
Dismiss
Disable similar suggestions
```

Only `Apply` or an explicit edited approval can mutate local assets.

## 10. Contribution Closed Loop

Contribution starts from a local diagnosis, not from public sync.

Flow:

```text
diagnosis completed
-> reusable issue detected
-> show lightweight invitation if prompts are enabled
-> generate local pending contribution package
-> generate anonymized case
-> generate privacy report
-> user reviews and edits
-> user selects allowed uses
-> user submits, keeps local, rejects, or withdraws
```

No upload happens during package generation.

## 11. Contribution Package Structure

Minimal package:

```text
.intent-quality/contributions/pending/contrib_YYYYMMDD_NNN/
  contribution.yaml
  anonymized-case.yaml
  privacy-report.yaml
  review.md
```

`contribution.yaml` stores state, source diagnosis, allowed uses, and review status.

`anonymized-case.yaml` stores the public-safe case candidate.

`privacy-report.yaml` stores detected risks, redactions, and remaining review items.

`review.md` gives the human-readable preview and confirmation checklist.

## 12. Anonymization Rules

Default redactions:

- replace project names with role labels such as `local project`;
- remove repository URLs and private paths;
- shorten conversation excerpts;
- remove full logs and file contents;
- remove names, emails, handles, company names, keys, and tokens;
- generalize timestamps when exact time is unnecessary;
- keep failure category, expected behavior, actual failure mode, and teaching notes.

The anonymized package should preserve the collaboration lesson, not the private incident.

## 13. Withdrawal And Prompt Controls

Users must be able to:

- keep a contribution local;
- delete a pending package;
- withdraw a submitted package where the registry supports withdrawal;
- turn off future contribution prompts;
- turn prompts back on in the local profile.

Local state:

```yaml
preferences:
  contribution_prompt_enabled: true

contribution_prompt:
  last_shown_at: "2026-06-16T00:00:00+08:00"
  disabled_at: null
  disabled_reason: null
```

Withdrawal does not rewrite diagnosis history. It changes the contribution state and records the withdrawal request.

## 14. Acceptance Criteria

The minimal loop is complete when:

- a public index can be represented locally;
- at least one external candidate can be marked untrusted and checked;
- a pending suggestion can be generated without applying anything;
- a contribution package can be generated locally without upload;
- anonymization and privacy report files exist;
- every mutating step has `requires_user_confirmation: true`;
- contribution prompts can be disabled and later re-enabled.

## 15. Read-Only Local Check

The repository includes a minimal checker:

```bash
python tools/local_loop_check.py
```

The checker validates the sample public index, external candidate, pending suggestions, and contribution package. It is read-only and must not apply suggestions, mutate profiles, add datasets, add casebook entries, or submit contributions.
