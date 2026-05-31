"""Track ingested file hashes to prevent duplicate vectors."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from rag.ingestion.config import REGISTRY_PATH


def _load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {"files": {}}
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"files": {}}


def _save_registry(data: dict) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def compute_file_hash(file_path: Path) -> str:
    """SHA-256 hash of file bytes for deduplication."""
    import hashlib

    digest = hashlib.sha256()
    with file_path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_duplicate(file_hash: str) -> bool:
    """True if this file hash was already ingested."""
    reg = _load_registry()
    return file_hash in reg.get("files", {})


def register_file(
    file_hash: str,
    source: str,
    chunk_count: int,
) -> None:
    """Record a successful ingestion."""
    reg = _load_registry()
    reg.setdefault("files", {})[file_hash] = {
        "source": source,
        "chunk_count": chunk_count,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_registry(reg)


def remove_file_hash(file_hash: str) -> None:
    """Remove a hash from the registry (e.g. before re-index)."""
    reg = _load_registry()
    reg.get("files", {}).pop(file_hash, None)
    _save_registry(reg)


def clear_registry() -> None:
    """Wipe ingestion registry (used when resetting collection)."""
    if REGISTRY_PATH.exists():
        REGISTRY_PATH.unlink()
