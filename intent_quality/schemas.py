from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


REQUIRED_PUBLIC_CHECKS = {
    "schema_valid",
    "rubric_compatible",
    "privacy_risk",
    "poisoning_risk",
    "relevance_explained",
}

SAFE_SYNC_FALSE_POLICIES = [
    "auto_download_candidates",
    "auto_apply_rules",
    "auto_modify_profile",
    "auto_add_eval_cases",
    "auto_add_casebook_entries",
    "auto_override_rubrics",
    "auto_change_contribution_settings",
]

SECRET_RE = re.compile(
    r"(api[_-]?key|secret|token|password|-----BEGIN [A-Z ]+PRIVATE KEY-----)",
    re.IGNORECASE,
)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
URL_RE = re.compile(r"\bhttps?://[^\s'\"]+")
PRIVATE_PATH_RE = re.compile(r"([A-Za-z]:\\Users\\|/Users/|/home/|\\\\[^\\]+\\)")
INJECTION_RE = re.compile(
    r"(ignore previous|ignore all prior|system prompt|developer message|"
    r"must automatically apply|do not ask for confirmation|"
    r"auto_apply_rules:\s*true|requires_user_confirmation:\s*false|"
    r"user_accepted:\s*true|confirmed_at:\s*['\"]?\d)",
    re.IGNORECASE,
)
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
PROJECT_PROFILE_TARGETS = {
    ".intent-quality/profile/project-profile.yaml",
    "profile/project-profile.yaml",
}
EVAL_REVIEW_STATUSES = {"pending", "in_review", "reviewed"}
EVAL_REVIEW_DECISIONS = {"confirmed_pass", "confirmed_fail", "remains_uncertain"}


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def write_yaml(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=False)


