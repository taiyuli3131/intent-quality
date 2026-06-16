from __future__ import annotations

from pathlib import Path


LOCAL_DIR = ".intent-quality"


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for path in [current, *current.parents]:
        if (path / "PROJECT-INFO.md").exists() and (path / "SCHEMAS.md").exists():
            return path
        if (path / ".git").exists():
            return path
    return current


def local_state_dir(root: Path) -> Path:
    return root / LOCAL_DIR


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def next_numbered_id(directory: Path, prefix: str, suffix: str = ".yaml") -> str:
    existing = sorted(directory.glob(f"{prefix}_*{suffix}"))
    numbers: list[int] = []
    for path in existing:
        stem = path.stem
        try:
            numbers.append(int(stem.rsplit("_", 1)[1]))
        except (IndexError, ValueError):
            continue
    return f"{prefix}_{(max(numbers) + 1) if numbers else 1:03d}"

