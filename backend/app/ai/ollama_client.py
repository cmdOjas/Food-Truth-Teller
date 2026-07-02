"""
Ollama HTTP client.

Sends prompts to a locally-running Ollama instance and returns the
model's text response.  Supports both regular (buffered) and streaming
requests.  A single requests.Session is reused across calls to keep the
TCP connection alive and avoid repeated handshake overhead.
"""
from __future__ import annotations

import json
import logging
from typing import Generator

import requests
from flask import current_app

logger = logging.getLogger(__name__)

_SESSION: requests.Session | None = None


def _get_session() -> requests.Session:
    """Return a module-level reusable HTTP session (lazy init)."""
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
        _SESSION.headers.update({"Content-Type": "application/json"})
    return _SESSION


def generate(
    prompt: str,
    model: str | None = None,
    system: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 1200,
    timeout: int = 120,
) -> str:
    """
    Send *prompt* to Ollama and return the complete response string.

    Parameters
    ----------
    prompt:      The user / instruction text.
    model:       Ollama model tag (default from app config: OLLAMA_MODEL).
    system:      Optional system message prepended before the prompt.
    temperature: Sampling temperature — lower = more deterministic.
    max_tokens:  Maximum tokens to generate.
    timeout:     HTTP request timeout in seconds.

    Raises
    ------
    RuntimeError if Ollama is unreachable or returns a non-200 status.
    """
    base_url = _cfg("OLLAMA_BASE_URL", "http://localhost:11434")
    model = model or _cfg("OLLAMA_MODEL", "phi3:latest")

    payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "stop": ["<|end|>", "</s>"],
        },
    }
    if system:
        payload["system"] = system

    try:
        resp = _get_session().post(
            f"{base_url}/api/generate",
            data=json.dumps(payload),
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure Ollama is running: `ollama serve`"
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            f"Ollama request timed out after {timeout}s. "
            "Try a shorter prompt or increase OLLAMA_TIMEOUT."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"Ollama HTTP error: {exc}") from exc


def stream_generate(
    prompt: str,
    model: str | None = None,
    system: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 1200,
    timeout: int = 120,
) -> Generator[str, None, None]:
    """
    Stream token chunks from Ollama.  Yields partial response strings.
    Useful for Server-Sent Events (SSE) endpoints.
    """
    base_url = _cfg("OLLAMA_BASE_URL", "http://localhost:11434")
    model = model or _cfg("OLLAMA_MODEL", "phi3:latest")

    payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "stop": ["<|end|>", "</s>"],
        },
    }
    if system:
        payload["system"] = system

    try:
        with _get_session().post(
            f"{base_url}/api/generate",
            data=json.dumps(payload),
            stream=True,
            timeout=timeout,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError("Cannot connect to Ollama.") from exc


def is_ollama_running() -> bool:
    """Return True if Ollama's health endpoint responds."""
    base_url = _cfg("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        resp = _get_session().get(f"{base_url}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def _cfg(key: str, default: str = "") -> str:
    """Read from Flask app config, fall back to *default*."""
    try:
        return current_app.config.get(key, default) or default
    except RuntimeError:
        # Outside app context (e.g., tests)
        import os
        return os.environ.get(key, default)
