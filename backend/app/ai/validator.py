"""
Response validator and JSON extractor.

Phi-3 sometimes wraps JSON in markdown code fences or adds trailing prose.
This module strips all that and returns a validated, normalised dict.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ── Expected JSON schema ────────────────────────────────────────────────────

REQUIRED_KEYS: set[str] = {
    "overall_score",
    "health_rating",
    "summary",
    "pros",
    "cons",
    "warnings",
    "recommended_for",
    "avoid_if",
    "better_alternatives",
    "daily_limit",
    "personalized_advice",
    "confidence",
}

VALID_RATINGS = {"Excellent", "Good", "Fair", "Poor", "Avoid"}

_DEFAULTS: dict[str, Any] = {
    "overall_score": 50,
    "health_rating": "Fair",
    "summary": "Analysis could not be fully completed.",
    "pros": [],
    "cons": [],
    "warnings": [],
    "recommended_for": [],
    "avoid_if": [],
    "better_alternatives": [],
    "daily_limit": "Consult a nutritionist.",
    "personalized_advice": "Unable to generate personalised advice at this time.",
    "confidence": 0.5,
}


def extract_json(raw: str) -> dict:
    """
    Extract and validate the JSON object from *raw* model output.

    Strategy:
    1. Try to parse the whole string directly.
    2. Strip markdown code fences and retry.
    3. Locate the first ``{`` … last ``}`` substring and parse that.
    4. Try to repair truncated JSON by closing open brackets.
    5. If all fail, return a safe default dict.
    """
    text = raw.strip()

    # Attempt 1 — direct parse
    parsed = _try_parse(text)
    if parsed is not None:
        return _normalise(parsed)

    # Attempt 2 — strip ```json ... ``` or ``` ... ```
    stripped = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    parsed = _try_parse(stripped)
    if parsed is not None:
        return _normalise(parsed)

    # Attempt 3 — extract first {...} block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        parsed = _try_parse(text[start : end + 1])
        if parsed is not None:
            return _normalise(parsed)

    # Attempt 4 — repair truncated JSON (Phi-3 cuts off mid-output)
    if start != -1:
        truncated = text[start:]
        repaired = _repair_truncated_json(truncated)
        parsed = _try_parse(repaired)
        if parsed is not None:
            logger.warning("Repaired truncated JSON from model output.")
            return _normalise(parsed)

    logger.warning("Could not extract valid JSON from model output: %s", text[:300])
    return dict(_DEFAULTS)


def _try_parse(text: str) -> dict | None:
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def _repair_truncated_json(text: str) -> str:
    """
    Attempt to close an incomplete JSON object by:
    1. Removing the last incomplete key-value pair if mid-string.
    2. Closing any open arrays with [].
    3. Closing the root object with }.
    """
    # Remove trailing incomplete string value (ends mid-quote)
    # e.g.  "daily_limit": "Do not consum   ← truncated
    text = text.rstrip()

    # Remove trailing comma
    text = text.rstrip(",").rstrip()

    # Close any open string (odd number of unescaped quotes after last complete value)
    # Simple heuristic: if last char is not ] } " or a digit, truncate to last comma/colon
    if text and text[-1] not in ('}', ']', '"', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
        # Find last safe boundary
        for i in range(len(text) - 1, -1, -1):
            if text[i] in (',', '{', '['):
                text = text[:i].rstrip().rstrip(",")
                break

    # Count unclosed [ and {
    opens = 0
    in_string = False
    escape_next = False
    for ch in text:
        if escape_next:
            escape_next = False
            continue
        if ch == '\\':
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            opens += 1
        elif ch == '}':
            opens -= 1
        elif ch == '[':
            opens += 1
        elif ch == ']':
            opens -= 1

    # Close outstanding opens
    # We need to close arrays first, then objects
    # Since we don't track types, use a simpler approach: just append }
    # and wrap arrays inline — the normaliser will handle missing fields
    closing = ''
    # Re-scan to properly close
    stack = []
    in_string = False
    escape_next = False
    for ch in text:
        if escape_next:
            escape_next = False
            continue
        if ch == '\\':
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch in ('{', '['):
            stack.append(ch)
        elif ch == '}' and stack and stack[-1] == '{':
            stack.pop()
        elif ch == ']' and stack and stack[-1] == '[':
            stack.pop()

    for bracket in reversed(stack):
        closing += ']' if bracket == '[' else '}'

    return text + closing


def _normalise(data: dict) -> dict:
    """Fill missing keys, coerce types, clamp ranges."""
    result = dict(_DEFAULTS)
    result.update(data)

    # Coerce numeric fields
    try:
        result["overall_score"] = max(0, min(100, int(float(result["overall_score"]))))
    except (ValueError, TypeError):
        result["overall_score"] = _DEFAULTS["overall_score"]

    try:
        result["confidence"] = max(0.0, min(1.0, float(result["confidence"])))
    except (ValueError, TypeError):
        result["confidence"] = _DEFAULTS["confidence"]

    # Ensure lists are lists
    for key in ("pros", "cons", "warnings", "recommended_for", "avoid_if", "better_alternatives"):
        if not isinstance(result.get(key), list):
            val = result.get(key)
            result[key] = [str(val)] if val else []

    # Ensure strings are strings
    for key in ("summary", "daily_limit", "personalized_advice"):
        if not isinstance(result.get(key), str):
            result[key] = str(result.get(key, ""))

    # Normalise health_rating
    rating = str(result.get("health_rating", "Fair")).strip().title()
    if rating not in VALID_RATINGS:
        # Map score to rating as fallback
        score = result["overall_score"]
        if score >= 80:
            rating = "Good"
        elif score >= 60:
            rating = "Fair"
        else:
            rating = "Poor"
    result["health_rating"] = rating

    return result
