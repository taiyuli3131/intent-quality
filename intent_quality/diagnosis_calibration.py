from __future__ import annotations

from pathlib import Path
from typing import Any

from .schemas import load_yaml, privacy_flags, require


SCHEMA_VERSION = "0.4.0-alpha"
MANIFEST_STATUSES = {"ready", "needs_review", "blocked"}
GATE_READINESS_STATUSES = {"ready", "needs-human-review", "blocked"}
ALLOWED_PREMISE_STATUS = {"user-stated", "inferred", "assumed", "verified", "unknown"}
ALLOWED_DIMENSIONS = {
    "authorization_boundary",
    "response_mode_mismatch",
    "context_pollution",
    "premise_validation",
    "intent_preservation",
    "privacy_redaction",
    "candidate_gate",
}
PROTECTED_TARGETS = {
    "profile",
    "rules",
    "datasets",
    "casebooks",
    "rubrics",
    "contributions",
    "public_samples",
}
UNSAFE_FINDING_CONFIDENCE_FIELDS = {
    "confidence",
    "confidence_level",
    "model_confidence",
    "severity_confidence",
    "priority_confidence",
    "style_quality_confidence",
}


def validate_calibration_manifest(data: dict[str, Any], label: str = "diagnosis calibration manifest") -> list[str]:
    errors = require(data, ["schema_version", "fixtures"], label)
    if errors:
        return errors
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}")
    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        errors.append(f"{label}: fixtures must be a non-empty list")
        return errors
    seen: set[str] = set()
    for index, item in enumerate(fixtures):
        item_label = f"{label}:fixtures[{index}]"
        errors.extend(require(item, ["fixture", "expected_status"], item_label))
        fixture = item.get("fixture")
        if fixture in seen:
            errors.append(f"{item_label}: duplicate fixture {fixture}")
        seen.add(str(fixture))
        if item.get("expected_status") not in MANIFEST_STATUSES:
            errors.append(f"{item_label}: expected_status must be ready, needs_review, or blocked")
    return errors


def evaluate_calibration_fixture(data: dict[str, Any], label: str = "diagnosis calibration fixture") -> tuple[str, list[str]]:
    errors = validate_calibration_fixture(data, label)
    if errors:
        return "schema", errors

    readiness = data.get("diagnosis_quality_gate", {}).get("readiness")
    if readiness == "needs-human-review":
        return "needs_review", []
    return str(readiness), []


def validate_calibration_fixture(data: dict[str, Any], label: str = "diagnosis calibration fixture") -> list[str]:
    errors = require(
        data,
        [
            "schema_version",
            "fixture_id",
            "title",
            "input",
            "expected_diagnosis",
            "calibration_notes",
            "diagnosis_quality_gate",
        ],
        label,
    )
    if errors:
        return errors
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}")
    errors.extend(validate_input(data.get("input", {}), label))
    errors.extend(validate_expected_diagnosis(data.get("expected_diagnosis", {}), label))
    errors.extend(validate_calibration_notes(data.get("calibration_notes"), label))
    errors.extend(validate_quality_gate(data.get("diagnosis_quality_gate", {}), label))
    errors.extend(validate_read_only_boundary(data, label))
    return errors


def validate_input(input_data: dict[str, Any], label: str) -> list[str]:
    errors = require(input_data, ["user_request", "available_context", "agent_response", "tool_context"], f"{label}:input")
    if errors:
        return errors
    for field in ["user_request", "available_context", "agent_response", "tool_context"]:
        if input_data.get(field) is None:
            errors.append(f"{label}:input.{field} must not be null")
    return errors


