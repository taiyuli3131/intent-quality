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

MUTATING_TARGETS = [
    "profile",
    "rules",
    "datasets",
    "casebooks",
    "rubrics",
    "contributions",
    "public_samples",
]


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
    confidence = overall_confidence(source_type, text, detected)
    expected_mode, actual_mode = infer_modes(lowered)
    findings = [
        make_finding(index + 1, dimension, text, confidence, source_type)
        for index, dimension in enumerate(detected)
    ]
    premises = build_premises(text, source_type, expected_mode, actual_mode, findings)
    authorization_scope = build_authorization_scope(lowered, expected_mode, actual_mode)
    questions = completion_questions(source_type, detected, expected_mode, actual_mode)
    now = datetime.now().astimezone().isoformat(timespec="seconds")

    return {
        "schema_version": "0.3.0-alpha",
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
            "analysis": interaction_analysis(expected_mode, actual_mode),
        },
        "authorization_scope": authorization_scope,
        "dimensions": build_dimensions(detected, findings, confidence),
        "premises": premises,
        "findings": findings,
        "completion_questions": questions,
        "missing_information": [item["question"] for item in questions],
        "learning_feedback": {
            "concepts": [
                {
                    "concept": concept,
                    "why_it_matters": learning_note_for(concept),
                    "playbook": playbook_path_for(concept),
                }
                for concept in detected
            ],
            "user_tip": "Separate discussion, draft, execution, and persistence when asking file-capable Agents to work in a project.",
            "agent_tip": "Name the expected mode and ask before crossing from analysis into file or durable-state changes.",
        },
        "generated_candidates": generated_candidates(primary, detected, findings),
    }


def overall_confidence(source_type: str, text: str, detected: list[str]) -> str:
    stripped = text.strip()
    if source_type == "conversation" and len(stripped) > 400 and len(detected) > 1:
        return "high"
    if source_type == "conversation" and len(stripped) > 200:
        return "medium"
    if source_type == "manual" and len(stripped) > 280 and len(detected) > 1:
        return "medium"
    return "low"


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


def interaction_analysis(expected_mode: str, actual_mode: str) -> str:
    if expected_mode == actual_mode:
        return "The available input does not show a response-mode mismatch."
    if actual_mode == "unknown":
        return "The expected mode is visible, but the Agent's actual behavior needs more evidence."
    return "The Agent appears to have crossed from the expected mode into a different behavior mode."


def build_authorization_scope(lowered: str, expected_mode: str, actual_mode: str) -> dict[str, Any]:
    explicit_write_auth = any(
        term in lowered
        for term in ["please edit", "go ahead and edit", "apply the changes", "update the files", "write the files"]
    )
    denied_write_auth = any(term in lowered for term in ["do not edit", "don't edit", "without permission"])
    write_status = "denied" if denied_write_auth else "authorized" if explicit_write_auth else "unknown"
    if actual_mode == "file_update" and write_status != "authorized":
        boundary_status = "exceeded"
    elif expected_mode in {"discussion", "verification"} and write_status == "unknown":
        boundary_status = "not_authorized"
    else:
        boundary_status = "within_scope"

    targets: dict[str, Any] = {}
    for target in MUTATING_TARGETS:
        targets[target] = {
            "status": "not_authorized",
            "may_modify": False,
            "requires_user_confirmation": True,
        }
    targets["files"] = {
        "status": write_status,
        "may_modify": write_status == "authorized",
        "requires_user_confirmation": write_status != "authorized",
    }

    return {
        "boundary_status": boundary_status,
        "expected_scope": expected_mode,
        "actual_scope": actual_mode,
        "targets": targets,
        "notes": [
            "Diagnosis may write only diagnosis reports.",
            "Profile, rule, dataset, casebook, rubric, contribution, and public-sample changes remain preview-only.",
        ],
    }


