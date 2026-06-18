# Open Source Foundation Checklist

> Status: preparation checklist
> Date: 2026-06-18

## Required Before Public Repository Use

- MIT license exists.
- Contribution guide exists.
- Security policy exists.
- Privacy policy exists.
- README includes installation, quick start, verification, and safety boundaries.
- `pyproject.toml` includes license and project metadata.
- `.intent-quality/` remains ignored.
- Examples are synthetic or anonymized.
- Public samples are documented as untrusted by default.
- Profile memory is documented as pending, project-local, and confirmation-gated.

## Verification Commands

```bash
python -m intent_quality.cli check
python -m compileall intent_quality
```

Expected check behavior:

- read-only;
- no rule mutation;
- no profile mutation;
- no dataset mutation;
- no casebook mutation;
- no candidate adoption;
- no suggestion application;
- no contribution submission.

## Deferred From Open Source Foundation

- hosted accounts;
- dashboard;
- automatic public upload;
- automatic public-sample adoption;
- production public registry trust infrastructure;
- default LLM-as-judge scoring;
- complete semantic evaluator;
- formal adapter integrations as core runtime dependencies.
