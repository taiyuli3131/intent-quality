from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .paths import ensure_dir, find_project_root, local_state_dir, next_numbered_id
from .render import render_diagnosis_markdown, write_text
from .schemas import write_yaml


ISSUE_PATTERNS = {
    "authorization_boundary": [
        "do not edit",
        "don't edit",
        "before we change",
        "without permission",
        "unauthorized",
        "write files",
        "modified",
        "created file",
    ],
    "response_mode_mismatch": [
        "discuss",
        "advice",
        "tell me whether",
        "brainstorm",
        "planning",
        "treated as execution",
    ],
    "context_pollution": [
        "ignore previous",
        "old context",
        "stale context",
        "previous discussion",
        "scope reset",
    ],
    "premise_validation": [
        "clearly better",
        "unverified",
        "assume",
        "no evidence",
        "unsupported",
        "fact",
    ],
    "intent_preservation": [
        "replaced",
        "goal drift",
        "instead of",
        "preserve",
        "actual objective",
    ],
}


DIMENSION_LABELS = {
    "authorization_boundary": "Authorization boundary may have been crossed or needs explicit confirmation.",
    "response_mode_mismatch": "The requested response mode may not match the Agent action.",
    "context_pollution": "Prior or unrelated context may have affected the current task.",
    "premise_validation": "A decision-critical premise may need validation before use.",
    "intent_preservation": "The user's objective may have been replaced or narrowed.",
}


def run_manual(args: Any) -> int:
    text = args.description
    if not text:
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            print("Describe the collaboration issue. Submit an empty line to finish.")
            lines: list[str] = []
            while True:
                try:
                    line = input("> ")
                except EOFError:
                    break
                if not line:
                    break
                lines.append(line)
            text = "\n".join(lines)
    return create_diagnosis(text, "manual", None, Path(args.root) if args.root else None)


def run_conversation(args: Any) -> int:
    path = Path(args.conversation).resolve()
    text = path.read_text(encoding="utf-8")
    return create_diagnosis(text, "conversation", path, Path(args.root) if args.root else None)


def create_diagnosis(text: str, source_type: str, source_path: Path | None, root_arg: Path | None) -> int:
    root = find_project_root(root_arg)
    diagnoses_dir = ensure_dir(local_state_dir(root) / "diagnoses")
    date_part = datetime.now().strftime("%Y%m%d")
    local_id = next_numbered_id(diagnoses_dir, f"diag_{date_part}")
    diagnosis_id = local_id

    data = build_diagnosis(text, diagnosis_id, source_type, source_path, root)
    yaml_path = diagnoses_dir / f"{diagnosis_id}.yaml"
    md_path = diagnoses_dir / f"{diagnosis_id}.md"
    write_yaml(yaml_path, data)
    write_text(md_path, render_diagnosis_markdown(data))

    print(f"diagnosis written: {yaml_path}")
    print(f"report written: {md_path}")
    print("mode: diagnosis reports only; no profile, rules, dataset, casebook, or contribution files were modified")
    return 0


def build_diagnosis(
    text: str,
    diagnosis_id: str,
    source_type: str,
    source_path: Path | None,
    root: Path,
) -> dict[str, Any]:
    lowered = text.lower()
    detected = [dimension for dimension, needles in ISSUE_PATTERNS.items() if any(n in lowered for n in needles)]
    if not detected:
        detected = ["response_mode_mismatch"]

    primary = detected[0]
    secondary = detected[1:]
    confidence = "medium" if source_type == "conversation" and len(text.strip()) > 200 else "low"
    expected_mode, actual_mode = infer_modes(lowered)
    findings = [make_finding(index + 1, dimension, text, confidence) for index, dimension in enumerate(detected)]
    now = datetime.now().astimezone().isoformat(timespec="seconds")

    return {
        "schema_version": "0.1.0",
        "diagnosis_id": diagnosis_id,
        "created_at": now,
        "source": {
            "type": source_type,
            "path": str(source_path) if source_path else str(root),
            "permission_scope": "project_readonly" if source_type != "manual" else "user_supplied_description",
        },
        "summary": {
            "primary_issue": primary,
            "secondary_issues": secondary,
            "overall_confidence": confidence,
        },
        "interaction_state": {
            "expected_mode": expected_mode,
            "actual_mode": actual_mode,
            "mismatch": expected_mode != actual_mode,
        },
        "dimensions": build_dimensions(detected, findings, confidence),
        "findings": findings,
        "missing_information": missing_questions(source_type, detected),
        "learning_feedback": {
            "concepts": detected[:3],
            "user_tip": "Separate discussion, draft, execution, and persistence when asking file-capable Agents to work in a project.",
        },
        "generated_candidates": {
            "case": "preview_only",
            "eval": "preview_only",
            "contribution": "optional_preview_only",
            "profile_update": "optional_preview_only",
        },
    }