def make_finding(index: int, dimension: str, text: str, confidence: str, source_type: str) -> dict[str, Any]:
    excerpt = first_excerpt(text, ISSUE_PATTERNS.get(dimension, []))
    severity = "high" if dimension == "authorization_boundary" else "medium"
    evidence_id = f"E{index:03d}"
    return {
        "id": f"F{index:03d}",
        "dimension": dimension,
        "severity": severity,
        "confidence": confidence,
        "conclusion": DIMENSION_LABELS[dimension],
        "evidence": [
            {
                "id": evidence_id,
                "source_type": "input_text",
                "evidence_type": evidence_type_for(dimension),
                "premise_status": premise_status_for(dimension, source_type),
                "excerpt": excerpt,
                "supports": "The input contains language associated with this diagnosis dimension.",
            }
        ],
        "premise_status": premise_status_for(dimension, source_type),
        "recommendation": recommendation_for(dimension),
    }


def evidence_type_for(dimension: str) -> str:
    return {
        "authorization_boundary": "authorization_signal",
        "response_mode_mismatch": "mode_signal",
        "context_pollution": "context_signal",
        "premise_validation": "premise_signal",
        "intent_preservation": "goal_signal",
    }[dimension]


def premise_status_for(dimension: str, source_type: str) -> str:
    if source_type == "conversation" and dimension in {"authorization_boundary", "response_mode_mismatch"}:
        return "inferred"
    if dimension == "premise_validation":
        return "unknown"
    return "user-stated" if source_type == "manual" else "inferred"


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


