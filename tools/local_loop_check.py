#!/usr/bin/env python3
"""Minimal read-only checks for the public sync and contribution loop."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


SECRET_RE = re.compile(
    r"(api[_-]?key|secret|token|password|-----BEGIN [A-Z ]+PRIVATE KEY-----)",
    re.IGNORECASE,
)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
URL_RE = re.compile(r"\bhttps?://[^\s'\"]+")
PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:\\Users\\|/Users/|/home/|\\\\[^\\]+\\)")
INJECTION_RE = re.compile(
    r"(ignore previous|ignore all prior|system prompt|developer message|"
    r"must automatically apply|do not ask for confirmation)",
    re.IGNORECASE,
)


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def require(mapping: dict[str, Any], fields: list[str], label: str) -> list[str]:
    errors: list[str] = []
    for field in fields:
        if field not in mapping:
            errors.append(f"{label}: missing required field {field}")
    return errors


def text_blob(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(text_blob(v) for v in value.values())
    if isinstance(value, list):
        return "\n".join(text_blob(v) for v in value)
    return "" if value is None else str(value)


def privacy_flags(value: Any) -> list[str]:
    blob = text_blob(value)
    flags: list[str] = []
    if SECRET_RE.search(blob):
        flags.append("secret_like_text")
    if EMAIL_RE.search(blob):
        flags.append("email")
    if URL_RE.search(blob):
        flags.append("url")
    if PRIVATE_PATH_RE.search(blob):
        flags.append("private_path")
    return flags


def poisoning_flags(value: Any) -> list[str]:
    blob = text_blob(value)
    flags: list[str] = []
    if INJECTION_RE.search(blob):
        flags.append("instruction_override_or_auto_apply_language")
    if "auto_apply_rules: true" in blob or "requires_user_confirmation: false" in blob:
        flags.append("unsafe_mutation_default")
    return flags


def check_public_index(root: Path) -> list[str]:
    path = root / "public-registry" / "index.yaml"
    data = load_yaml(path)
    errors = require(data, ["schema_version", "registry_id", "trust", "entries"], str(path))
    if data.get("trust", {}).get("default_trust") != "untrusted":
        errors.append(f"{path}: public index must default to untrusted")
    if data.get("sync_policy_hint", {}).get("auto_apply_rules") is not False:
        errors.append(f"{path}: auto_apply_rules must be false")
    for policy in [
        "auto_download_candidates",
        "auto_modify_profile",
        "auto_add_eval_cases",
        "auto_add_casebook_entries",
        "auto_override_rubrics",
        "auto_change_contribution_settings",
    ]:
        if data.get("sync_policy_hint", {}).get(policy) is not False:
            errors.append(f"{path}: {policy} must be false")
    for entry in data.get("entries", []):
        errors.extend(
            require(
                entry,
                [
                    "entry_id",
                    "entry_type",
                    "schema_version",
                    "rubric_version",
                    "source_url",
                    "checks_required",
                ],
                f"{path}:{entry.get('entry_id', '<unknown>')}",
            )
        )
        required_checks = set(entry.get("checks_required", []))
        for check in {
            "schema_valid",
            "rubric_compatible",
            "privacy_risk",
            "poisoning_risk",
            "relevance_explained",
        }:
            if check not in required_checks:
                errors.append(f"{path}:{entry.get('entry_id')}: missing check {check}")
    return errors


def check_external_candidates(root: Path) -> list[str]:
    base = root / "examples" / "local-loop" / ".intent-quality" / "cases" / "external-candidates"
    errors: list[str] = []
    for path in base.glob("*.yaml"):
        data = load_yaml(path)
        errors.extend(require(data, ["candidate_id", "source", "trust", "relevance"], str(path)))
        trust = data.get("trust", {})
        checks = trust.get("local_checks", {})
        if trust.get("default_trust") != "untrusted":
            errors.append(f"{path}: candidate must default to untrusted")
        if trust.get("user_accepted") is not False:
            errors.append(f"{path}: user_accepted must start false")
        for check in ["schema_valid", "rubric_compatible", "privacy_risk", "poisoning_risk", "relevance_explained"]:
            if check not in checks:
                errors.append(f"{path}: missing local check {check}")
        if checks.get("relevance_explained") is not True:
            errors.append(f"{path}: relevance_explained must be true before suggestions")
        if checks.get("poisoning_risk") == "high":
            errors.append(f"{path}: high poisoning risk candidates must be quarantined")
        for action in data.get("suggested_actions", []):
            if action.get("requires_user_confirmation") is not True:
                errors.append(f"{path}: suggested action must require user confirmation")
        for flag in privacy_flags(data):
            errors.append(f"{path}: privacy flag found: {flag}")
        for flag in poisoning_flags(data):
            errors.append(f"{path}: poisoning flag found: {flag}")
    return errors


def check_suggestions(root: Path) -> list[str]:
    path = root / "examples" / "local-loop" / ".intent-quality" / "suggestions" / "pending-suggestions.yaml"
    data = load_yaml(path)
    errors = require(data, ["schema_version", "suggestions"], str(path))
    for suggestion in data.get("suggestions", []):
        label = f"{path}:{suggestion.get('suggestion_id', '<unknown>')}"
        errors.extend(
            require(
                suggestion,
                [
                    "source",
                    "suggestion_type",
                    "risk_level",
                    "proposal",
                    "evidence",
                    "impact_scope",
                    "rollback_plan",
                    "confirmation_state",
                    "preview",
                    "status",
                ],
                label,
            )
        )
        if suggestion.get("status") != "pending":
            errors.append(f"{label}: suggestion must start pending")
        if suggestion.get("requires_user_confirmation") is not True:
            errors.append(f"{label}: requires_user_confirmation must be true")
        if suggestion.get("applied_at") is not None:
            errors.append(f"{label}: applied_at must start null")
        if not suggestion.get("evidence"):
            errors.append(f"{label}: evidence must not be empty")
        if not suggestion.get("impact_scope", {}).get("local_files"):
            errors.append(f"{label}: impact_scope.local_files must name target files")
        rollback = suggestion.get("rollback_plan", {})
        if rollback.get("reversible") is not True or not rollback.get("boundary"):
            errors.append(f"{label}: rollback_plan must be reversible and include a boundary")
        confirmation = suggestion.get("confirmation_state", {})
        if confirmation.get("status") != "awaiting_user_confirmation":
            errors.append(f"{label}: confirmation_state.status must be awaiting_user_confirmation")
        if confirmation.get("confirmed_at") is not None:
            errors.append(f"{label}: confirmed_at must start null")
    return errors


def check_contributions(root: Path) -> list[str]:
    base = root / "examples" / "local-loop" / ".intent-quality" / "contributions" / "pending"
    errors: list[str] = []
    for package in base.iterdir():
        if not package.is_dir():
            continue
        contribution = load_yaml(package / "contribution.yaml")
        privacy = load_yaml(package / "privacy-report.yaml")
        if contribution.get("status") != "pending_user_review":
            errors.append(f"{package}: contribution must start pending_user_review")
        if contribution.get("submission", {}).get("submitted") is not False:
            errors.append(f"{package}: contribution must not start submitted")
        if contribution.get("requires_user_confirmation") is not True:
            errors.append(f"{package}: contribution must require user confirmation")
        authorization = contribution.get("user_authorization_scope", {})
        if authorization.get("status") != "not_authorized_for_submission":
            errors.append(f"{package}: contribution must start not_authorized_for_submission")
        if authorization.get("may_submit") is not False:
            errors.append(f"{package}: contribution package generation must not authorize submission")
        if authorization.get("may_publish_docs_example") is not False:
            errors.append(f"{package}: docs example permission must default false")
        if contribution.get("allowed_uses", {}).get("docs_example") is not False:
            errors.append(f"{package}: docs_example allowed use must default false")
        withdrawal = contribution.get("withdrawal", {})
        if withdrawal.get("status") not in {"not_submitted", "withdrawn"}:
            errors.append(f"{package}: withdrawal.status must be explicit")
        if privacy.get("authorization", {}).get("submission_authorized") is not False:
            errors.append(f"{package}: privacy report must show submission_authorized false")
        if privacy.get("requires_user_confirmation") is not True:
            errors.append(f"{package}: privacy report must require user confirmation")
        if privacy.get("submission_blocked") is True and privacy.get("privacy_risk", {}).get("level") == "low":
            errors.append(f"{package}: low privacy risk should not block submission")
        for filename in ["anonymized-case.yaml", "privacy-report.yaml", "review.md"]:
            if not (package / filename).exists():
                errors.append(f"{package}: missing {filename}")
        anonymized = load_yaml(package / "anonymized-case.yaml")
        for flag in privacy_flags(anonymized):
            errors.append(f"{package / 'anonymized-case.yaml'}: privacy flag found: {flag}")
        for flag in poisoning_flags(anonymized):
            errors.append(f"{package / 'anonymized-case.yaml'}: poisoning flag found: {flag}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Run read-only local loop checks.")
    parser.add_argument("--root", default=".", help="Repository root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    for check in [check_public_index, check_external_candidates, check_suggestions, check_contributions]:
        errors.extend(check(root))

    if errors:
        print("local loop checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("local loop checks passed")
    print("checked: public index, external candidates, pending suggestions, contribution packages")
    print("mode: read-only; no rules, profiles, datasets, casebooks, or submissions were modified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
