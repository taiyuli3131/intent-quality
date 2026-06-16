from __future__ import annotations

import argparse
from typing import Sequence

from . import __version__
from .check import run_check
from .contribution import run_contribute_create, run_contribute_review
from .diagnose import run_conversation, run_manual
from .eval import run_eval
from .public_sync import run_public_fetch, run_public_suggest
from .suggestions import run_list


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="intent-quality", description="Local-first Agent collaboration quality CLI.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    diagnose = subparsers.add_parser("diagnose", help="Generate a local diagnosis report.")
    diagnose.add_argument("--root", help="Project root. Defaults to auto-detection.")
    diagnose.add_argument("--description", help="Manual issue description for non-interactive use.")
    source = diagnose.add_mutually_exclusive_group(required=True)
    source.add_argument("--manual", action="store_true", help="Create a diagnosis from a manual description.")
    source.add_argument("--conversation", help="Create a diagnosis from a conversation Markdown file.")
    diagnose.set_defaults(func=run_diagnose)

    eval_parser = subparsers.add_parser("eval", help="Evaluate a response against a collaboration-quality dataset.")
    eval_parser.add_argument("dataset", help="Dataset YAML path.")
    eval_parser.add_argument("--response", required=True, help="Response Markdown file to score.")
    eval_parser.add_argument("--eval-id", help="Run only one eval case.")
    eval_parser.add_argument("--output", help="Optional YAML output path.")
    eval_parser.set_defaults(func=run_eval)

    suggest = subparsers.add_parser("suggest", help="Inspect local suggestions.")
    suggest_sub = suggest.add_subparsers(dest="suggest_command", required=True)
    suggest_list = suggest_sub.add_parser("list", help="List pending suggestions.")
    suggest_list.add_argument("--root", help="Project root. Defaults to auto-detection.")
    suggest_list.add_argument("--path", help="Suggestion YAML path. Defaults to .intent-quality/suggestions/pending-suggestions.yaml.")
    suggest_list.set_defaults(func=run_list)

    public = subparsers.add_parser("public", help="Fetch public indexes and generate reviewable suggestions.")
    public_sub = public.add_subparsers(dest="public_command", required=True)
    public_fetch = public_sub.add_parser("fetch", help="Fetch the public index only.")
    public_fetch.add_argument("--root", help="Project root. Defaults to auto-detection.")
    public_fetch.add_argument("--index", help="Source public index path. Defaults to public-registry/index.yaml.")
    public_fetch.set_defaults(func=run_public_fetch)
    public_suggest = public_sub.add_parser("suggest", help="Generate external candidates and pending suggestions.")
    public_suggest.add_argument("--root", help="Project root. Defaults to auto-detection.")
    public_suggest.add_argument("--index", help="Public index path. Defaults to .intent-quality/public/index.yaml.")
    public_suggest.add_argument("--entry-id", help="Generate suggestions for one public entry.")
    public_suggest.set_defaults(func=run_public_suggest)

    contribute = subparsers.add_parser("contribute", help="Create and review local contribution packages.")
    contribute_sub = contribute.add_subparsers(dest="contribute_command", required=True)
    contribute_create = contribute_sub.add_parser("create", help="Create a pending local contribution package.")
    contribute_create.add_argument("--root", help="Project root. Defaults to auto-detection.")
    contribute_create.add_argument("--diagnosis", help="Diagnosis YAML to generalize into a contribution package.")
    contribute_create.add_argument("--description", help="Manual issue description when no diagnosis file is supplied.")
    contribute_create.set_defaults(func=run_contribute_create)
    contribute_review = contribute_sub.add_parser("review", help="Review a pending local contribution package.")
    contribute_review.add_argument("--root", help="Project root. Defaults to auto-detection.")
    contribute_review.add_argument("--package", help="Contribution package directory. Defaults to newest pending package.")
    contribute_review.set_defaults(func=run_contribute_review)

    check = subparsers.add_parser("check", help="Run read-only local loop checks.")
    check.add_argument("--root", help="Project root. Defaults to auto-detection.")
    check.set_defaults(func=run_check)
    return parser


def run_diagnose(args: argparse.Namespace) -> int:
    if args.manual:
        return run_manual(args)
    return run_conversation(args)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
