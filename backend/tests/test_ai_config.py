import pytest

from app.core.config import Settings
from app.infrastructure.ai.workers.worker import GroqChatClient


def test_settings_reads_groq_key_from_env(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "sk-test-key")
    settings = Settings()
    assert settings.groq_api_key == "sk-test-key"


def test_groq_client_requires_key_when_fallback_is_disabled(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    monkeypatch.setenv("AI_USE_FALLBACK", "false")
    client = GroqChatClient("qwen/qwen3.8-27b", api_key="", allow_fallback=False)

    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        client.complete("Title: Sample Lesson\nGenerate a lesson about biology.")
