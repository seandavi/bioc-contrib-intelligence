"""Minimal Cloudflare Clef client: typed decisions with probabilities.

Wire format per developers.cloudflare.com/workers-ai/models/clef (see also
seandavi/bugsigdb-curation-tools `decision.py`, the full DecisionModel seam).
ponytail: no images, no mock backend; port that seam if either is needed.

Questions are {id: spec}. A bare string spec is a yes/no ("noul") question;
otherwise pass the wire shape, e.g. {"type": "choice", "instructions": ..., "criteria":
{"a": "desc", ...}} or {"type": "score", "instructions": ..., "criteria": [low, ..., high]}.
Answers: noul -> P(yes) as a float; choice -> {"choice", "probabilities"};
score -> {"score" (0 = lowest level, probability-weighted), "probabilities"}.

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


def _wire(spec: str | dict) -> dict:
    return {"type": "noul", "instructions": spec} if isinstance(spec, str) else spec


def _answer(a: dict):
    if a["type"] == "noul":
        return float(a["noul"])
    if a["type"] == "choice":
        return {"choice": a["choice"], "probabilities": a["probabilities"]}
    return {"score": float(a["score"]), "probabilities": a["probabilities"]}


@retry(retry=retry_if_exception_type((Retryable, httpx.TransportError)),
       wait=wait_exponential(min=1, max=30), stop=stop_after_attempt(5), reraise=True)
async def decide(c: httpx.AsyncClient, state: str, questions: dict[str, str | dict],
                 model: str = "clef") -> tuple[dict, dict]:
    """Ask `questions` about `state`. Returns ({id: answer}, usage)."""
    url = API.format(account=os.environ["CLOUDFLARE_ACCOUNT_ID"], model=model)
    body = {"model": model, "state": state,
            "questions": {q: _wire(s) for q, s in questions.items()}}
    r = await c.post(url, json=body)
    if r.status_code in (429, 500, 502, 503, 504):
        raise Retryable(r.status_code)
    r.raise_for_status()
    res = r.json()["result"]
    return {q: _answer(a) for q, a in res["answers"].items()}, res.get("usage", {})
