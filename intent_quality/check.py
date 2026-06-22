from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from typing import Any, Callable

from .paths import find_project_root
from .schemas import (
    load_yaml,
    load_yaml_bytes,
    validate_contribution_package,
    validate_eval_result_review,
    validate_external_candidate,
    validate_profile_update_suggestion,
    validate_public_case,
    validate_public_index,
    validate_suggestion,
    validate_suggestions_file,
)
from .eval import evaluate_dataset
from .diagnose import build_diagnosis
from .render import render_diagnosis_markdown


EXPECTED_FIXTURES = {
    "good-candidate": "pass",
    "bad-hash": "hash",
    "missing-field": "schema",
    "prompt-injection": "poisoning",
    "privacy-leak": "privacy",
    "auto-apply-attempt": "poisoning",
}

EXPECTED_EVAL_FIXTURES = {
    "auth-boundary-pass.md": ("eval_auth_boundary_direction_001", "pass"),
    "auth-boundary-fail.md": ("eval_auth_boundary_direction_001", "fail"),
    "context-pollution-pass.md": ("eval_context_pollution_001", "pass"),
    "context-pollution-fail.md": ("eval_context_pollution_001", "fail"),
    "advice-only-pass.md": ("eval_advice_only_premature_execution_001", "pass"),
    "advice-only-fail.md": ("eval_advice_only_premature_execution_001", "fail"),
    "unverified-premise-pass.md": ("eval_unverified_premise_001", "pass"),
    "unverified-premise-fail.md": ("eval_unverified_premise_001", "fail"),
    "growth-goal-pass.md": ("eval_growth_goal_replaced_by_risk_001", "pass"),
    "growth-goal-fail.md": ("eval_growth_goal_replaced_by_risk_001", "fail"),
    "growth-goal-needs-review.md": ("eval_growth_goal_replaced_by_risk_001", "needs_review"),
}

EXPECTED_PROFILE_MEMORY_FIXTURES = {
    "valid-profile-update.yaml": "pass",
    "stale-warning.yaml": "pass",
    "unsafe-private.yaml": "privacy",
    "unsafe-auto-apply.yaml": "auto_apply",
    "unsafe-global-memory.yaml": "scope",
}

EXPECTED_EVAL_REVIEW_FIXTURES = {
    "confirmed-pass.yaml": "confirmed_pass",
    "confirmed-fail.yaml": "confirmed_fail",
    "remains-uncertain.yaml": "remains_uncertain",
}


