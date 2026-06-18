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
    validate_external_candidate,
    validate_public_case,
    validate_public_index,
    validate_suggestions_file,
)


EXPECTED_FIXTURES = {
    "good-candidate": "pass",
    "bad-hash": "hash",
    "missing-field": "schema",
    "prompt-injection": "poisoning",
    "privacy-leak": "privacy",
    "auto-apply-attempt": "poisoning",
}


def run_check(args: Any) -> int:
    root = find_project_root(Path(args.root) if args.root else None)
    errors: list[str] = []
    errors.extend(run_legacy_local_loop(root))
    errors.extend(check_public_registry(root))
    errors.extend(check_local_loop_assets(root))
    errors.extend(check_public_candidate_fixtures(root))

    if errors:
        print("local loop checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("local loop checks passed")
    print("checked: public index, public cases, external candidates, suggestions, contribution packages, public sync fixtures")
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
