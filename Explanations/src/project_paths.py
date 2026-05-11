from __future__ import annotations

from pathlib import Path


EXPLANATIONS_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = EXPLANATIONS_ROOT.parent


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return EXPLANATIONS_ROOT / candidate


def resolve_repository_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return REPOSITORY_ROOT / candidate


def owlready_file_uri(path: str | Path) -> str:
    resolved = Path(path).resolve()
    if resolved.drive:
        return "file://" + resolved.as_posix()
    return resolved.as_uri()
