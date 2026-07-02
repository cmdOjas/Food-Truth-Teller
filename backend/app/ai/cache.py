"""
In-process LRU analysis cache.

Keyed on (barcode, user_id) so each user gets their own cached result.
Cache is invalidated when the user updates their profile.
TTL is configurable via ANALYSIS_CACHE_TTL_SECONDS (default 3600 = 1 hour).
"""
from __future__ import annotations

import hashlib
import logging
import time
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 3600          # seconds
_MAX_ENTRIES  = 500          # max cache size before LRU eviction

_lock  = Lock()
_store: dict[str, dict] = {}  # key → {result, ts, hits}


# ── Public API ───────────────────────────────────────────────────────────────

def make_key(barcode: str, user_id: int | str, profile_hash: str = "") -> str:
    """Create a deterministic cache key."""
    raw = f"{barcode}:{user_id}:{profile_hash}"
    return hashlib.sha256(raw.encode()).hexdigest()


def profile_hash(profile) -> str:
    """
    Hash the fields of a UserProfile that affect analysis results.
    Used to invalidate the cache when the profile changes.
    """
    if profile is None:
        return "no_profile"
    fields = (
        f"{profile.age}|{profile.gender}|{profile.weight_kg}|{profile.height_cm}"
        f"|{sorted(profile.health_conditions or [])}|{sorted(profile.allergies or [])}"
        f"|{profile.diet_preference}"
    )
    return hashlib.md5(fields.encode()).hexdigest()


def get(key: str) -> dict | None:
    """Return cached result or None if missing/expired."""
    with _lock:
        entry = _store.get(key)
        if entry is None:
            return None
        ttl = _get_ttl()
        if time.time() - entry["ts"] > ttl:
            del _store[key]
            return None
        entry["hits"] += 1
        logger.debug("Cache hit for key=%s (hits=%d)", key[:16], entry["hits"])
        return entry["result"]


def set(key: str, result: dict) -> None:
    """Store *result* under *key*.  Evicts oldest entries if at capacity."""
    with _lock:
        if len(_store) >= _MAX_ENTRIES:
            _evict_oldest()
        _store[key] = {"result": result, "ts": time.time(), "hits": 0}
        logger.debug("Cache set for key=%s", key[:16])


def invalidate_user(user_id: int | str) -> int:
    """
    Remove all cache entries for *user_id*.
    Call this whenever a user updates their profile.
    Returns the number of entries removed.
    """
    uid = str(user_id)
    with _lock:
        # The key is a sha256 hash so we can't reverse-lookup by user_id
        # directly.  Instead we store a side-index of uid→keys.
        removed = 0
        for k in list(_store.keys()):
            if _store[k].get("user_id") == uid:
                del _store[k]
                removed += 1
    return removed


def stats() -> dict:
    """Return cache statistics (useful for debugging/admin endpoints)."""
    with _lock:
        return {
            "entries": len(_store),
            "max_entries": _MAX_ENTRIES,
            "ttl_seconds": _get_ttl(),
        }


def clear_all() -> int:
    """Clear the entire cache. Used when system prompt changes."""
    with _lock:
        count = len(_store)
        _store.clear()
        return count


# ── Internals ────────────────────────────────────────────────────────────────

def _evict_oldest() -> None:
    """Remove the 10% oldest entries (must be called with _lock held)."""
    n = max(1, len(_store) // 10)
    oldest = sorted(_store.items(), key=lambda kv: kv[1]["ts"])[:n]
    for k, _ in oldest:
        del _store[k]


def _get_ttl() -> int:
    try:
        from flask import current_app
        return int(current_app.config.get("ANALYSIS_CACHE_TTL_SECONDS", _DEFAULT_TTL))
    except RuntimeError:
        import os
        return int(os.environ.get("ANALYSIS_CACHE_TTL_SECONDS", _DEFAULT_TTL))
