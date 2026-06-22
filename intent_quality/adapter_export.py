from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml

from .eval import SCORING_METHOD
from .schemas import load_yaml, write_yaml


ADAPTER_EXPORT_SCHEMA_VERSION = "0.3.0"
SUPPORTED_FORMATS = {"promptfoo", "deepeval", "pydantic-evals"}


def run_adapter_export(args: argparse.Namespace) -> int:
    dataset_path = Path(args.dataset).resolve()
    dataset = load_yaml(dataset_path)
    output = build_adapter_export(dataset, args.format, Path(args.dataset))

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(output_path, output)
        print(f"adapter export draft written: {output_path}")
    else:
        print(yaml.safe_dump(output, sort_keys=False, allow_unicode=False))
    return 0


def build_adapter_export(dataset: dict[str, Any], adapter_format: str, dataset_path: Path | None = None) -> dict[str, Any]:
    if adapter_format not in SUPPORTED_FORMATS:
        raise ValueError(f"unsupported adapter format: {adapter_format}")

    source = build_source(dataset, dataset_path)
    export = {
        "schema_version": ADAPTER_EXPORT_SCHEMA_VERSION,
        "export_id": stable_export_id(dataset, adapter_format),
        "format": adapter_format,
        "experimental": True,
        "internal_only": True,
        "generated_by": "intent-quality",
        "source": source,
        "scoring_method": dict(SCORING_METHOD),
        "safety": {
            "runs_external_framework": False,
            "core_runtime_dependency": False,
            "changes_default_scorer": False,
            "applies_results": False,
            "mutates_assets": False,
            "requires_user_confirmation_before_use": True,
        },
        "limitations": [
            "Draft export only; intent-quality does not run this adapter in v0.3.",
            "The default scorer remains the local heuristic marker scorer, not a complete semantic evaluator.",
            "Review generated adapter files before using them in external tooling.",
        ],
        "draft": build_draft(dataset, adapter_format),
    }
    return export


def build_source(dataset: dict[str, Any], dataset_path: Path | None) -> dict[str, Any]:
    cases = dataset.get("cases", [])
    source = {
        "dataset_id": dataset.get("dataset_id"),
        "dataset_schema_version": dataset.get("schema_version"),
        "rubric_version": dataset.get("rubric_version"),
        "visibility": dataset.get("visibility"),
        "status": dataset.get("status"),
        "case_count": len(cases) if isinstance(cases, list) else 0,
    }
    if dataset_path is not None:
        source["dataset_path"] = str(dataset_path)
    return source


def build_draft(dataset: dict[str, Any], adapter_format: str) -> dict[str, Any]:
    if adapter_format == "promptfoo":
        return build_promptfoo_draft(dataset)
    if adapter_format == "deepeval":
        return build_deepeval_draft(dataset)
    return build_pydantic_evals_draft(dataset)


def build_promptfoo_draft(dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "config_type": "promptfoo_config_draft",
        "description": "Experimental draft for mapping intent-quality cases into Promptfoo-style tests.",
        "prompts": ["{{agent_response}}"],
        "providers": ["manual-review-placeholder"],
        "tests": [
            {
                "description": case.get("eval_id"),
                "vars": {
                    "user_prompt": case.get("input", {}).get("user_prompt"),
                    "context": case.get("input", {}).get("context", {}),
                    "agent_response": "<response under test>",
                },
                "metadata": case_metadata(case),
                "assertions_draft": [
                    {"type": "must_observe", "values": case.get("expected", {}).get("must", [])},
                    {"type": "must_not_observe", "values": case.get("expected", {}).get("must_not", [])},
                ],
            }
            for case in dataset.get("cases", [])
        ],
    }


def build_deepeval_draft(dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "config_type": "deepeval_test_case_draft",
        "description": "Experimental draft for hand-reviewing DeepEval-style test case mapping.",
        "metrics_draft": [
            {
                "name": "CollaborationQualityMarkers",
                "source": "intent-quality heuristic markers",
                "requires_manual_review": True,
            }
        ],
        "test_cases": [
            {
                "name": case.get("eval_id"),
                "input": case.get("input", {}).get("user_prompt"),
                "actual_output": "<response under test>",
                "expected_output": {
                    "response_mode": case.get("expected", {}).get("response_mode"),
                    "must": case.get("expected", {}).get("must", []),
                    "must_not": case.get("expected", {}).get("must_not", []),
                },
                "metadata": case_metadata(case),
            }
            for case in dataset.get("cases", [])
        ],
    }


def build_pydantic_evals_draft(dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "config_type": "pydantic_evals_dataset_draft",
        "description": "Experimental draft for mapping cases into a Pydantic Evals style dataset.",
        "dataset": {
            "name": dataset.get("dataset_id"),
            "cases": [
                {
                    "name": case.get("eval_id"),
                    "inputs": {
                        "user_prompt": case.get("input", {}).get("user_prompt"),
                        "context": case.get("input", {}).get("context", {}),
                        "agent_response": "<response under test>",
                    },
                    "expected_output": {
                        "response_mode": case.get("expected", {}).get("response_mode"),
                        "must": case.get("expected", {}).get("must", []),
                        "must_not": case.get("expected", {}).get("must_not", []),
                    },
                    "metadata": case_metadata(case),
                }
                for case in dataset.get("cases", [])
            ],
        },
    }


def case_metadata(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_case_id": case.get("source_case_id"),
        "primary_risk": case.get("primary_risk"),
        "secondary_risks": case.get("secondary_risks", []),
        "difficulty": case.get("difficulty", "unknown"),
        "blocking_failures": case.get("scoring", {}).get("pass_criteria", {}).get("blocking_failures", []),
    }


def stable_export_id(dataset: dict[str, Any], adapter_format: str) -> str:
    basis = "\n".join(
        [
            str(dataset.get("dataset_id", "unknown")),
            str(dataset.get("schema_version", "unknown")),
            str(dataset.get("rubric_version", "unknown")),
            adapter_format,
        ]
    )
    return "adapter_" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
