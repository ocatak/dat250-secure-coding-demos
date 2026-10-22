"""A filename sanitizer as it is often written - and a safer version."""
import os


def naive_safe_name(name: str) -> str:
    # "remove path traversal"
    return name.replace("../", "")


def safe_name(name: str) -> str:
    # Keep only the final path component and reject anything odd
    base = os.path.basename(name)
    if base in ("", ".", "..") or "\x00" in base:
        raise ValueError("invalid filename")
    return base
