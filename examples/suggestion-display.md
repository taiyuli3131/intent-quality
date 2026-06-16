# Suggestion Display Sample

## Pending Suggestion

```yaml
suggestion_id: sug_20260616_001
source:
  type: diagnosis
  diagnosis_id: diag_20260616_001
suggestion_type: profile_rule
risk_level: medium
requires_user_confirmation: true
reversible: true
status: pending
```

## Require Confirmation Before File Writes In Direction Discussions

Source: diagnosis `diag_20260616_001`  
Risk level: medium  
Status: pending review

### Why This Was Suggested

The diagnosis found that a project direction discussion was treated as permission to update files. This pattern can recur in Codex workflows because the Agent has both conversation and file-editing capabilities.

### Proposed Change

Target:

```text
.intent-quality/profile/project-profile.yaml
```

Change summary:

```text
For product direction, roadmap, positioning, or planning discussions, require explicit user confirmation before file writes.
```

Example rule candidate:

```yaml
preferences:
  require_confirmation_before_file_write: true
  default_mode_for_direction_discussion: discussion_only
```

### What Applying It Would Do

Future Agents using this profile should:

- treat direction discussions as discussion-only by default;
- ask before creating, editing, or deleting files;
- distinguish proposals from applied changes.

### What It Will Not Do

Applying this suggestion will not:

- upload anything publicly;
- modify eval datasets;
- add a public sample to local assets;
- change contribution settings;
- prevent the user from explicitly asking for edits.

### Review Actions

```text
[Preview change] [Apply suggestion] [Edit before applying] [Dismiss] [Disable similar suggestions]
```

Recommended default action:

```text
Preview change
```

Reason:

This suggestion changes future collaboration behavior, so the user should see the exact profile diff before applying it.