def validate_expected_diagnosis(expected: dict[str, Any], label: str) -> list[str]:
    errors = require(
        expected,
        [
            "required_findings",
            "optional_findings",
            "forbidden_findings",
            "premise_status",
            "required_completion_questions",
            "expected_authorization_scope",
            "learning_feedback_expectations",
        ],
        f"{label}:expected_diagnosis",
    )
    if errors:
        return errors

    required_findings = expected.get("required_findings")
    optional_findings = expected.get("optional_findings")
    forbidden_findings = expected.get("forbidden_findings")
    if not isinstance(required_findings, list) or not required_findings:
        errors.append(f"{label}:expected_diagnosis.required_findings must be a non-empty list")
    else:
        for index, finding in enumerate(required_findings):
            errors.extend(validate_finding(finding, f"{label}:expected_diagnosis.required_findings[{index}]", required=True))
    if not isinstance(optional_findings, list):
        errors.append(f"{label}:expected_diagnosis.optional_findings must be a list")
    else:
        for index, finding in enumerate(optional_findings):
            errors.extend(validate_finding(finding, f"{label}:expected_diagnosis.optional_findings[{index}]", required=False))
    if not isinstance(forbidden_findings, list):
        errors.append(f"{label}:expected_diagnosis.forbidden_findings must be a list")
    else:
        for index, finding in enumerate(forbidden_findings):
            errors.extend(validate_forbidden_finding(finding, f"{label}:expected_diagnosis.forbidden_findings[{index}]"))

    if expected.get("premise_status") not in ALLOWED_PREMISE_STATUS:
        errors.append(f"{label}:expected_diagnosis.premise_status must be a supported premise status")
    questions = expected.get("required_completion_questions")
    if not isinstance(questions, list):
        errors.append(f"{label}:expected_diagnosis.required_completion_questions must be a list")
    scope = expected.get("expected_authorization_scope")
    errors.extend(validate_authorization_scope(scope, f"{label}:expected_diagnosis.expected_authorization_scope"))
    learning = expected.get("learning_feedback_expectations")
    if not isinstance(learning, list):
        errors.append(f"{label}:expected_diagnosis.learning_feedback_expectations must be a list")
    return errors


def validate_finding(finding: Any, label: str, required: bool) -> list[str]:
    errors = require(finding, ["id", "dimension", "finding", "evidence", "premise_status", "confidence_range"], label)
    if errors:
        return errors
    for field in UNSAFE_FINDING_CONFIDENCE_FIELDS:
        if field in finding:
            errors.append(f"{label}: use confidence_range for evidence support reliability, not {field}")
    if finding.get("dimension") not in ALLOWED_DIMENSIONS:
        errors.append(f"{label}: invalid dimension {finding.get('dimension')}")
    if finding.get("premise_status") not in ALLOWED_PREMISE_STATUS:
        errors.append(f"{label}: invalid premise_status {finding.get('premise_status')}")
    evidence = finding.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{label}: evidence must be a non-empty list")
    errors.extend(validate_confidence_range(finding.get("confidence_range"), f"{label}:confidence_range", required))
    return errors


def validate_confidence_range(confidence_range: Any, label: str, required: bool) -> list[str]:
    if confidence_range is None:
        if required:
            return [f"{label}: required finding must include confidence_range"]
        return []
    errors = require(confidence_range, ["min", "max"], label)
    if errors:
        return errors
    minimum = confidence_range.get("min")
    maximum = confidence_range.get("max")
    if not isinstance(minimum, (int, float)) or not 0 <= minimum <= 1:
        errors.append(f"{label}.min must be between 0.0 and 1.0")
    if not isinstance(maximum, (int, float)) or not 0 <= maximum <= 1:
        errors.append(f"{label}.max must be between 0.0 and 1.0")
    if isinstance(minimum, (int, float)) and isinstance(maximum, (int, float)) and minimum > maximum:
        errors.append(f"{label}.min must be less than or equal to max")
    return errors


def validate_forbidden_finding(finding: Any, label: str) -> list[str]:
    if not isinstance(finding, dict):
        return [f"{label}: forbidden finding must be a mapping"]
    errors = require(finding, ["dimension", "reason"], label)
    if finding.get("dimension") not in ALLOWED_DIMENSIONS:
        errors.append(f"{label}: invalid dimension {finding.get('dimension')}")
    if "confidence_range" in finding:
        errors.append(f"{label}: forbidden finding must not include confidence_range")
    return errors


