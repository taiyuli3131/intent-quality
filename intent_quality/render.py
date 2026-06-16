from __future__ import annotations

from pathlib import Path
from typing import Any


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def render_diagnosis_markdown(data: dict[str, Any]) -> str:
    findings = data.get("findings", [])
    missing = data.get("missing_information", [])
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
        "",
        "## Findings",
        "",
    ]
    if findings:
        for finding in findings:
            lines.extend(
                [
                    f"### {finding['id']} - {finding['dimension']}",
                    "",
                    f"- Severity: `{finding['severity']}`",
                    f"- Confidence: `{finding['confidence']}`",
                    f"- Conclusion: {finding['conclusion']}",
                    f"- Recommendation: {finding['recommendation']}",
                    "",
                    "Evidence:",
                ]
            )
            for evidence in finding.get("evidence", []):
                lines.append(f"- `{evidence['source_type']}`: {evidence['excerpt']}")
            lines.append("")
    else:
        lines.extend(["No material findings were detected from the available input.", ""])

    lines.extend(["## Missing Information", ""])
    if missing:
        lines.extend(f"- {item}" for item in missing)
    else:
        lines.append("- None identified.")

    lines.extend(
        [
            "",
            "## Learning Feedback",
            "",
            f"- Concepts: {', '.join(concepts) or 'none'}",
            f"- User tip: {data.get('learning_feedback', {}).get('user_tip', 'No specific tip generated.')}",
            "",
            "## Generated Candidates",
            "",
        ]
    )
    for key, value in data.get("generated_candidates", {}).items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    return "\n".join(lines)