def load_yaml_bytes(content: bytes, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = yaml.safe_load(content.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        return None, [f"{label}: source content is not valid UTF-8 YAML: {exc}"]
    if not isinstance(value, dict):
        return None, [f"{label}: source content must be a YAML mapping"]
    return value, []


def require(mapping: Any, fields: list[str], label: str) -> list[str]:
    if not isinstance(mapping, dict):
        return [f"{label}: expected mapping"]
    return [f"{label}: missing required field {field}" for field in fields if field not in mapping]


def require_bool(mapping: dict[str, Any], field: str, expected: bool, label: str) -> list[str]:
    if mapping.get(field) is not expected:
        return [f"{label}: {field} must be {str(expected).lower()}"]
    return []


def validate_public_index(data: dict[str, Any], label: str = "public index") -> list[str]:
    errors = require(data, ["schema_version", "registry_id", "generated_at", "trust", "sync_policy_hint", "entries"], label)
    if errors:
        return errors
    if data.get("trust", {}).get("default_trust") != "untrusted":
        errors.append(f"{label}: trust.default_trust must be untrusted")
    policy = data.get("sync_policy_hint", {})
    for key in SAFE_SYNC_FALSE_POLICIES:
        if policy.get(key) is not False:
            errors.append(f"{label}: sync_policy_hint.{key} must be false")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append(f"{label}: entries must be a non-empty list")
        return errors
    for index, entry in enumerate(entries):
        errors.extend(validate_public_index_entry(entry, f"{label}:entries[{index}]"))
    return errors


def validate_public_index_entry(entry: dict[str, Any], label: str) -> list[str]:
    errors = require(
        entry,
        [
            "entry_id",
            "entry_type",
            "schema_version",
            "rubric_version",
            "title",
            "category",
            "summary",
            "source_url",
            "content_sha256",
            "created_at",
            "updated_at",
            "license",
            "allowed_uses",
            "risk_flags",
            "compatibility",
            "checks_required",
        ],
        label,
    )
    if errors:
        return errors
    if entry.get("entry_type") != "case":
        errors.append(f"{label}: entry_type must be case for v0.2-alpha")
    if not SHA256_RE.match(str(entry.get("content_sha256", ""))):
        errors.append(f"{label}: content_sha256 must be a lowercase SHA256 hex digest")
    checks = set(entry.get("checks_required", []))
    missing = sorted(REQUIRED_PUBLIC_CHECKS - checks)
    for check in missing:
        errors.append(f"{label}: missing required check {check}")
    allowed = entry.get("allowed_uses", {})
    errors.extend(require(allowed, ["public_candidate_pool", "eval_dataset", "docs_example"], f"{label}:allowed_uses"))
    if allowed.get("docs_example") is not False:
        errors.append(f"{label}: allowed_uses.docs_example must default false")
    compatibility = entry.get("compatibility", {})
    if not compatibility.get("dimensions"):
        errors.append(f"{label}: compatibility.dimensions must not be empty")
    return errors


def validate_public_case(data: dict[str, Any], entry: dict[str, Any] | None = None, label: str = "public case") -> list[str]:
    errors = require(
        data,
        ["schema_version", "case_id", "rubric_version", "title", "source", "category", "scenario", "signals"],
        label,
    )
    if errors:
        return errors
    if entry:
        if data.get("schema_version") != entry.get("schema_version"):
            errors.append(f"{label}: schema_version does not match public index")
        if data.get("rubric_version") != entry.get("rubric_version"):
            errors.append(f"{label}: rubric_version does not match public index")
    source = data.get("source", {})
    if source.get("type") != "public_registry":
        errors.append(f"{label}: source.type must be public_registry")
    if source.get("anonymized") is not True:
        errors.append(f"{label}: source.anonymized must be true")
    category = data.get("category", {})
    errors.extend(require(category, ["primary", "secondary"], f"{label}:category"))
    scenario = data.get("scenario", {})
    errors.extend(
        require(
            scenario,
            ["user_intent", "expected_agent_behavior", "actual_failure_mode"],
            f"{label}:scenario",
        )
    )
    signals = data.get("signals", {})
    errors.extend(require(signals, ["failure_signals", "success_signals"], f"{label}:signals"))
    if not signals.get("failure_signals"):
        errors.append(f"{label}: signals.failure_signals must not be empty")
    if not signals.get("success_signals"):
        errors.append(f"{label}: signals.success_signals must not be empty")
    privacy = privacy_flags(data)
    if privacy:
        errors.append(f"{label}: privacy_risk failed: {', '.join(privacy)}")
    poisoning = poisoning_flags(data)
    if poisoning:
        errors.append(f"{label}: poisoning_risk failed: {', '.join(poisoning)}")
    return errors


def validate_external_candidate(data: dict[str, Any], label: str = "external candidate") -> list[str]:
    errors = require(data, ["schema_version", "candidate_id", "source", "trust", "relevance", "suggested_actions"], label)
    if errors:
        return errors
    source = data.get("source", {})
    errors.extend(require(source, ["registry", "source_url", "fetched_at", "public_entry_id"], f"{label}:source"))
    if "content_sha256" in source and not SHA256_RE.match(str(source.get("content_sha256", ""))):
        errors.append(f"{label}: source.content_sha256 must be a lowercase SHA256 hex digest")
    if source.get("sha256_verified") is not True and "content_sha256" in source:
        errors.append(f"{label}: source.sha256_verified must be true when content_sha256 is recorded")
    trust = data.get("trust", {})
    if trust.get("status") != "external_candidate":
        errors.append(f"{label}: trust.status must be external_candidate")
    if trust.get("default_trust") != "untrusted":
        errors.append(f"{label}: trust.default_trust must be untrusted")
    if trust.get("user_accepted") is not False:
        errors.append(f"{label}: trust.user_accepted must be false")
    checks = trust.get("local_checks", {})
    for check in REQUIRED_PUBLIC_CHECKS:
        if check not in checks:
            errors.append(f"{label}: trust.local_checks missing {check}")
    if checks.get("schema_valid") is not True:
        errors.append(f"{label}: schema_valid must be true for generated candidates")
    if checks.get("rubric_compatible") is not True:
        errors.append(f"{label}: rubric_compatible must be true for generated candidates")
    if checks.get("relevance_explained") is not True:
        errors.append(f"{label}: relevance_explained must be true for generated candidates")
    relevance = data.get("relevance", {})
    if not relevance.get("explanation"):
        errors.append(f"{label}: relevance.explanation must not be empty")
    for action in data.get("suggested_actions", []):
        if action.get("requires_user_confirmation") is not True:
            errors.append(f"{label}: suggested action must require user confirmation")
    for flag in poisoning_flags_without_paths(data):
        errors.append(f"{label}: poisoning flag found: {flag}")
    return errors


def validate_suggestion(suggestion: dict[str, Any], label: str = "suggestion") -> list[str]:
    errors = require(
        suggestion,
        [
            "suggestion_id",
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
            "requires_user_confirmation",
            "reversible",
            "applied_at",
        ],
        label,
    )
    if errors:
        return errors
    if suggestion.get("status") != "pending":
        errors.append(f"{label}: status must be pending")
    if suggestion.get("requires_user_confirmation") is not True:
        errors.append(f"{label}: requires_user_confirmation must be true")
    if suggestion.get("applied_at") is not None:
        errors.append(f"{label}: applied_at must be null")
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
        errors.append(f"{label}: confirmation_state.confirmed_at must start null")
    if suggestion.get("suggestion_type") == "profile_update":
        errors.extend(validate_profile_update_suggestion(suggestion, label))
    return errors


def validate_profile_update_suggestion(suggestion: dict[str, Any], label: str = "profile update suggestion") -> list[str]:
    errors: list[str] = []
    source = suggestion.get("source", {})
    proposal = suggestion.get("proposal", {})
    impact = suggestion.get("impact_scope", {})
    preview = suggestion.get("preview", {})
    stale_warning = suggestion.get("stale_memory_warning")

    if source.get("type") != "diagnosis":
        errors.append(f"{label}: profile_update source.type must be diagnosis")
    if not source.get("diagnosis_id"):
        errors.append(f"{label}: profile_update source.diagnosis_id is required")
    if proposal.get("profile_scope") != "project":
        errors.append(f"{label}: proposal.profile_scope must be project")
    if proposal.get("target") not in PROJECT_PROFILE_TARGETS:
        errors.append(f"{label}: proposal.target must be the project profile")
    if proposal.get("confirmed_preference") is not False:
        errors.append(f"{label}: proposal.confirmed_preference must be false")
    if proposal.get("auto_apply") is not False:
        errors.append(f"{label}: proposal.auto_apply must be false")

    if not isinstance(stale_warning, dict):
        errors.append(f"{label}: stale_memory_warning is required")
    else:
        if stale_warning.get("status") not in {"none", "possible", "present"}:
            errors.append(f"{label}: stale_memory_warning.status must be none, possible, or present")
        if "reason" not in stale_warning:
            errors.append(f"{label}: stale_memory_warning.reason is required")
        if stale_warning.get("requires_user_review") is not True:
            errors.append(f"{label}: stale_memory_warning.requires_user_review must be true")

    evidence = suggestion.get("evidence", [])
    if not any(item.get("source_type") == "diagnosis_finding" for item in evidence if isinstance(item, dict)):
        errors.append(f"{label}: evidence must include a diagnosis_finding source")

    local_files = impact.get("local_files", [])
    if local_files != [".intent-quality/profile/project-profile.yaml"]:
        errors.append(f"{label}: impact_scope.local_files must contain only the project profile")
    if not impact.get("behavior"):
        errors.append(f"{label}: impact_scope.behavior must describe behavior impact")
    non_goals = " ".join(str(item).lower() for item in impact.get("non_goals", []))
    if "does not edit" not in non_goals and "does not apply" not in non_goals:
        errors.append(f"{label}: impact_scope.non_goals must say the suggestion does not apply edits")

    if preview.get("pending_only") is not True:
        errors.append(f"{label}: preview.pending_only must be true")
    if preview.get("requires_user_confirmation") is not True:
        errors.append(f"{label}: preview.requires_user_confirmation must be true")

    if privacy_flags(suggestion):
        errors.append(f"{label}: profile_update must not contain private identifiers or private paths")
    if poisoning_flags(suggestion):
        errors.append(f"{label}: profile_update contains unsafe auto-apply or confirmation-bypass language")
    scope_blob = text_blob(
        {
            "proposal": proposal,
            "behavior": impact.get("behavior", []),
        }
    )
    if re.search(r"\b(global|cross-project|cross project|all projects|personal memory|remember me)\b", scope_blob, re.IGNORECASE):
        errors.append(f"{label}: profile_update must not create global, cross-project, or broad personal memory")
    return errors


def validate_eval_review_record(data: dict[str, Any], label: str = "eval review record") -> list[str]:
    errors = require(
        data,
        [
            "schema_version",
            "review_status",
            "reviewed_by",
            "reviewed_at",
            "decision",
            "reviewer_notes",
            "calibration_notes",
            "safety",
        ],
        label,
    )
    if errors:
        return errors
    if data.get("schema_version") != "0.3.0":
        errors.append(f"{label}: schema_version must be 0.3.0")
    status = data.get("review_status")
    if status not in EVAL_REVIEW_STATUSES:
        errors.append(f"{label}: review_status must be pending, in_review, or reviewed")
    decision = data.get("decision")
    if status == "reviewed":
        if decision not in EVAL_REVIEW_DECISIONS:
            errors.append(f"{label}: reviewed records require a valid decision")
        if not data.get("reviewed_by"):
            errors.append(f"{label}: reviewed records require reviewed_by")
        if not data.get("reviewed_at"):
            errors.append(f"{label}: reviewed records require reviewed_at")
        if not data.get("reviewer_notes"):
            errors.append(f"{label}: reviewed records require reviewer_notes")
    elif decision is not None:
        errors.append(f"{label}: non-reviewed records must keep decision null")
    if not isinstance(data.get("reviewer_notes"), list):
        errors.append(f"{label}: reviewer_notes must be a list")
    calibration = data.get("calibration_notes", {})
    errors.extend(require(calibration, ["false_positive", "false_negative"], f"{label}:calibration_notes"))
    for key in ["false_positive", "false_negative"]:
        item = calibration.get(key, {})
        errors.extend(require(item, ["applies", "notes"], f"{label}:calibration_notes.{key}"))
        if "applies" in item and not isinstance(item.get("applies"), bool):
            errors.append(f"{label}:calibration_notes.{key}.applies must be boolean")
        if "notes" in item and not isinstance(item.get("notes"), list):
            errors.append(f"{label}:calibration_notes.{key}.notes must be a list")
    safety = data.get("safety", {})
    for field in ["local_record_only", "changes_default_scorer", "applies_result", "mutates_assets"]:
        if field not in safety:
            errors.append(f"{label}:safety missing {field}")
    if safety.get("local_record_only") is not True:
        errors.append(f"{label}: safety.local_record_only must be true")
    for field in ["changes_default_scorer", "applies_result", "mutates_assets"]:
        if safety.get(field) is not False:
            errors.append(f"{label}: safety.{field} must be false")
    if privacy_flags(data):
        errors.append(f"{label}: eval review record must not contain private identifiers or private paths")
    if poisoning_flags(data):
        errors.append(f"{label}: eval review record contains unsafe auto-apply or confirmation-bypass language")
    return errors


def validate_eval_result_review(data: dict[str, Any], label: str = "eval result") -> list[str]:
    errors = require(data, ["schema_version", "result_id", "source", "scoring_method", "result", "human_review"], label)
    if errors:
        return errors
    if data.get("schema_version") not in {"0.2.0", "0.3.0"}:
        errors.append(f"{label}: schema_version must be 0.2.0 or 0.3.0")
    scoring = data.get("scoring_method", {})
    if scoring.get("type") != "heuristic":
        errors.append(f"{label}: scoring_method.type must remain heuristic")
    limitations = str(scoring.get("limitations", "")).lower()
    if "not a complete semantic evaluator" not in limitations:
        errors.append(f"{label}: scoring_method.limitations must preserve heuristic scorer limitation language")
    result = data.get("result", {})
    if result.get("status") != "needs_review":
        errors.append(f"{label}: eval review fixtures must target needs_review results")
    if not result.get("needs_review_reason"):
        errors.append(f"{label}: needs_review results must include needs_review_reason")
    errors.extend(validate_eval_review_record(data.get("human_review", {}), f"{label}:human_review"))
    return errors


def validate_adapter_export(data: dict[str, Any], label: str = "adapter export") -> list[str]:
    errors = require(
        data,
        [
            "schema_version",
            "export_id",
            "format",
            "experimental",
            "internal_only",
            "source",
            "scoring_method",
            "safety",
            "limitations",
            "draft",
        ],
        label,
    )
    if errors:
        return errors
    if data.get("schema_version") != "0.3.0":
        errors.append(f"{label}: schema_version must be 0.3.0")
    if data.get("format") not in {"promptfoo", "deepeval", "pydantic-evals"}:
        errors.append(f"{label}: format must be promptfoo, deepeval, or pydantic-evals")
    if data.get("experimental") is not True:
        errors.append(f"{label}: experimental must be true")
    if data.get("internal_only") is not True:
        errors.append(f"{label}: internal_only must be true")
    source = data.get("source", {})
    errors.extend(
        require(
            source,
            ["dataset_id", "dataset_schema_version", "rubric_version", "case_count"],
            f"{label}:source",
        )
    )
    scoring = data.get("scoring_method", {})
    if scoring.get("type") != "heuristic":
        errors.append(f"{label}: scoring_method.type must remain heuristic")
    limitations_text = text_blob(data.get("limitations", []) + [scoring.get("limitations", "")]).lower()
    if "not a complete semantic evaluator" not in limitations_text:
        errors.append(f"{label}: limitations must preserve heuristic scorer limitation language")
    safety = data.get("safety", {})
    if safety.get("requires_user_confirmation_before_use") is not True:
        errors.append(f"{label}: safety.requires_user_confirmation_before_use must be true")
    for field in [
        "runs_external_framework",
        "core_runtime_dependency",
        "changes_default_scorer",
        "applies_results",
        "mutates_assets",
    ]:
        if safety.get(field) is not False:
            errors.append(f"{label}: safety.{field} must be false")
    draft = data.get("draft", {})
    if not isinstance(draft, dict) or not draft.get("config_type"):
        errors.append(f"{label}: draft.config_type is required")
    if privacy_flags(data):
        errors.append(f"{label}: adapter export must not contain private identifiers or private paths")
    if poisoning_flags(data):
        errors.append(f"{label}: adapter export contains unsafe auto-apply or confirmation-bypass language")
    return errors


def validate_suggestions_file(data: dict[str, Any], label: str = "suggestions file") -> list[str]:
    errors = require(data, ["schema_version", "suggestions"], label)
    if errors:
        return errors
    for index, suggestion in enumerate(data.get("suggestions", [])):
        errors.extend(validate_suggestion(suggestion, f"{label}:suggestions[{index}]"))
    return errors


def validate_contribution_package(package: Path, label: str | None = None) -> list[str]:
    label = label or str(package)
    errors: list[str] = []
    required_files = ["contribution.yaml", "anonymized-case.yaml", "privacy-report.yaml", "review.md"]
    for filename in required_files:
        if not (package / filename).exists():
            errors.append(f"{label}: missing {filename}")
    if errors:
        return errors
    contribution = load_yaml(package / "contribution.yaml")
    privacy = load_yaml(package / "privacy-report.yaml")
    anonymized = load_yaml(package / "anonymized-case.yaml")
    errors.extend(validate_contribution(contribution, f"{label}:contribution.yaml"))
    errors.extend(validate_privacy_report(privacy, f"{label}:privacy-report.yaml"))
    for flag in privacy_flags(anonymized):
        errors.append(f"{label}:anonymized-case.yaml privacy flag found: {flag}")
    for flag in poisoning_flags(anonymized):
        errors.append(f"{label}:anonymized-case.yaml poisoning flag found: {flag}")
    return errors


def validate_contribution(data: dict[str, Any], label: str = "contribution") -> list[str]:
    errors = require(
        data,
        [
            "schema_version",
            "contribution_id",
            "source_diagnosis",
            "status",
            "allowed_uses",
            "user_authorization_scope",
            "privacy",
            "submission",
            "withdrawal",
            "requires_user_confirmation",
        ],
        label,
    )
    if errors:
        return errors
    if data.get("status") != "pending_user_review":
        errors.append(f"{label}: status must start pending_user_review")
    if data.get("requires_user_confirmation") is not True:
        errors.append(f"{label}: requires_user_confirmation must be true")
    allowed = data.get("allowed_uses", {})
    if allowed.get("docs_example") is not False:
        errors.append(f"{label}: allowed_uses.docs_example must default false")
    auth = data.get("user_authorization_scope", {})
    if auth.get("status") != "not_authorized_for_submission":
        errors.append(f"{label}: user_authorization_scope.status must be not_authorized_for_submission")
    for field in ["may_submit", "may_publish_docs_example", "may_include_source_excerpts"]:
        if auth.get(field) is not False:
            errors.append(f"{label}: user_authorization_scope.{field} must be false")
    if data.get("submission", {}).get("submitted") is not False:
        errors.append(f"{label}: submission.submitted must be false")
    withdrawal = data.get("withdrawal", {})
    if withdrawal.get("status") not in {"not_submitted", "withdrawn"}:
        errors.append(f"{label}: withdrawal.status must be explicit")
    return errors


def validate_privacy_report(data: dict[str, Any], label: str = "privacy report") -> list[str]:
    errors = require(
        data,
        [
            "schema_version",
            "contribution_id",
            "generated_at",
            "privacy_risk",
            "authorization",
            "detected_flags",
            "remaining_review_items",
            "submission_blocked",
            "requires_user_confirmation",
        ],
        label,
    )
    if errors:
        return errors
    if data.get("authorization", {}).get("submission_authorized") is not False:
        errors.append(f"{label}: authorization.submission_authorized must be false")
    if data.get("requires_user_confirmation") is not True:
        errors.append(f"{label}: requires_user_confirmation must be true")
    if data.get("submission_blocked") is True and data.get("privacy_risk", {}).get("level") == "low":
        errors.append(f"{label}: low privacy risk should not block submission")
    return errors


def text_blob(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(text_blob(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(text_blob(item) for item in value)
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
    return flags


def poisoning_flags_without_paths(value: Any) -> list[str]:
    return poisoning_flags(value)
