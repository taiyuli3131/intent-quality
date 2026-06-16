from __future__ import annotations

from pathlib import Path
from typing import Any

from .paths import find_project_root, local_state_dir
from .schemas import load_yaml


def run_list(args: Any) -> int:
    root = find_project_root(Path(args.root) if args.root else None)
    path = Path(args.path).resolve() if args.path else local_state_dir(root) / "suggestions" / "pending-suggestions.yaml"
    if not path.exists():
        print(f"no pending suggestions found at {path}")
        return 0

    data = load_yaml(path)
    suggestions = data.get("suggestions", [])
    if not suggestions:
        print(f"no pending suggestions found at {path}")
        return 0

    print(f"pending suggestions: {path}")
    for item in suggestions:
        proposal = item.get("proposal", {})
        print(f"\n{item.get('suggestion_id', '<unknown>')}")
        print(f"  type: {item.get('suggestion_type', '<unknown>')}")
        print(f"  status: {item.get('status', '<unknown>')}")
        print(f"  risk: {item.get('risk_level', '<unknown>')}")
        print(f"  target: {proposal.get('target', '<none>')}")
        print(f"  title: {proposal.get('title', '<untitled>')}")
        print(f"  requires confirmation: {item.get('requires_user_confirmation') is True}")
    print("\nmode: list only; no suggestions were applied")
    return 0

