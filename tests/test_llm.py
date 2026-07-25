import pytest

from bcintel import llm

KEYS = ["LLM_PROVIDER", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)


def test_infers_provider_from_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "x")
    assert llm._provider() == "gemini" and llm.available()

    monkeypatch.setenv("ANTHROPIC_API_KEY", "y")  # anthropic wins when both present
    assert llm._provider() == "claude" and llm.available()


def test_explicit_provider_without_key_is_unavailable(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    assert llm._provider() == "gemini"
    assert not llm.available()  # forced provider, but no key


def test_no_credentials(monkeypatch):
    assert llm._provider() == "none"
    assert not llm.available()
    with pytest.raises(RuntimeError):
        llm.generate("hi")
