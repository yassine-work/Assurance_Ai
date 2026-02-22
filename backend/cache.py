"""
In-memory prediction cache.

WHY:  Running the ML model is the most expensive operation in the API
      (~50-200ms per prediction). If two users send the exact same input,
      there's no reason to re-compute — we serve the cached result instantly.

HOW:  We hash the input dict (sorted keys → JSON string → SHA-256) and
      store the result in a dict. We cap the cache at MAX_SIZE entries
      and expire entries after TTL seconds.

IN PRODUCTION: You'd swap this for Redis for persistence across restarts
               and shared caching across multiple API instances.
"""

import hashlib
import json
import time
from threading import Lock

MAX_SIZE = 1000      # Maximum cached predictions
TTL_SECONDS = 3600   # Cache entries expire after 1 hour

_cache: dict[str, dict] = {}
_timestamps: dict[str, float] = {}
_lock = Lock()
_stats = {"hits": 0, "misses": 0}


def _make_key(input_data: dict) -> str:
    """Create a deterministic hash key from input data."""
    # Sort keys so {"a":1,"b":2} and {"b":2,"a":1} produce the same key
    canonical = json.dumps(input_data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def cache_get(input_data: dict) -> dict | None:
    """Look up a cached prediction result. Returns None on miss."""
    key = _make_key(input_data)
    with _lock:
        if key in _cache:
            # Check if expired
            if time.time() - _timestamps[key] > TTL_SECONDS:
                del _cache[key]
                del _timestamps[key]
                _stats["misses"] += 1
                return None
            _stats["hits"] += 1
            return _cache[key]
        _stats["misses"] += 1
        return None


def cache_set(input_data: dict, result: dict) -> None:
    """Store a prediction result in the cache."""
    key = _make_key(input_data)
    with _lock:
        # Evict oldest entries if cache is full
        if len(_cache) >= MAX_SIZE:
            oldest_key = min(_timestamps, key=_timestamps.get)
            del _cache[oldest_key]
            del _timestamps[oldest_key]
        _cache[key] = result
        _timestamps[key] = time.time()


def cache_clear() -> int:
    """Clear the entire cache. Returns number of entries removed."""
    with _lock:
        count = len(_cache)
        _cache.clear()
        _timestamps.clear()
        return count


def cache_stats() -> dict:
    """Return cache performance statistics."""
    with _lock:
        total = _stats["hits"] + _stats["misses"]
        return {
            "size": len(_cache),
            "max_size": MAX_SIZE,
            "ttl_seconds": TTL_SECONDS,
            "hits": _stats["hits"],
            "misses": _stats["misses"],
            "hit_rate": round(_stats["hits"] / total * 100, 1) if total > 0 else 0,
        }