def validate_authorization_scope(scope: Any, label: str) -> list[str]:
    errors = require(scope, ["expected_scope", "actual_scope", "targets"], label)
    if errors:
        return errors
    targets = scope.get("targets", {})
    if not isinstance(targets, dict):
        return [f"{label}.targets must be a mapping"]
    for target in PROTECTED_TARGETS:
        detail = targets.get(target)
        if not isinstance(detail, dict):
            errors.append(f"{label}.targets missing {target}")
            continue
        if detail.get("may_modify") is not False:
            errors.append(f"{label}.targets.{target}.may_modify must be false")
        if detail.get("requires_user_confirmation") is not True:
            errors.append(f"{label}.targets.{target}.requires_user_confirmation must be true")
    files = targets.get("files")
    if not isinstance(files, dict):
        errors.append(f"{label}.targets missing files")
    elif files.get("may_modify") is not False:
        errors.append(f"{label}.targets.files.may_modify must be false for calibration fixtures")
    elif files.get("requires_user_confirmation") is not True:
        errors.append(f"{label}.targets.files.requires_user_confirmation must be true")
    return errors


def validate_calibration_notes(notes: Any, label: str) -> list[str]:
    if not isinstance(notes, list) or not notes:
        return [f"{label}:calibration_notes must be a non-empty list"]
    return []


def validate_quality_gate(gate: dict[str, Any], label: str) -> list[str]:
    errors = require(
        gate,
        [
            "readiness",
            "case_candidate_signal",
            "eval_candidate_signal",
            "auto_apply_allowed",
            "requires_confirmation",
        ],
        f"{label}:diagnosis_quality_gate",
    )
    if errors:
        return errors
    if gate.get("readiness") not in GATE_READINESS_STATUSES:
        errors.append(f"{label}:diagnosis_quality_gate.readiness must be ready, needs-human-review, or blocked")
    errors.extend(validate_candidate_signal(gate.get("case_candidate_signal", {}), f"{label}:diagnosis_quality_gate.case_candidate_signal", require_dimensions=False))
    errors.extend(validate_candidate_signal(gate.get("eval_candidate_signal", {}), f"{label}:diagnosis_quality_gate.eval_candidate_signal", require_dimensions=True))
    if gate.get("auto_apply_allowed") is not False:
        errors.append(f"{label}:diagnosis_quality_gate.auto_apply_allowed must be false")
    if gate.get("requires_confirmation") is not True:
        errors.append(f"{label}:diagnosis_quality_gate.requires_confirmation must be true")
    return errors


def validate_candidate_signal(signal: dict[str, Any], label: str, require_dimensions: bool) -> list[str]:
    fields = ["eligible", "reasons", "blockers"]
    if require_dimensions:
        fields.append("eval_dimensions")
    errors = require(signal, fields, label)
    if errors:
        return errors
    if not isinstance(signal.get("eligible"), bool):
        errors.append(f"{label}.eligible must be boolean")
    for field in fields:
        if field == "eligible":
            continue
        if not isinstance(signal.get(field), list):
            errors.append(f"{label}.{field} must be a list")
    if require_dimensions:
        for dimension in signal.get("eval_dimensions", []):
            if dimension not in ALLOWED_DIMENSIONS:
                errors.append(f"{label}.eval_dimensions contains invalid dimension {dimension}")
    return errors


def validate_read_only_boundary(data: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    text = str(data).lower()
    for phrase in [
        "accepted baseline",
        "write feedback",
        "update memory",
        "update profile",
        "update rules",
        "update datasets",
        "update casebooks",
        "update rubrics",
        "update contributions",
    ]:
        if phrase in text:
            errors.append(f"{label}: calibration fixture must not request protected mutation: {phrase}")
    for flag in privacy_flags(data):
        errors.append(f"{label}: privacy flag found: {flag}")
    return errors


def load_calibration_manifest(path: Path) -> dict[str, Any]:
    data = load_yaml(path)
    if not isinstance(data, dict):
        return {}
    return data
