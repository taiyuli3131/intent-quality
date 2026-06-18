from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen

from .paths import ensure_dir, find_project_root, local_state_dir
from .schemas import load_yaml, load_yaml_bytes, validate_public_case, validate_public_index, write_yaml


@dataclass(frozen=True)
class CachedCandidate:
    data: dict[str, Any]
    cache_path: Path
    sha256: str


def run_public_fetch(args: Any) -> int:
    root = find_project_root(Path(args.root) if args.root else None)
    source = Path(args.index).resolve() if args.index else root / "public-registry" / "index.yaml"
    if not source.exists():
        print(f"public fetch failed: {source} does not exist")
        return 1

    data = load_yaml(source)
    errors = validate_public_index(data, str(source))
    if errors:
        print("public fetch blocked:")
        for error in errors:
            print(f"- {error}")
        return 1

    public_dir = ensure_dir(local_state_dir(root) / "public")
    write_yaml(public_dir / "index.yaml", data)
    write_yaml(
        public_dir / "last-fetch.yaml",
        {
            "schema_version": "0.1.0",
            "fetched_at": now_iso(),
            "source": str(source),
            "mode": "index_only",
            "auto_applied": False,
        },
    )
    print(f"public index fetched: {public_dir / 'index.yaml'}")
    print("mode: index only; no candidates, suggestions, profiles, rules, datasets, or casebooks were applied")
    return 0


def run_public_suggest(args: Any) -> int:
    root = find_project_root(Path(args.root) if args.root else None)
    index_path = Path(args.index).resolve() if args.index else local_state_dir(root) / "public" / "index.yaml"
    if not index_path.exists():
        fallback = root / "public-registry" / "index.yaml"
        index_path = fallback if fallback.exists() else index_path
    if not index_path.exists():
        print(f"public suggest failed: {index_path} does not exist")
        return 1

    index = load_yaml(index_path)
    errors = validate_public_index(index, str(index_path))
    if errors:
        print("public suggest blocked:")
        for error in errors:
            print(f"- {error}")
        return 1

    entries = index.get("entries", [])
    if args.entry_id:
        entries = [entry for entry in entries if entry.get("entry_id") == args.entry_id]
    if not entries:
        print("no public entries matched")
        return 0

    candidate_dir = ensure_dir(local_state_dir(root) / "cases" / "external-candidates")
    suggestion_dir = ensure_dir(local_state_dir(root) / "suggestions")
    suggestions = []
    for entry in entries:
        fetched = fetch_and_gate_candidate(root, index_path, entry)
        if fetched is None:
            return 1
        candidate = build_external_candidate(index, entry, fetched)
        candidate_path = candidate_dir / f"{candidate['candidate_id']}.yaml"
        write_yaml(candidate_path, candidate)
        suggestions.extend(build_suggestions(candidate, entry))

    pending_path = suggestion_dir / "pending-suggestions.yaml"
    write_yaml(
        pending_path,
        {
            "schema_version": "0.1.0",
            "generated_at": now_iso(),
            "suggestions": suggestions,
        },
    )
    print(f"external candidates written: {candidate_dir}")
    print(f"candidate cache written: {local_state_dir(root) / 'public' / 'cache'}")
    print(f"pending suggestions written: {pending_path}")
    print("mode: suggestion generation only; no suggestions were applied")
    return 0


def fetch_and_gate_candidate(root: Path, index_path: Path, entry: dict[str, Any]) -> CachedCandidate | None:
    entry_id = entry.get("entry_id", "unknown")
    try:
        content = fetch_source_bytes(root, index_path, entry)
    except OSError as exc:
        print(f"public candidate fetch blocked: {entry_id}: {exc}")
        return None

    actual_sha = hashlib.sha256(content).hexdigest()
    expected_sha = entry.get("content_sha256")
    if expected_sha != actual_sha:
        print("public candidate fetch blocked:")
        print(f"- {entry_id}: content_sha256 mismatch")
        print(f"  expected: {expected_sha}")
        print(f"  actual:   {actual_sha}")
        return None

    data, parse_errors = load_yaml_bytes(content, entry_id)
    if parse_errors or data is None:
        print("public candidate gate blocked:")
        for error in parse_errors:
            print(f"- {error}")
        return None

    gate_errors = validate_public_case(data, entry, entry_id)
    if gate_errors:
        print("public candidate gate blocked:")
        for error in gate_errors:
            print(f"- {error}")
        return None

    cache_dir = ensure_dir(local_state_dir(root) / "public" / "cache")
    suffix = source_suffix(entry.get("source_url"))
    cache_path = cache_dir / f"{entry_id}{suffix}"
    cache_path.write_bytes(content)
    return CachedCandidate(data=data, cache_path=cache_path, sha256=actual_sha)


def fetch_source_bytes(root: Path, index_path: Path, entry: dict[str, Any]) -> bytes:
    source_url = entry.get("source_url")
    if not source_url:
        raise OSError("missing source_url")
    parsed = urlparse(source_url)
    if parsed.scheme in {"http", "https"}:
        with urlopen(source_url, timeout=20) as response:
            return response.read()
    if parsed.scheme == "file":
        return Path(parsed.path).read_bytes()

    source = Path(source_url)
    candidates = [source]
    if not source.is_absolute():
        candidates = [root / source, index_path.parent / source]
    for candidate in candidates:
        if candidate.exists():
            return candidate.read_bytes()
    raise OSError(f"source_url not found: {source_url}")


