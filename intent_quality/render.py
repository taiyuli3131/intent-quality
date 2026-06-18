from __future__ import annotations

from pathlib import Path
from typing import Any


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def render_diagnosis_markdown(data: dict[str, Any]) -> str:
    findings = data.get("findings", [])
    questions = data.get("completion_questions", [])
    premises = data.get("premises", [])
    auth_scope = data.get("authorization_scope", {})
    concepts = data.get("learning_feedback", {}).get("concepts", [])
    lines = [
        f"# Diagnosis {data['diagnosis_id']}",
        "",
        "## Summary",
        "",
        f"- Primary issue: `{data['summary']['primary_issue']}`",
        f"- Secondary issues: {', '.join(data['summary'].get('secondary_issues', [])) or 'none'}",
        f"- Overall confidence: `{data['summary']['overall_confidence']}`",
        "",
        "## Interaction State",
        "",
        f"- Expected mode: `{data['interaction_state']['expected_mode']}`",
        f"- Actual mode: `{data['interaction_state']['actual_mode']}`",
        f"- Mismatch: `{str(data['interaction_state']['mismatch']).lower()}`",
        f"- Analysis: {data['interaction_state'].get('analysis', 'No mode analysis available.')}",
        "",
        "## Authorization Scope",
        "",
        f"- Boundary status: `{auth_scope.get('boundary_status', 'unknown')}`",
        f"- Expected scope: `{auth_scope.get('expected_scope', 'unknown')}`",
        f"- Actual scope: `{auth_scope.get('actual_scope', 'unknown')}`",
        "",
        "| Target | Status | May Modify | Requires Confirmation |",
        "| --- | --- | --- | --- |",
    ]
    for target, detail in auth_scope.get("targets", {}).items():
        lines.append(
            f"| {target} | `{detail.get('status', 'unknown')}` | "
            f"`{str(detail.get('may_modify', False)).lower()}` | "
            f"`{str(detail.get('requires_user_confirmation', True)).lower()}` |"
        )
    if auth_scope.get("notes"):
        lines.extend(["", "Notes:"])
        lines.extend(f"- {note}" for note in auth_scope.get("notes", []))

    dimensions = data.get("dimensions", {})
    if dimensions:
        lines.extend(
            [
                "",
                "## Dimensions",
                "",
                "| Dimension | Score | Confidence | Findings |",
                "| --- | --- | --- | --- |",
            ]
        )
        for dimension, detail in dimensions.items():
            findings_list = ", ".join(detail.get("findings", [])) or "none"
            lines.append(
                f"| `{dimension}` | `{detail.get('score', 'unknown')}` | "
                f"`{detail.get('confidence', 'unknown')}` | {findings_list} |"
            )

    lines.extend(
        [
            "",
            "## Premises",
            "",
            "| ID | Status | Confidence | Statement | Evidence |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for premise in premises:
        evidence = ", ".join(premise.get("evidence", [])) or "none"
        lines.append(
            f"| {premise.get('id', '')} | `{premise.get('status', 'unknown')}` | "
            f"`{premise.get('confidence', 'unknown')}` | {premise.get('statement', '')} | {evidence} |"
        )

    lines.extend(
        [
            "",
            "## Findings",
            "",
        ]
    )
    if findings:
        for finding in findings:
            lines.extend(
                [
                    f"### {finding['id']} - {finding['dimension']}",
                    "",
                    f"- Severity: `{finding['severity']}`",
                    f"- Confidence: `{finding['confidence']}`",
                    f"- Premise status: `{finding.get('premise_status', 'unknown')}`",
                    f"- Conclusion: {finding['conclusion']}",
                    f"- Recommendation: {finding['recommendation']}",
                    "",
                    "Evidence:",
                ]
            )
            for evidence in finding.get("evidence", []):
                lines.append(
                    f"- `{evidence.get('id', '')}` "
                    f"`{evidence.get('source_type', 'unknown')}`/"
                    f"`{evidence.get('evidence_type', 'unknown')}` "
                    f"premise `{evidence.get('premise_status', 'unknown')}`: "
                    f"{evidence.get('excerpt', '')}"
                )
                if evidence.get("supports"):
                    lines.append(f"  - Supports: {evidence['supports']}")
            lines.append("")
    else:
        lines.extend(["No material findings were detected from the available input.", ""])

    lines.extend(["## Targeted Completion Questions", ""])
    if questions:
        for item in questions:
            targets = ", ".join(item.get("targets", [])) or "general"
            lines.append(f"- `{item.get('id', '')}` {item.get('question', '')}")
            lines.append(f"  - Targets: {targets}")
            lines.append(f"  - Why it matters: {item.get('why_it_matters', '')}")
    else:
        lines.append("- None identified.")

    lines.extend(
        [
            "",
            "## Learning Feedback",
            "",
            f"- User tip: {data.get('learning_feedback', {}).get('user_tip', 'No specific tip generated.')}",
            f"- Agent tip: {data.get('learning_feedback', {}).get('agent_tip', 'No specific tip generated.')}",
            "",
            "| Concept | Why It Matters | Playbook |",
            "| --- | --- | --- |",
        ]
    )
    for item in concepts:
        if isinstance(item, dict):
            lines.append(
                f"| `{item.get('concept', '')}` | {item.get('why_it_matters', '')} | {item.get('playbook', '')} |"
            )
        else:
            lines.append(f"| `{item}` | See playbook. | |")

    lines.extend(
        [
            "",
            "## Generated Candidates",
            "",
            "Fields shown below map to `type`, `artifact_type`, `status`, `auto_apply`, `writes_local_asset`, and `requires_user_confirmation`.",
            "",
            "Candidate previews are review data only. `preview_only`, `auto_apply: false`, and `writes_local_asset: false` mean these rows do not apply changes or create local assets.",
            "",
            "| Type | Artifact | Status | Auto Apply | Writes Local Asset | Requires Confirmation |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for candidate in data.get("generated_candidates", []):
        lines.append(
            f"| {candidate.get('type', '')} | `{candidate.get('artifact_type', '')}` | "
            f"`{candidate.get('status', '')}` | `{str(candidate.get('auto_apply', False)).lower()}` | "
            f"`{str(candidate.get('writes_local_asset', False)).lower()}` | "
            f"`{str(candidate.get('requires_user_confirmation', True)).lower()}` |"
        )
    preview_lines = []
    for candidate in data.get("generated_candidates", []):
        preview = candidate.get("preview", {})
        if preview:
            included = ", ".join(preview.get("included_dimensions", [])) or "none"
            extra = ""
            if candidate.get("artifact_type") == "profile_update":
                stale = candidate.get("stale_memory_warning", {})
                rollback = candidate.get("rollback_plan", {})
                extra = (
                    f" Scope: `{candidate.get('profile_scope', 'unknown')}`. "
                    f"Confirmation: `{candidate.get('confirmation_state', {}).get('status', 'unknown')}`. "
                    f"Stale warning: `{stale.get('status', 'unknown')}`. "
                    f"Rollback reversible: `{str(rollback.get('reversible', False)).lower()}`."
                )
            preview_lines.append(
                f"- `{candidate.get('type', '')}`/`{candidate.get('artifact_type', '')}`: "
                f"{preview.get('title', 'Untitled preview')} - "
                f"{preview.get('summary', 'No summary provided.')} "
                f"Included dimensions: {included}.{extra}"
            )
    if preview_lines:
        lines.extend(["", "Preview details:"])
        lines.extend(preview_lines)
    lines.append("")
    return "\n".join(lines)
