# Privacy

`intent-quality` is local-first. Its default design is to help users diagnose and improve Agent collaboration without uploading local project data.

## Local Data

Runtime project state is expected to live under `.intent-quality/`. This directory is ignored by git in this repository.

Examples of local runtime data may include:

- diagnosis reports;
- generated local candidates;
- pending suggestions;
- contribution packages;
- profile memory suggestions;
- public sync cache.

These files may contain project-specific information. Review them before sharing.

## Public Contributions

Contribution is optional. A local contribution package is not a submission.

Before sharing any contribution material:

- review the anonymized case;
- review the privacy report;
- remove private paths, names, emails, tokens, repository identifiers, and proprietary excerpts;
- confirm allowed uses explicitly.

## Profile Memory

v0.3 profile memory is deliberately narrow:

- it is project-local;
- it is represented as pending suggestions;
- it must include evidence and rollback notes;
- it must not become a broad personal memory system;
- it must not be applied automatically.

## Public Samples

Public samples are untrusted until they pass local checks and the user accepts them. Public sample sync must not automatically modify rules, profiles, datasets, casebooks, rubrics, or contribution settings.