def source_suffix(source_url: str | None) -> str:
    if not source_url:
        return ".yaml"
    suffix = Path(urlparse(source_url).path).suffix
    return suffix if suffix else ".yaml"


def build_external_candidate(index: dict[str, Any], entry: dict[str, Any], fetched: CachedCandidate) -> dict[str, Any]:
    entry_id = entry.get("entry_id", "unknown")
    privacy = entry.get("risk_flags", {}).get("privacy", "medium")
    poisoning = entry.get("risk_flags", {}).get("poisoning", "medium")
    return {
        "schema_version": "0.1.0",
        "candidate_id": f"external_{entry_id}",
        "source": {
            "registry": index.get("registry_id", "unknown"),
            "source_url": entry.get("source_url"),
            "fetched_at": now_iso(),
            "public_entry_id": entry_id,
            "cache_path": f".intent-quality/public/cache/{fetched.cache_path.name}",
            "content_sha256": fetched.sha256,
            "sha256_verified": True,
        },
        "trust": {
            "status": "external_candidate",
            "default_trust": "untrusted",
            "local_checks": {
                "schema_valid": True,
                "rubric_compatible": True,
                "privacy_risk": privacy,
                "poisoning_risk": poisoning,
                "relevance_explained": True,
            },
            "user_accepted": False,
        },
        "relevance": {
            "matched_project_patterns": entry.get("compatibility", {}).get("dimensions", []),
            "explanation": [
                f"Public entry '{entry.get('title', entry_id)}' matches local collaboration-quality dimensions.",
                "The candidate remains untrusted until the user explicitly accepts it.",
            ],
        },
        "content_summary": {
            "case_id": fetched.data.get("case_id"),
            "title": fetched.data.get("title"),
            "primary_category": fetched.data.get("category", {}).get("primary"),
        },
        "suggested_actions": [
            {"type": "learning_note", "requires_user_confirmation": True},
            {"type": "eval_case", "requires_user_confirmation": True},
        ],
        "checks": {
            "schema": {"status": "pass"},
            "rubric": {"status": "pass", "rubric_version": entry.get("rubric_version")},
            "privacy": {"status": "pass", "risk_level": privacy, "flags": []},
            "poisoning": {"status": "pass", "risk_level": poisoning, "flags": []},
            "relevance": {"status": "pass", "confidence": "medium"},
        },
    }


def build_suggestions(candidate: dict[str, Any], entry: dict[str, Any]) -> list[dict[str, Any]]:
    candidate_id = candidate["candidate_id"]
    entry_id = entry.get("entry_id", "unknown")
    base_source = {"type": "public_candidate", "candidate_id": candidate_id}
    return [
        {
            "suggestion_id": f"sug_{entry_id}_learning_note",
            "source": base_source,
            "suggestion_type": "learning_note",
            "risk_level": "low",
            "proposal": {
                "title": f"Review public learning note: {entry.get('title', entry_id)}",
                "target": ".intent-quality/playbook/public-sample-trust.md",
                "change_summary": "Create a reviewable learning note from an untrusted public candidate.",
            },
            **suggestion_safety_fields(candidate_id, [".intent-quality/playbook/public-sample-trust.md"]),
            "rationale": candidate.get("relevance", {}).get("explanation", []),
            "status": "pending",
            "requires_user_confirmation": True,
            "reversible": True,
            "applied_at": None,
        },
        {
            "suggestion_id": f"sug_{entry_id}_eval_candidate",
            "source": base_source,
            "suggestion_type": "eval_case",
            "risk_level": "medium",
            "proposal": {
                "title": f"Create external eval candidate: {entry.get('title', entry_id)}",
                "target": f".intent-quality/datasets/external-candidates/{entry_id}.yaml",
                "change_summary": "Create an external eval candidate for review without adding it to accepted datasets.",
            },
            **suggestion_safety_fields(candidate_id, [f".intent-quality/datasets/external-candidates/{entry_id}.yaml"]),
            "rationale": candidate.get("relevance", {}).get("explanation", []),
            "status": "pending",
            "requires_user_confirmation": True,
            "reversible": True,
            "applied_at": None,
        },
    ]


def suggestion_safety_fields(candidate_id: str, files: list[str]) -> dict[str, Any]:
    return {
        "evidence": [
            {
                "source_type": "external_candidate",
                "reference": candidate_id,
                "excerpt": "Candidate passed local schema, rubric, privacy, poisoning, and relevance checks.",
            }
        ],
        "impact_scope": {
            "local_files": files,
            "behavior": ["Creates or updates a reviewable local candidate only after user confirmation."],
            "non_goals": [
                "Does not apply rules.",
                "Does not modify profile, accepted datasets, casebooks, rubrics, or contribution settings.",
            ],
        },
        "rollback_plan": {
            "reversible": True,
            "boundary": "Only files named in impact_scope.local_files would be removed or restored if applied.",
            "required_snapshot": "Review target files before applying.",
        },
        "confirmation_state": {
            "status": "awaiting_user_confirmation",
            "confirmed_by": None,
            "confirmed_at": None,
        },
        "preview": {
            "instructions": "Inspect source, evidence, impact scope, and rollback plan before applying.",
        },
    }


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