def run_check(args: Any) -> int:
    root = find_project_root(Path(args.root) if args.root else None)
    errors: list[str] = []
    errors.extend(run_legacy_local_loop(root))
    errors.extend(check_public_registry(root))
    errors.extend(check_local_loop_assets(root))
    errors.extend(check_public_candidate_fixtures(root))
    errors.extend(check_eval_response_fixtures(root))
    errors.extend(check_eval_review_fixtures(root))
    errors.extend(check_diagnosis_quality_fixtures(root))
    errors.extend(check_profile_memory_fixtures(root))
    errors.extend(check_playbook_pages(root))

    if errors:
        print("local loop checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("local loop checks passed")
    print("checked: public index, public cases, external candidates, suggestions, contribution packages, public sync fixtures, eval response fixtures, eval review fixtures, diagnosis quality fixtures, profile memory fixtures, playbook links")
    print("mode: read-only; no rules, profiles, datasets, casebooks, candidates, suggestions, or submissions were modified")
    return 0


def run_legacy_local_loop(root: Path) -> list[str]:
    checker_path = root / "tools" / "local_loop_check.py"
    if not checker_path.exists():
        return [f"check failed: {checker_path} does not exist"]

    module = load_checker(checker_path)
    errors: list[str] = []
    checks: list[Callable[[Path], list[str]]] = [
        module.check_public_index,
        module.check_external_candidates,
        module.check_suggestions,
        module.check_contributions,
    ]
    for check in checks:
        errors.extend(check(root))
    return errors


def check_public_registry(root: Path) -> list[str]:
    errors: list[str] = []
    index_path = root / "public-registry" / "index.yaml"
    if not index_path.exists():
        return [f"{index_path}: missing public index"]
    index = load_yaml(index_path)
    errors.extend(validate_public_index(index, str(index_path)))
    for entry in index.get("entries", []):
        source = root / entry.get("source_url", "")
        label = f"{index_path}:{entry.get('entry_id', '<unknown>')}"
        if not source.exists():
            errors.append(f"{label}: source_url not found: {source}")
            continue
        content = source.read_bytes()
        actual_sha = hashlib.sha256(content).hexdigest()
        if actual_sha != entry.get("content_sha256"):
            errors.append(f"{label}: content_sha256 mismatch expected {entry.get('content_sha256')} actual {actual_sha}")
            continue
        case, parse_errors = load_yaml_bytes(content, label)
        errors.extend(parse_errors)
        if case is not None:
            errors.extend(validate_public_case(case, entry, label))
    return errors


def check_local_loop_assets(root: Path) -> list[str]:
    base = root / "examples" / "local-loop" / ".intent-quality"
    errors: list[str] = []
    for path in (base / "cases" / "external-candidates").glob("*.yaml"):
        errors.extend(validate_external_candidate(load_yaml(path), str(path)))
    suggestions = base / "suggestions" / "pending-suggestions.yaml"
    if suggestions.exists():
        errors.extend(validate_suggestions_file(load_yaml(suggestions), str(suggestions)))
    contributions = base / "contributions" / "pending"
    if contributions.exists():
        for package in contributions.iterdir():
            if package.is_dir():
                errors.extend(validate_contribution_package(package))
    return errors


def check_public_candidate_fixtures(root: Path) -> list[str]:
    base = root / "examples" / "public-candidate-fixtures"
    if not base.exists():
        return [f"{base}: missing public sync failure fixtures"]

    errors: list[str] = []
    seen: set[str] = set()
    for fixture, expected in EXPECTED_FIXTURES.items():
        fixture_dir = base / fixture
        seen.add(fixture)
        if not fixture_dir.exists():
            errors.append(f"{fixture_dir}: missing fixture")
            continue
        outcome = evaluate_fixture(fixture_dir)
        if outcome != expected:
            errors.append(f"{fixture_dir}: expected {expected}, got {outcome}")

    extra = sorted(path.name for path in base.iterdir() if path.is_dir() and path.name not in seen)
    for fixture in extra:
        outcome = evaluate_fixture(base / fixture)
        if outcome == "unexpected_error":
            errors.append(f"{base / fixture}: fixture could not be evaluated")
    return errors


def check_eval_response_fixtures(root: Path) -> list[str]:
    dataset_path = root / "datasets" / "collaboration-quality.v0.1.yaml"
    fixture_dir = root / "examples" / "eval-response-fixtures"
    if not dataset_path.exists():
        return [f"{dataset_path}: missing eval dataset"]
    if not fixture_dir.exists():
        return [f"{fixture_dir}: missing eval response fixtures"]

    dataset = load_yaml(dataset_path)
    manifest_path = fixture_dir / "manifest.yaml"
    errors: list[str] = []
    expected = EXPECTED_EVAL_FIXTURES
    if manifest_path.exists():
        manifest = load_yaml(manifest_path)
        expected = {
            item["response"]: (item["eval_id"], item["expected_status"])
            for item in manifest.get("fixtures", [])
        }
    for filename, (eval_id, expected_status) in expected.items():
        path = fixture_dir / filename
        if not path.exists():
            errors.append(f"{path}: missing eval response fixture")
            continue
        response = path.read_text(encoding="utf-8")
        results = evaluate_dataset(dataset, response, eval_id)
        if len(results) != 1:
            errors.append(f"{path}: expected one result for {eval_id}, got {len(results)}")
            continue
        status = results[0].get("result", {}).get("status")
        if status != expected_status:
            errors.append(f"{path}: expected {expected_status}, got {status}")
        if not results[0].get("evidence") and expected_status == "pass":
            errors.append(f"{path}: pass fixture produced no evidence mapping")
        if expected_status == "pass" and results[0].get("failure_codes"):
            errors.append(f"{path}: pass fixture produced failure codes: {results[0].get('failure_codes')}")
        if expected_status == "pass" and results[0].get("observations", {}).get("violated_must_not"):
            errors.append(f"{path}: pass fixture violated must_not observations")
        if expected_status == "pass" and results[0].get("observations", {}).get("blocking_failures"):
            errors.append(f"{path}: pass fixture produced blocking failures")
        if expected_status != "pass" and not results[0].get("failure_codes"):
            errors.append(f"{path}: failing fixture produced no failure codes")
    return errors


def check_eval_review_fixtures(root: Path) -> list[str]:
    fixture_dir = root / "examples" / "eval-review-fixtures"
    manifest_path = fixture_dir / "manifest.yaml"
    if not manifest_path.exists():
        return [f"{manifest_path}: missing eval review fixture manifest"]

    manifest = load_yaml(manifest_path)
    errors: list[str] = []
    expected = {
        item["fixture"]: item["expected_decision"]
        for item in manifest.get("fixtures", [])
    } or EXPECTED_EVAL_REVIEW_FIXTURES

    before = protected_snapshot(root)
    for filename, expected_decision in expected.items():
        path = fixture_dir / filename
        if not path.exists():
            errors.append(f"{path}: missing eval review fixture")
            continue
        review_result = load_yaml(path)
        errors.extend(validate_eval_result_review(review_result, str(path)))
        actual_decision = review_result.get("human_review", {}).get("decision")
        if actual_decision != expected_decision:
            errors.append(f"{path}: expected review decision {expected_decision}, got {actual_decision}")
    after = protected_snapshot(root)
    if before != after:
        errors.append("eval review fixture check modified protected local assets")
    return errors


def check_diagnosis_quality_fixtures(root: Path) -> list[str]:
    fixture_dir = root / "examples" / "diagnosis-fixtures"
    manifest_path = fixture_dir / "manifest.yaml"
    if not manifest_path.exists():
        return [f"{manifest_path}: missing diagnosis quality fixture manifest"]

    manifest = load_yaml(manifest_path)
    errors: list[str] = []
    before = protected_snapshot(root)
    for item in manifest.get("fixtures", []):
        path = fixture_dir / item.get("input", "")
        if not path.exists():
            errors.append(f"{path}: missing diagnosis fixture input")
            continue
        text = path.read_text(encoding="utf-8")
        source_type = item.get("source_type", "manual")
        diagnosis = build_diagnosis(text, f"fixture_{path.stem}", source_type, path, root)
        errors.extend(validate_diagnosis_quality(diagnosis, str(path), item))
        errors.extend(validate_learning_playbook_links(diagnosis, str(path), root))
        rendered = render_diagnosis_markdown(diagnosis)
        for required in [
            "## Authorization Scope",
            "## Premises",
            "## Targeted Completion Questions",
            "## Generated Candidates",
        ]:
            if required not in rendered:
                errors.append(f"{path}: rendered report missing section {required}")

    after = protected_snapshot(root)
    if before != after:
        errors.append("diagnosis fixture check modified protected local assets")
    example_yaml = root / "examples" / "diagnose-report.yaml"
    if not example_yaml.exists():
        errors.append(f"{example_yaml}: missing YAML diagnosis report example")
    else:
        example_diagnosis = load_yaml(example_yaml)
        errors.extend(
            validate_diagnosis_quality(
                example_diagnosis,
                str(example_yaml),
                {
                    "expected_primary_issue": "authorization_boundary",
                    "expected_mode": "discussion",
                    "actual_mode": "file_update",
                },
            )
        )
        errors.extend(validate_learning_playbook_links(example_diagnosis, str(example_yaml), root))
    return errors


def check_profile_memory_fixtures(root: Path) -> list[str]:
    fixture_dir = root / "examples" / "profile-memory-fixtures"
    manifest_path = fixture_dir / "manifest.yaml"
    if not manifest_path.exists():
        return [f"{manifest_path}: missing profile memory fixture manifest"]

    manifest = load_yaml(manifest_path)
    errors: list[str] = []
    before = protected_snapshot(root)
    expected = {
        item["fixture"]: item["expected_status"]
        for item in manifest.get("fixtures", [])
    } or EXPECTED_PROFILE_MEMORY_FIXTURES

    for filename, expected_status in expected.items():
        path = fixture_dir / filename
        if not path.exists():
            errors.append(f"{path}: missing profile memory fixture")
            continue
        suggestion = load_yaml(path)
        outcome = evaluate_profile_memory_fixture(suggestion, str(path))
        if outcome != expected_status:
            errors.append(f"{path}: expected {expected_status}, got {outcome}")

    after = protected_snapshot(root)
    if before != after:
        errors.append("profile memory fixture check modified protected local assets")
    return errors


def check_playbook_pages(root: Path) -> list[str]:
    required = [
        "authorization-boundary.md",
        "context-pollution.md",
        "premise-validation.md",
        "response-mode.md",
        "diagnose-vs-eval.md",
        "public-sample-trust.md",
        "suggestions-and-confirmation.md",
        "contribution-privacy.md",
    ]
    errors: list[str] = []
    for filename in required:
        path = root / "docs" / "playbook" / filename
        if not path.exists():
            errors.append(f"{path}: missing playbook page")
    return errors


def protected_snapshot(root: Path) -> dict[str, str]:
    protected = [
        root / ".intent-quality" / "profile",
        root / ".intent-quality" / "rules",
        root / ".intent-quality" / "datasets",
        root / ".intent-quality" / "cases",
        root / ".intent-quality" / "rubrics",
        root / ".intent-quality" / "contributions",
        root / ".intent-quality" / "public",
        root / ".intent-quality" / "suggestions",
        root / "examples" / "local-loop" / ".intent-quality" / "profile",
        root / "examples" / "local-loop" / ".intent-quality" / "cases",
        root / "examples" / "local-loop" / ".intent-quality" / "contributions",
        root / "examples" / "local-loop" / ".intent-quality" / "public",
        root / "examples" / "local-loop" / ".intent-quality" / "suggestions",
        root / "datasets",
        root / "cases",
        root / "rubrics",
        root / "public-registry",
    ]
    snapshot: dict[str, str] = {}
    for base in protected:
        if not base.exists():
            snapshot[str(base)] = "<missing>"
            continue
        files = sorted(path for path in base.rglob("*") if path.is_file())
        digest = hashlib.sha256()
        for path in files:
            digest.update(str(path.relative_to(root)).encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        snapshot[str(base)] = digest.hexdigest()
    return snapshot


def validate_diagnosis_quality(data: dict[str, Any], label: str, expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "0.3.0-alpha":
        errors.append(f"{label}: schema_version must be 0.3.0-alpha")
    primary = expected.get("expected_primary_issue")
    if primary and data.get("summary", {}).get("primary_issue") != primary:
        errors.append(f"{label}: expected primary issue {primary}, got {data.get('summary', {}).get('primary_issue')}")
    interaction = data.get("interaction_state", {})
    if "expected_mode" in expected and interaction.get("expected_mode") != expected["expected_mode"]:
        errors.append(f"{label}: expected mode {expected['expected_mode']}, got {interaction.get('expected_mode')}")
    if "actual_mode" in expected and interaction.get("actual_mode") != expected["actual_mode"]:
        errors.append(f"{label}: actual mode {expected['actual_mode']}, got {interaction.get('actual_mode')}")
    if not data.get("authorization_scope", {}).get("targets"):
        errors.append(f"{label}: missing authorization-scope targets")
    protected_targets = data.get("authorization_scope", {}).get("targets", {})
    for target in ["profile", "rules", "datasets", "casebooks", "rubrics", "contributions", "public_samples"]:
        detail = protected_targets.get(target, {})
        if detail.get("may_modify") is not False:
            errors.append(f"{label}: diagnosis must not authorize {target} mutation")
        if detail.get("requires_user_confirmation") is not True:
            errors.append(f"{label}: {target} must require user confirmation")
    if not data.get("premises"):
        errors.append(f"{label}: missing premises")
    for premise in data.get("premises", []):
        if premise.get("status") not in {"user-stated", "inferred", "assumed", "verified", "unknown"}:
            errors.append(f"{label}: invalid premise status {premise.get('status')}")
    if not data.get("completion_questions"):
        errors.append(f"{label}: missing targeted completion questions")
    for finding in data.get("findings", []):
        if not finding.get("confidence"):
            errors.append(f"{label}: finding {finding.get('id')} missing confidence")
        if finding.get("premise_status") not in {"user-stated", "inferred", "assumed", "verified", "unknown"}:
            errors.append(f"{label}: finding {finding.get('id')} invalid premise status")
        for evidence in finding.get("evidence", []):
            for field in ["id", "source_type", "evidence_type", "premise_status", "excerpt"]:
                if field not in evidence:
                    errors.append(f"{label}: finding {finding.get('id')} evidence missing {field}")
    candidates = data.get("generated_candidates", [])
    candidate_types = {candidate.get("type") for candidate in candidates}
    for required in ["case", "eval", "profile", "rule", "contribution", "public_sample"]:
        if required not in candidate_types:
            errors.append(f"{label}: missing generated {required} candidate")
    for candidate in candidates:
        if candidate.get("status") != "preview_only":
            errors.append(f"{label}: candidate {candidate.get('type')} must be preview_only")
        if candidate.get("auto_apply") is not False:
            errors.append(f"{label}: candidate {candidate.get('type')} must not auto-apply")
        if candidate.get("writes_local_asset") is not False:
            errors.append(f"{label}: candidate {candidate.get('type')} must not write local assets")
        if candidate.get("requires_user_confirmation") is not True:
            errors.append(f"{label}: candidate {candidate.get('type')} must require confirmation")
        if candidate.get("artifact_type") == "profile_update":
            errors.extend(validate_diagnosis_profile_candidate(candidate, label))
    if not data.get("learning_feedback", {}).get("concepts"):
        errors.append(f"{label}: missing learning concepts")
    return errors


def validate_diagnosis_profile_candidate(candidate: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    if candidate.get("profile_scope") != "project":
        errors.append(f"{label}: profile_update candidate profile_scope must be project")
    for field in ["evidence", "impact_scope", "confirmation_state", "rollback_plan", "stale_memory_warning"]:
        if field not in candidate:
            errors.append(f"{label}: profile_update candidate missing {field}")
    confirmation = candidate.get("confirmation_state", {})
    if confirmation.get("status") != "awaiting_user_confirmation":
        errors.append(f"{label}: profile_update candidate must await user confirmation")
    if confirmation.get("confirmed_at") is not None:
        errors.append(f"{label}: profile_update candidate confirmed_at must be null")
    if candidate.get("impact_scope", {}).get("local_files") != [".intent-quality/profile/project-profile.yaml"]:
        errors.append(f"{label}: profile_update candidate must target only the project profile")
    stale_warning = candidate.get("stale_memory_warning", {})
    if stale_warning.get("requires_user_review") is not True:
        errors.append(f"{label}: profile_update stale warning must require review")
    rollback = candidate.get("rollback_plan", {})
    if rollback.get("reversible") is not True:
        errors.append(f"{label}: profile_update rollback must be reversible")
    preview = candidate.get("preview", {})
    if preview.get("pending_only") is not True or preview.get("requires_user_confirmation") is not True:
        errors.append(f"{label}: profile_update preview must be pending and confirmation-gated")
    return errors


def evaluate_profile_memory_fixture(suggestion: dict[str, Any], label: str) -> str:
    errors = validate_suggestion(suggestion, label)
    if not errors:
        return "pass"
    blob = "\n".join(errors)
    if "private identifiers" in blob:
        return "privacy"
    if "auto-apply" in blob or "confirmation-bypass" in blob or "auto_apply" in blob:
        return "auto_apply"
    if "global" in blob or "cross-project" in blob or "broad personal memory" in blob or "profile_scope" in blob:
        return "scope"
    return "schema"


def validate_learning_playbook_links(data: dict[str, Any], label: str, root: Path) -> list[str]:
    errors: list[str] = []
    for item in data.get("learning_feedback", {}).get("concepts", []):
        if not isinstance(item, dict):
            errors.append(f"{label}: learning concept must be a mapping")
            continue
        playbook = item.get("playbook")
        concept = item.get("concept", "<unknown>")
        if not playbook:
            errors.append(f"{label}: learning concept {concept} missing playbook link")
            continue
        path = (root / playbook).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{label}: learning concept {concept} playbook must stay under project root")
            continue
        if not path.exists():
            errors.append(f"{label}: learning concept {concept} playbook not found: {playbook}")
    return errors


def evaluate_fixture(fixture_dir: Path) -> str:
    index_path = fixture_dir / "index.yaml"
    case_path = fixture_dir / "case.yaml"
    if not index_path.exists() or not case_path.exists():
        return "unexpected_error"
    index = load_yaml(index_path)
    index_errors = validate_public_index(index, str(index_path))
    if index_errors:
        return classify_errors(index_errors)
    entries = index.get("entries", [])
    if not entries:
        return "unexpected_error"
    entry = entries[0]
    content = case_path.read_bytes()
    actual_sha = hashlib.sha256(content).hexdigest()
    if actual_sha != entry.get("content_sha256"):
        return "hash"
    case, parse_errors = load_yaml_bytes(content, str(case_path))
    if parse_errors or case is None:
        return "schema"
    case_errors = validate_public_case(case, entry, str(case_path))
    if case_errors:
        return classify_errors(case_errors)
    return "pass"


def classify_errors(errors: list[str]) -> str:
    blob = "\n".join(errors)
    if "content_sha256" in blob:
        return "hash"
    if "privacy_risk" in blob or "privacy flag" in blob:
        return "privacy"
    if "poisoning_risk" in blob or "poisoning flag" in blob:
        return "poisoning"
    if "schema" in blob or "missing required field" in blob:
        return "schema"
    return "unexpected_error"


def load_checker(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("intent_quality_local_loop_check", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load checker from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
