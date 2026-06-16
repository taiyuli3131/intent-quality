from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable

from .paths import find_project_root


def run_check(args: Any) -> int:
    root = find_project_root(Path(args.root) if args.root else None)
    checker_path = root / "tools" / "local_loop_check.py"
    if not checker_path.exists():
        print(f"check failed: {checker_path} does not exist")
        return 1

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

    if errors:
        print("local loop checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("local loop checks passed")
    print("checked: public index, external candidates, pending suggestions, contribution packages")
    print("mode: read-only; no rules, profiles, datasets, casebooks, or submissions were modified")
    return 0


def load_checker(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("intent_quality_local_loop_check", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load checker from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