def build_premises(
    text: str,
    source_type: str,
    expected_mode: str,
    actual_mode: str,
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    evidence_ids = [
        evidence["id"]
        for finding in findings
        for evidence in finding.get("evidence", [])
        if evidence.get("id")
    ]
    status = "user-stated" if source_type == "manual" else "inferred"
    premises = [
        {
            "id": "P001",
            "statement": f"The expected interaction mode was {expected_mode}.",
            "status": status,
            "confidence": "medium" if expected_mode != "diagnosis" else "low",
            "evidence": evidence_ids[:2],
        },
        {
            "id": "P002",
            "statement": f"The Agent's actual behavior mode was {actual_mode}.",
            "status": "unknown" if actual_mode == "unknown" else "inferred",
            "confidence": "low" if actual_mode == "unknown" else "medium",
            "evidence": evidence_ids[:2],
        },
        {
            "id": "P003",
            "statement": "No durable local asset change was authorized by the diagnosis itself.",
            "status": "verified",
            "confidence": "high",
            "evidence": ["diagnose_no_mutation_policy"],
        },
    ]
    if "assume" in text.lower():
        premises.append(
            {
                "id": "P004",
                "statement": "At least one decision-critical claim may be an assumption rather than verified fact.",
                "status": "assumed",
                "confidence": "medium",
                "evidence": evidence_ids,
            }
        )
    return premises


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


def completion_questions(
    source_type: str,
    detected: list[str],
    expected_mode: str,
    actual_mode: str,
) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = [
        {
            "id": "Q001",
            "targets": ["response_mode"],
            "question": "What exact user wording defined the expected response mode?",
            "why_it_matters": "It separates user intent from the Agent's interpretation.",
        }
    ]
    if "authorization_boundary" in detected:
        questions.append(
            {
                "id": "Q002",
                "targets": ["authorization_scope", "files"],
                "question": "Did the user explicitly authorize file writes or durable state changes?",
                "why_it_matters": "It determines whether the observed action was within scope or unauthorized.",
            }
        )
    if "context_pollution" in detected:
        questions.append(
            {
                "id": "Q003",
                "targets": ["context_pollution"],
                "question": "Which prior context was still relevant, and which context should have been excluded?",
                "why_it_matters": "It distinguishes useful continuity from stale-context contamination.",
            }
        )
    if "premise_validation" in detected:
        questions.append(
            {
                "id": "Q004",
                "targets": ["premise_validation"],
                "question": "What evidence, if any, supports the decision-critical premise?",
                "why_it_matters": "It prevents user-stated or assumed claims from being treated as verified.",
            }
        )
    if source_type == "manual" or actual_mode == "unknown":
        questions.append(
            {
                "id": "Q005",
                "targets": ["actual_mode", "evidence"],
                "question": "What did the Agent actually do or say that shows the failure?",
                "why_it_matters": "Manual reports need concrete Agent behavior before high-confidence conclusions.",
            }
        )
    if expected_mode != actual_mode:
        questions.append(
            {
                "id": "Q006",
                "targets": ["expected_vs_actual_mode"],
                "question": "Was there any earlier instruction that allowed the Agent to change modes?",
                "why_it_matters": "Earlier authorization can change the interpretation of the current turn.",
            }
        )
    return questions[:4]


def learning_note_for(concept: str) -> str:
    return {
        "authorization_boundary": "File-capable Agents need explicit permission before crossing from discussion into mutation.",
        "response_mode_mismatch": "Mode labels help keep advice, verification, drafting, execution, and persistence separate.",
        "context_pollution": "Long-running context is useful only when the Agent can tell current scope from stale assumptions.",
        "premise_validation": "Decision-critical claims should be labeled as user-stated, inferred, assumed, verified, or unknown.",
        "intent_preservation": "Risk handling should protect the user's goal rather than replacing it with a safer but different goal.",
    }[concept]


def playbook_path_for(concept: str) -> str:
    return {
        "authorization_boundary": "docs/playbook/authorization-boundary.md",
        "response_mode_mismatch": "docs/playbook/response-mode.md",
        "context_pollution": "docs/playbook/context-pollution.md",
        "premise_validation": "docs/playbook/premise-validation.md",
        "intent_preservation": "docs/playbook/diagnose-vs-eval.md",
    }[concept]


def generated_candidates(primary: str, detected: list[str], findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source_findings = [finding["id"] for finding in findings]
    candidates: list[dict[str, Any]] = []
    profile_evidence = [
        {
            "source_type": "diagnosis_finding",
            "reference": finding["id"],
            "excerpt": finding.get("conclusion", ""),
        }
        for finding in findings
    ]
    candidates.append(
        {
            "type": "profile",
            "artifact_type": "profile_update",
            "status": "preview_only",
            "source_findings": list(source_findings),
            "primary_issue": primary,
            "profile_scope": "project",
            "requires_user_confirmation": True,
            "auto_apply": False,
            "writes_local_asset": False,
            "confirmation_state": {
                "status": "awaiting_user_confirmation",
                "confirmed_by": None,
                "confirmed_at": None,
            },
            "evidence": profile_evidence,
            "impact_scope": {
                "local_files": [".intent-quality/profile/project-profile.yaml"],
                "behavior": [
                    f"Future project-local collaboration can treat {primary} as a reviewable pattern."
                ],
                "non_goals": [
                    "Does not edit the project profile until the user explicitly applies it.",
                    "Does not create global, cross-project, or broad personal memory.",
                ],
            },
            "rollback_plan": {
                "reversible": True,
                "boundary": "Only the proposed project-profile change would be in scope if later applied.",
                "required_snapshot": "Review the project profile before any confirmed application.",
            },
            "stale_memory_warning": {
                "status": "possible" if "context_pollution" in detected else "none",
                "reason": "Diagnosis-derived profile updates can become stale if old context no longer applies.",
                "requires_user_review": True,
            },
            "preview": {
                "title": f"profile_update candidate for {primary}",
                "summary": "Pending project-local profile suggestion derived from diagnosis evidence.",
                "included_dimensions": list(detected),
                "pending_only": True,
                "requires_user_confirmation": True,
            },
        }
    )
    base = [
        ("case", "casebook_entry", "Reviewable case draft from diagnosis findings."),
        ("eval", "eval_sample", "Reviewable eval sample draft from expected versus actual behavior."),
        ("rule", "rule_update", "Optional local rule suggestion for future pre-action prevention."),
        ("contribution", "contribution_package", "Optional anonymized contribution package draft."),
        ("public_sample", "public_candidate", "Optional public-sample relevance note only."),
    ]
    for candidate_type, artifact_type, summary in base:
        candidates.append(
            {
                "type": candidate_type,
                "artifact_type": artifact_type,
                "status": "preview_only",
                "source_findings": list(source_findings),
                "primary_issue": primary,
                "requires_user_confirmation": True,
                "auto_apply": False,
                "writes_local_asset": False,
                "preview": {
                    "title": f"{artifact_type} candidate for {primary}",
                    "summary": summary,
                    "included_dimensions": list(detected),
                },
            }
        )
    return candidates
