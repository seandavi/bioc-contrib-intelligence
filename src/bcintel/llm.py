"""LLM backend — a thin interface over a deep module.

Callers use only two functions and never learn which provider answered:

    available() -> bool
    generate(prompt, system=None) -> str

Everything else — provider selection, auth, per-provider request/response shapes —
is hidden here. Adding or swapping a backend changes only this file; no caller
moves. Requests go over httpx (already a dependency), so there is no SDK.

Provider is chosen from the environment. `LLM_PROVIDER` forces one; otherwise it
is inferred from whichever key is present:

    gemini  Google AI Studio   GEMINI_API_KEY / GOOGLE_API_KEY   (model: GEMINI_MODEL)
    claude  Anthropic API      ANTHROPIC_API_KEY                 (model: ANTHROPIC_MODEL)

Defaults: gemini-2.5-flash, claude-sonnet-5.

Vertex/Bedrock Claude slot in as additional providers here when needed, with the
interface unchanged.
"""
from __future__ import annotations

import os

import httpx


def _gemini_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def _anthropic_key():
    return os.environ.get("ANTHROPIC_API_KEY")


def _call_gemini(prompt, system, timeout):
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    body: dict = {"contents": [{"parts": [{"text": prompt}]}]}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    r = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": _gemini_key()}, json=body, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    cands = data.get("candidates") or []
    if not cands:
        return f"_(Gemini returned no content: {data.get('promptFeedback', 'unknown')})_"
    parts = cands[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts).strip()


def _call_claude(prompt, system, timeout):
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
    body: dict = {"model": model, "max_tokens": 2048,
                  "messages": [{"role": "user", "content": prompt}]}
    if system:
        body["system"] = system
    r = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": _anthropic_key(), "anthropic-version": "2023-06-01"},
        json=body, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    return text.strip() or f"_(Claude returned no text: {data.get('stop_reason')})_"


# provider name -> (key getter, call fn). Add a row to grow the module.
_PROVIDERS = {
    "gemini": (_gemini_key, _call_gemini),
    "claude": (_anthropic_key, _call_claude),
}


def _provider() -> str:
    forced = os.environ.get("LLM_PROVIDER")
    if forced:
        return forced.lower()
    if _anthropic_key():
        return "claude"
    if _gemini_key():
        return "gemini"
    return "none"


def available() -> bool:
    spec = _PROVIDERS.get(_provider())
    return bool(spec and spec[0]())


def generate(prompt: str, system: str | None = None, timeout: float = 60.0) -> str:
    prov = _provider()
    spec = _PROVIDERS.get(prov)
    if not spec or not spec[0]():
        raise RuntimeError(
            f"No LLM credentials for provider '{prov}'. "
            "Set ANTHROPIC_API_KEY, or GEMINI_API_KEY / GOOGLE_API_KEY.")
    return spec[1](prompt, system, timeout)
