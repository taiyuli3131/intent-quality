from __future__ import annotations

from pathlib import Path
from typing import Any

from .schemas import load_yaml, privacy_flags, poisoning_flags, require


SCHEMA_VERSION = "0.4.0-alpha"
ALLOWED_STATUSES = {"ready", "needs_review", "blocked"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_PREMISE_STATUS = {"user-stated", "inferred", "assumed", "verified", "unknown"}
ALLOWED_FINDING_KINDS = {"required", "optional", "forbidden"}
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
BLOCKER_CODES = {"privacy_redaction", "candidate_gate", "schema", "authorization_scope"}


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
        if item.get("expected_status") not in ALLOWED_STATUSES:
            errors.append(f"{item_label}: expected_status must be ready, needs_review, or blocked")
    return errors


def evaluate_calibration_fixture(data: dict[str, Any], label: str = "diagnosis calibration fixture") -> tuple[str, list[str]]:
    errors = validate_calibration_fixture(data, label)
    if errors:
        return "schema", errors

    blockers = set(data.get("blockers", []))
    if privacy_blocked(data):
        blockers.add("privacy_redaction")
    if candidate_gate_blocked(data):
        blockers.add("candidate_gate")

    readiness = data.get("readiness", {})
    status = readiness.get("status")
    if blockers or status == "blocked":
        return "blocked", validate_blockers(data, blockers, label)
    if status == "needs_review":
        return "needs_review", []
    return "ready", []


def validate_calibration_fixture(data: dict[str, Any], label: str = "diagnosis calibration fixture") -> list[str]:
    errors = require(
        data,
        [
            "schema_version",
            "fixture_id",
            "title",
            "expected_status",
            "source",
            "readiness",
            "authorization_scope",
            "confidence_calibration",
            "finding_requirements",
            "findings",
            "premises",
            "completion_questions",
            "privacy",
            "generated_candidates",
            "safety",
        ],
        label,
    )
    if errors:
        return errors
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{label}: schema_version must be {SCHEMA_VERSION}")
    if data.get("expected_status") not in ALLOWED_STATUSES:
        errors.append(f"{label}: expected_status must be ready, needs_review, or blocked")
    errors.extend(validate_readiness(data, label))
    errors.extend(validate_source(data.get("source", {}), label))
    errors.extend(validate_authorization_scope(data.get("authorization_scope", {}), label))
    errors.extend(validate_confidence(data.get("confidence_calibration", {}), label))
    errors.extend(validate_findings(data, label))
    errors.extend(validate_premises(data.get("premises", []), label))
    errors.extend(validate_completion_questions(data, label))
    errors.extend(validate_privacy_section(data.get("privacy", {}), label))
    errors.extend(validate_candidates(data.get("generated_candidates", []), label))
    errors.extend(validate_safety(data.get("safety", {}), label))
    if data.get("expected_status") == "ready" and (privacy_blocked(data) or candidate_gate_blocked(data)):
        errors.append(f"{label}: ready fixtures must not include privacy or candidate gate blockers")
    return errors


def validate_readiness(data: dict[str, Any], label: str) -> list[str]:
    readiness = data.get("readiness", {})
    errors = require(readiness, ["status", "rationale"], f"{label}:readiness")
    if errors:
        return errors
    status = readiness.get("status")
    if status not in ALLOWED_STATUSES:
        errors.append(f"{label}:readiness.status must be ready, needs_review, or blocked")
    if status != data.get("expected_status"):
        errors.append(f"{label}: readiness.status must match expected_status")
    if status == "ready" and readiness.get("requires_manual_completion") is not False:
        errors.append(f"{label}: ready fixtures must not require manual completion")
    if status == "needs_review" and readiness.get("requires_manual_completion") is not True:
        errors.append(f"{label}: needs_review fixtures must require manual completion")
    if status == "blocked" and not data.get("blockers"):
        errors.append(f"{label}: blocked fixtures must list blockers")
    return errors


def validate_source(source: dict[str, Any], label: str) -> list[str]:
    errors = require(source, ["type", "input_summary", "permission_scope"], f"{label}:source")
    if source.get("type") not in {"manual", "conversation", "project"}:
        errors.append(f"{label}:source.type must be manual, conversation, or project")
    if source.get("permission_scope") not in {"user_supplied_description", "project_readonly", "conversation_readonly"}:
        errors.append(f"{label}:source.permission_scope must be read-only or user supplied")
    return errors


def validate_authorization_scope(scope: dict[str, Any], label: str) -> list[str]:
    errors = require(scope, ["boundary_status", "expected_scope", "actual_scope", "targets"], f"{label}:authorization_scope")
    if errors:
        return errors
    targets = scope.get("targets", {})
    if not isinstance(targets, dict):
        return [f"{label}:authorization_scope.targets must be a mapping"]
    for target in PROTECTED_TARGETS:
        detail = targets.get(target)
        if not isinstance(detail, dict):
            errors.append(f"{label}:authorization_scope.targets missing {target}")
            continue
        if detail.get("may_modify") is not False:
            errors.append(f"{label}:authorization_scope.targets.{target}.may_modify must be false")
        if detail.get("requires_user_confirmation") is not True:
            errors.append(f"{label}:authorization_scope.targets.{target}.requires_user_confirmation must be true")
    files = targets.get("files")
    if not isinstance(files, dict):
        errors.append(f"{label}:authorization_scope.targets missing files")
    elif files.get("requires_user_confirmation") is not True and files.get("may_modify") is not True:
        errors.append(f"{label}:authorization_scope.targets.files must be explicit about confirmation")
    return errors


def validate_confidence(confidence: dict[str, Any], label: str) -> list[str]:
    errors = require(confidence, ["level", "score", "rule"], f"{label}:confidence_calibration")
    if errors:
        return errors
    if confidence.get("level") not in ALLOWED_CONFIDENCE:
        errors.append(f"{label}:confidence_calibration.level must be high, medium, or low")
    score = confidence.get("score")
    if not isinstance(score, (int, float)) or not 0 <= score <= 1:
        errors.append(f"{label}:confidence_calibration.score must be between 0 and 1")
    return errors


def validate_findings(data: dict[str, Any], label: str) -> list[str]:
    findings = data.get("findings", [])
    if not isinstance(findings, list) or not findings:
        return [f"{label}: findings must be a non-empty list"]
    errors: list[str] = []
    ids: set[str] = set()
    dimensions: set[str] = set()
    for index, finding in enumerate(findings):
        item_label = f"{label}:findings[{index}]"
        errors.extend(
            require(
                finding,
                ["id", "kind", "dimension", "severity", "confidence", "conclusion", "evidence", "premise_status"],
                item_label,
            )
        )
        ids.add(str(finding.get("id")))
        dimensions.add(str(finding.get("dimension")))
        if finding.get("kind") not in ALLOWED_FINDING_KINDS:
            errors.append(f"{item_label}: kind must be required, optional, or forbidden")
        if finding.get("dimension") not in ALLOWED_DIMENSIONS:
            errors.append(f"{item_label}: invalid dimension {finding.get('dimension')}")
        if finding.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append(f"{item_label}: confidence must be high, medium, or low")
        if finding.get("premise_status") not in ALLOWED_PREMISE_STATUS:
            errors.append(f"{item_label}: invalid premise_status {finding.get('premise_status')}")
        evidence = finding.get("evidence", [])
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{item_label}: evidence must be a non-empty list")
        for evidence_index, item in enumerate(evidence):
            evidence_label = f"{item_label}:evidence[{evidence_index}]"
            errors.extend(require(item, ["id", "source_type", "evidence_type", "premise_status", "excerpt"], evidence_label))
            if item.get("premise_status") not in ALLOWED_PREMISE_STATUS:
                errors.append(f"{evidence_label}: invalid premise_status {item.get('premise_status')}")

    requirements = data.get("finding_requirements", {})
    errors.extend(require(requirements, ["required", "optional", "forbidden"], f"{label}:finding_requirements"))
    required = set(requirements.get("required", []))
    forbidden = set(requirements.get("forbidden", []))
    for dimension in required - dimensions:
        errors.append(f"{label}: missing required finding dimension {dimension}")
    for dimension in forbidden & dimensions:
        errors.append(f"{label}: contains forbidden finding dimension {dimension}")
    if len(ids) != len(findings):
        errors.append(f"{label}: finding ids must be unique")
    return errors


def validate_premises(premises: list[Any], label: str) -> list[str]:
    if not isinstance(premises, list) or not premises:
        return [f"{label}: premises must be a non-empty list"]
    errors: list[str] = []
    for index, premise in enumerate(premises):
        item_label = f"{label}:premises[{index}]"
        errors.extend(require(premise, ["id", "statement", "status", "confidence", "evidence"], item_label))
        if premise.get("status") not in ALLOWED_PREMISE_STATUS:
            errors.append(f"{item_label}: invalid status {premise.get('status')}")
        if premise.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append(f"{item_label}: confidence must be high, medium, or low")
    return errors


def validate_completion_questions(data: dict[str, Any], label: str) -> list[str]:
    questions = data.get("completion_questions", [])
    status = data.get("expected_status")
    if status == "needs_review" and not questions:
        return [f"{label}: needs_review fixtures require completion questions"]
    if not isinstance(questions, list):
        return [f"{label}: completion_questions must be a list"]
    errors: list[str] = []
    for index, question in enumerate(questions):
        item_label = f"{label}:completion_questions[{index}]"
        errors.extend(require(question, ["id", "targets", "question", "why_it_matters"], item_label))
        if not isinstance(question.get("targets"), list) or not question.get("targets"):
            errors.append(f"{item_label}: targets must be a non-empty list")
    return errors


def validate_privacy_section(privacy: dict[str, Any], label: str) -> list[str]:
    errors = require(privacy, ["redaction_status", "detected_flags", "requires_user_review"], f"{label}:privacy")
    if errors:
        return errors
    if privacy.get("redaction_status") not in {"clear", "needs_redaction", "blocked"}:
        errors.append(f"{label}:privacy.redaction_status must be clear, needs_redaction, or blocked")
    flags = privacy.get("detected_flags")
    if not isinstance(flags, list):
        errors.append(f"{label}:privacy.detected_flags must be a list")
    if privacy.get("redaction_status") in {"needs_redaction", "blocked"} and privacy.get("requires_user_review") is not True:
        errors.append(f"{label}:privacy.requires_user_review must be true when redaction is needed")
    return errors


def validate_candidates(candidates: list[Any], label: str) -> list[str]:
    if not isinstance(candidates, list) or not candidates:
        return [f"{label}: generated_candidates must be a non-empty list"]
    errors: list[str] = []
    for index, candidate in enumerate(candidates):
        item_label = f"{label}:generated_candidates[{index}]"
        errors.extend(
            require(
                candidate,
                ["type", "artifact_type", "status", "requires_user_confirmation", "auto_apply", "writes_local_asset", "gate"],
                item_label,
            )
        )
        if not isinstance(candidate.get("requires_user_confirmation"), bool):
            errors.append(f"{item_label}: requires_user_confirmation must be boolean")
        if not isinstance(candidate.get("auto_apply"), bool):
            errors.append(f"{item_label}: auto_apply must be boolean")
        if not isinstance(candidate.get("writes_local_asset"), bool):
            errors.append(f"{item_label}: writes_local_asset must be boolean")
        gate = candidate.get("gate", {})
        errors.extend(require(gate, ["status", "requires_user_confirmation", "adoption_allowed_without_confirmation"], f"{item_label}:gate"))
        if not isinstance(gate.get("requires_user_confirmation"), bool):
            errors.append(f"{item_label}:gate.requires_user_confirmation must be boolean")
        if not isinstance(gate.get("adoption_allowed_without_confirmation"), bool):
            errors.append(f"{item_label}:gate.adoption_allowed_without_confirmation must be boolean")
    return errors


def validate_safety(safety: dict[str, Any], label: str) -> list[str]:
    errors = require(
        safety,
        [
            "read_only_fixture",
            "generates_real_fixture",
            "writes_feedback",
            "default_llm_as_judge",
            "claims_semantic_evaluator",
            "auto_adopts_candidate",
        ],
        f"{label}:safety",
    )
    if errors:
        return errors
    if safety.get("read_only_fixture") is not True:
        errors.append(f"{label}:safety.read_only_fixture must be true")
    for field in [
        "generates_real_fixture",
        "writes_feedback",
        "default_llm_as_judge",
        "claims_semantic_evaluator",
        "auto_adopts_candidate",
    ]:
        if safety.get(field) is not False:
            errors.append(f"{label}:safety.{field} must be false")
    if poisoning_flags(safety):
        errors.append(f"{label}:safety contains unsafe auto-apply or confirmation-bypass language")
    return errors


def validate_blockers(data: dict[str, Any], blockers: set[str], label: str) -> list[str]:
    errors: list[str] = []
    declared = set(data.get("blockers", []))
    unknown = declared - BLOCKER_CODES
    for blocker in sorted(unknown):
        errors.append(f"{label}: unknown blocker {blocker}")
    if not blockers:
        errors.append(f"{label}: blocked fixture must expose at least one blocker")
    if data.get("expected_status") == "blocked" and not declared:
        errors.append(f"{label}: expected blocked fixture must declare blockers")
    if "privacy_redaction" in declared and not privacy_blocked(data):
        errors.append(f"{label}: declared privacy_redaction blocker without privacy evidence")
    if "candidate_gate" in declared and not candidate_gate_blocked(data):
        errors.append(f"{label}: declared candidate_gate blocker without candidate gate evidence")
    return errors


def privacy_blocked(data: dict[str, Any]) -> bool:
    privacy = data.get("privacy", {})
    return privacy.get("redaction_status") in {"needs_redaction", "blocked"} or bool(privacy_flags(data.get("redaction_sample", {})))


def candidate_gate_blocked(data: dict[str, Any]) -> bool:
    for candidate in data.get("generated_candidates", []):
        if candidate.get("requires_user_confirmation") is not True:
            return True
        if candidate.get("auto_apply") is not False:
            return True
        if candidate.get("writes_local_asset") is not False:
            return True
        gate = candidate.get("gate", {})
        if gate.get("status") == "blocked":
            return True
        if gate.get("requires_user_confirmation") is not True:
            return True
        if gate.get("adoption_allowed_without_confirmation") is not False:
            return True
    return False


def load_calibration_manifest(path: Path) -> dict[str, Any]:
    data = load_yaml(path)
    if not isinstance(data, dict):
        return {}
    return data
