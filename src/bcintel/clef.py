"""Minimal Cloudflare Clef client: yes/no ("noul") decisions with probabilities.

Wire format per developers.cloudflare.com/workers-ai/models/clef (see also
seandavi/bugsigdb-curation-tools `decision.py`, the full DecisionModel seam).
ponytail: noul questions only, no images; port that seam when choice/score or a
mock backend is needed.

Auth: CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN (GSM: cdsci-r2-account-id,
cdsci-cloudflare-workers-ai-token). Pricing: $0.24/M input tokens, no output charge.
"""
from __future__ import annotations

import os

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

API = "https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/cloudflare/{model}"


class Retryable(Exception):
    pass


def client() -> httpx.AsyncClient:
    tok = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not tok or not os.environ.get("CLOUDFLARE_ACCOUNT_ID"):
        raise SystemExit("Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN.")
    return httpx.AsyncClient(headers={"Authorization": f"Bearer {tok}"}, timeout=90.0)


@retry(retry=retry_if_exception_type((Retryable, httpx.TransportError)),
       wait=wait_exponential(min=1, max=30), stop=stop_after_attempt(5), reraise=True)
async def decide(c: httpx.AsyncClient, state: str, questions: dict[str, str],
                 model: str = "clef") -> tuple[dict[str, float], dict]:
    """Ask yes/no `questions` ({id: instructions}) about `state`.
    Returns ({id: p_yes}, usage)."""
    url = API.format(account=os.environ["CLOUDFLARE_ACCOUNT_ID"], model=model)
    body = {"model": model, "state": state,
            "questions": {q: {"type": "noul", "instructions": t} for q, t in questions.items()}}
    r = await c.post(url, json=body)
    if r.status_code in (429, 500, 502, 503, 504):
        raise Retryable(r.status_code)
    r.raise_for_status()
    res = r.json()["result"]
    return {q: float(a["noul"]) for q, a in res["answers"].items()}, res.get("usage", {})
