import os
from typing import Tuple


def is_windows_style_path(path: str) -> bool:
    """Detect Windows paths that include drive letters (e.g., C:\\path)."""
    drive, _ = os.path.splitdrive(path)
    return bool(drive)


def running_in_docker() -> bool:
    """Return True when the code runs inside a Docker container."""
    return os.path.exists("/.dockerenv")


def resolve_sadtalker_dir(raw_dir: str, docker_override: str) -> Tuple[str, bool, bool]:
    """
    Normalize the SadTalker installation directory.
    When inside Docker, prefer the override path (defaults to /app/sadtalker) to support Windows host paths.
    Returns the resolved path, a bool indicating whether an override was applied, and whether the original value used a Windows-style path.
    """
    resolved = os.path.abspath(raw_dir)
    override_used = False
    windows_path = is_windows_style_path(raw_dir)

    if running_in_docker():
        if docker_override:
            resolved = os.path.abspath(docker_override)
            override_used = True
        elif windows_path:
            resolved = os.path.abspath("/app/sadtalker")

    return resolved, override_used, windows_path