def infer_modes(lowered: str) -> tuple[str, str]:
    if any(term in lowered for term in ["do not edit", "don't edit", "discuss", "advice", "tell me whether"]):
        expected = "discussion"
    elif any(term in lowered for term in ["evaluate", "review", "check"]):
        expected = "verification"
    else:
        expected = "diagnosis"

    if any(term in lowered for term in ["created", "modified", "wrote", "updated file", "write files"]):
        actual = "file_update"
    elif any(term in lowered for term in ["answered", "said", "recommended"]):
        actual = "discussion"
    else:
        actual = "unknown"
    return expected, actual


def make_finding(index: int, dimension: str, text: str, confidence: str) -> dict[str, Any]:
    excerpt = first_excerpt(text, ISSUE_PATTERNS.get(dimension, []))
    severity = "high" if dimension == "authorization_boundary" else "medium"
    return {
        "id": f"F{index:03d}",
        "dimension": dimension,
        "severity": severity,
        "confidence": confidence,
        "conclusion": DIMENSION_LABELS[dimension],
        "evidence": [
            {
                "source_type": "input_text",
                "excerpt": excerpt,
            }
        ],
        "recommendation": recommendation_for(dimension),
    }


def first_excerpt(text: str, needles: list[str]) -> str:
    compact = " ".join(text.split())
    lowered = compact.lower()
    for needle in needles:
        index = lowered.find(needle)
        if index >= 0:
            start = max(0, index - 60)
            end = min(len(compact), index + 160)
            return compact[start:end]
    return compact[:220] if compact else "No detailed input was provided."


def recommendation_for(dimension: str) -> str:
    return {
        "authorization_boundary": "Require explicit confirmation before file writes, profile changes, rule changes, datasets, casebooks, or contribution actions.",
        "response_mode_mismatch": "State the intended mode before acting and keep discussion/advice separate from execution.",
        "context_pollution": "Treat explicit topic switches as scope resets and label any reused context.",
        "premise_validation": "Mark central claims as user-stated or unverified until evidence is supplied or checked.",
        "intent_preservation": "Preserve the user's legitimate objective while separating path risks as guardrails.",
    }[dimension]


def build_dimensions(detected: list[str], findings: list[dict[str, Any]], confidence: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for dimension in ISSUE_PATTERNS:
        related = [finding["id"] for finding in findings if finding["dimension"] == dimension]
        result[dimension] = {
            "score": 0.35 if dimension in detected else 0.75,
            "confidence": confidence if dimension in detected else "low",
            "findings": related,
        }
    return result


def missing_questions(source_type: str, detected: list[str]) -> list[str]:
    questions = ["What exact user wording defined the expected response mode?"]
    if "authorization_boundary" in detected:
        questions.append("Did the user explicitly authorize file writes or durable state changes?")
    if "context_pollution" in detected:
        questions.append("Which prior context was still relevant, and which context should have been excluded?")
    if "premise_validation" in detected:
        questions.append("What evidence, if any, supports the decision-critical premise?")
    if source_type == "manual":
        questions.append("What did the Agent actually do or say that shows the failure?")
    return questions[:4]
