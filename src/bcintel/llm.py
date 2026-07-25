"""LLM backend — Google Gemini (AI Studio) via the REST API.

Called through httpx (already a dependency), so no SDK. Key from GEMINI_API_KEY
or GOOGLE_API_KEY; model from GEMINI_MODEL (default gemini-2.5-flash). Optional:
`available()` is False with no key, and callers fall back to a non-LLM path so
the bot still runs offline and tests never hit the network.
"""
from __future__ import annotations

import os

import httpx

DEFAULT_MODEL = "gemini-2.5-flash"
API = "https://generativelanguage.googleapis.com/v1beta/models"


def api_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def available() -> bool:
    return bool(api_key())


def generate(prompt: str, system: str | None = None, model: str | None = None,
             timeout: float = 60.0) -> str:
    key = api_key()
    if not key:
        raise RuntimeError("No Gemini key: set GEMINI_API_KEY or GOOGLE_API_KEY")
    model = model or os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    body: dict = {"contents": [{"parts": [{"text": prompt}]}]}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    r = httpx.post(f"{API}/{model}:generateContent",
                   headers={"x-goog-api-key": key}, json=body, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    cands = data.get("candidates") or []
    if not cands:  # safety block or empty response
        return f"_(Gemini returned no content: {data.get('promptFeedback', 'unknown')})_"
    parts = cands[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts).strip()
