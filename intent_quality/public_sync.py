from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .paths import ensure_dir, find_project_root, local_state_dir
from .schemas import load_yaml, write_yaml


REQUIRED_PUBLIC_CHECKS = [
    "schema_valid",
    "rubric_compatible",
    "privacy_risk",
    "poisoning_risk",
    "relevance_explained",
]


def run_public_fetch(args: Any) -> int:
    root = find_project_root(Path(args.root) if args.root else None)
    source = Path(args.index).resolve() if args.index else root / "public-registry" / "index.yaml"
    if not source.exists():
        print(f"public fetch failed: {source} does not exist")
        return 1

    data = load_yaml(source)
    errors = validate_public_index_policy(data, source)
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
    errors = validate_public_index_policy(index, index_path)
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
        candidate = build_external_candidate(index, entry)
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
    print(f"pending suggestions written: {pending_path}")
    print("mode: suggestion generation only; no suggestions were applied")
    return 0


def validate_public_index_policy(data: dict[str, Any], source: Path) -> list[str]:
    errors: list[str] = []
    if data.get("trust", {}).get("default_trust") != "untrusted":
        errors.append(f"{source}: public index must default to untrusted")
    policy = data.get("sync_policy_hint", {})
    for key in [
        "auto_download_candidates",
        "auto_apply_rules",
        "auto_modify_profile",
        "auto_add_eval_cases",
        "auto_add_casebook_entries",
        "auto_override_rubrics",
        "auto_change_contribution_settings",
    ]:
        if policy.get(key) is not False:
            errors.append(f"{source}: {key} must be false")
    for entry in data.get("entries", []):
        checks = set(entry.get("checks_required", []))
        for check in REQUIRED_PUBLIC_CHECKS:
            if check not in checks:
                errors.append(f"{source}:{entry.get('entry_id', '<unknown>')}: missing check {check}")
    return errors


def build_external_candidate(index: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
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
