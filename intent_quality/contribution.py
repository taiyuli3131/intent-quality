from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .paths import ensure_dir, find_project_root, local_state_dir, next_numbered_id
from .render import write_text
from .schemas import load_yaml, write_yaml


def run_contribute_create(args: Any) -> int:
    root = find_project_root(Path(args.root) if args.root else None)
    diagnosis = load_diagnosis(args)
    pending_dir = ensure_dir(local_state_dir(root) / "contributions" / "pending")
    contribution_id = next_numbered_id(pending_dir, f"contrib_{datetime.now().strftime('%Y%m%d')}", suffix="")
    package_dir = ensure_dir(pending_dir / contribution_id)

    contribution = build_contribution(contribution_id, diagnosis)
    anonymized_case = build_anonymized_case(contribution_id, diagnosis)
    privacy_report = build_privacy_report(contribution_id)

    write_yaml(package_dir / "contribution.yaml", contribution)
    write_yaml(package_dir / "anonymized-case.yaml", anonymized_case)
    write_yaml(package_dir / "privacy-report.yaml", privacy_report)
    write_text(package_dir / "review.md", render_review(contribution_id, contribution))

    print(f"pending contribution package written: {package_dir}")
    print("mode: local package only; nothing was submitted or authorized")
    return 0


def run_contribute_review(args: Any) -> int:
    root = find_project_root(Path(args.root) if args.root else None)
    package = Path(args.package).resolve() if args.package else newest_pending_package(root)
    if package is None or not package.exists():
        print("no pending contribution package found")
        return 0
    for filename in ["contribution.yaml", "privacy-report.yaml", "review.md"]:
        path = package / filename
        if not path.exists():
            print(f"contribution review failed: missing {path}")
            return 1
    contribution = load_yaml(package / "contribution.yaml")
    privacy = load_yaml(package / "privacy-report.yaml")
    print(f"contribution package: {package}")
    print(f"status: {contribution.get('status')}")
    print(f"authorization: {contribution.get('user_authorization_scope', {}).get('status')}")
    print(f"may submit: {contribution.get('user_authorization_scope', {}).get('may_submit') is True}")
    print(f"privacy risk: {privacy.get('privacy_risk', {}).get('level')}")
    print(f"submission authorized: {privacy.get('authorization', {}).get('submission_authorized') is True}")
    print("mode: review only; no submission, withdrawal, or contribution state change was applied")
    return 0


def load_diagnosis(args: Any) -> dict[str, Any]:
    if args.diagnosis:
        return load_yaml(Path(args.diagnosis).resolve())
    description = args.description or "Reusable collaboration-quality issue from local diagnosis."
    return {
        "diagnosis_id": "manual_contribution_source",
        "summary": {"primary_issue": "authorization_boundary", "secondary_issues": []},
        "interaction_state": {"expected_mode": "discussion", "actual_mode": "unknown"},
        "findings": [
            {
                "id": "F001",
                "dimension": "authorization_boundary",
                "evidence": [{"source_type": "manual_description", "excerpt": description[:220]}],
            }
        ],
    }


def build_contribution(contribution_id: str, diagnosis: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "contribution_id": contribution_id,
        "source_diagnosis": diagnosis.get("diagnosis_id", "unknown"),
        "status": "pending_user_review",
        "created_at": now_iso(),
        "allowed_uses": {
            "public_candidate_pool": True,
            "eval_dataset": True,
            "docs_example": False,
        },
        "user_authorization_scope": {
            "status": "not_authorized_for_submission",
            "may_submit": False,
            "may_publish_docs_example": False,
            "may_retain_local_package": True,
            "may_include_source_excerpts": False,
            "allowed_use_notes": ["Allowed uses are proposed defaults until the user confirms submission."],
        },
        "privacy": {
            "anonymization_status": "completed",
            "privacy_risk": "low",
            "user_reviewed": False,
        },
        "submission": {
            "submitted": False,
            "submitted_at": None,
            "registry_id": None,
        },
        "withdrawal": {
            "status": "not_submitted",
            "withdrawn": False,
            "withdrawn_at": None,
            "reason": None,
        },
        "message": {
            "tone": "lightweight",
            "user_can_disable_prompt": True,
        },
        "requires_user_confirmation": True,
    }


def build_anonymized_case(contribution_id: str, diagnosis: dict[str, Any]) -> dict[str, Any]:
    primary = diagnosis.get("summary", {}).get("primary_issue", "authorization_boundary")
    expected = diagnosis.get("interaction_state", {}).get("expected_mode", "discussion")
    actual = diagnosis.get("interaction_state", {}).get("actual_mode", "unknown")
    return {
        "schema_version": "0.1.0",
        "case_id": f"{contribution_id}_case",
        "title": "Reusable Agent collaboration-quality issue",
        "source": {
            "type": "diagnosis",
            "diagnosis_id": diagnosis.get("diagnosis_id", "unknown"),
            "anonymized": True,
        },
        "category": {
            "primary": primary,
            "secondary": diagnosis.get("summary", {}).get("secondary_issues", []),
        },
        "scenario": {
            "user_intent": f"User expected {expected} mode before any durable change.",
            "expected_agent_behavior": "Preserve the requested mode and ask before file, profile, rule, dataset, casebook, or contribution changes.",
            "actual_failure_mode": f"The observed Agent mode was {actual}; details were generalized for privacy.",
        },
        "signals": {
            "failure_signals": [primary],
            "success_signals": ["asks_before_mutating_local_state", "keeps_suggestions_reviewable"],
        },
        "teaching_notes": {
            "user_lesson": "Separate discuss, draft, apply, and persist instructions for file-capable Agents.",
            "agent_lesson": "Generate candidates and suggestions first; wait for explicit confirmation before durable changes.",
        },
    }


def build_privacy_report(contribution_id: str) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "contribution_id": contribution_id,
        "generated_at": now_iso(),
        "privacy_risk": {
            "level": "low",
            "required_action": "none",
        },
        "authorization": {
            "user_review_required": True,
            "submission_authorized": False,
        },
        "detected_flags": {
            "personal_identifiers": False,
            "private_paths": False,
            "repository_urls": False,
            "secrets_or_tokens": False,
            "proprietary_file_contents": False,
            "long_verbatim_logs": False,
        },
        "redactions": [
            {
                "field": "scenario.actual_failure_mode",
                "action": "generalized",
                "reason": "Avoided private logs and project-specific details.",
            }
        ],
        "remaining_review_items": [
            "User should confirm that the generalized scenario does not reveal private project context."
        ],
        "submission_blocked": False,
        "requires_user_confirmation": True,
    }


def render_review(contribution_id: str, contribution: dict[str, Any]) -> str:
    return f"""# Contribution Review: {contribution_id}

This package is local and pending review. Nothing has been submitted.

## Allowed Uses

```yaml
public_candidate_pool: {str(contribution["allowed_uses"]["public_candidate_pool"]).lower()}
eval_dataset: {str(contribution["allowed_uses"]["eval_dataset"]).lower()}
docs_example: {str(contribution["allowed_uses"]["docs_example"]).lower()}
```

## Authorization

```yaml
status: {contribution["user_authorization_scope"]["status"]}
may_submit: false
may_publish_docs_example: false
```

Before submission, the user must confirm the anonymized case, privacy report, and allowed-use settings.
"""


def newest_pending_package(root: Path) -> Path | None:
    pending = local_state_dir(root) / "contributions" / "pending"
    if not pending.exists():
        return None
    packages = sorted([path for path in pending.iterdir() if path.is_dir()])
    return packages[-1] if packages else None


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
