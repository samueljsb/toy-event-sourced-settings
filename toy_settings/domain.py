from __future__ import annotations


def normalize_key(key: str) -> str:
    return key.strip().replace(" ", "_").replace("-", "_").upper()
