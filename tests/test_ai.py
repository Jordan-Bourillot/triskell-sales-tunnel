"""Tests du module IA — obfuscation, settings, dispatch (sans appel réseau)."""

from __future__ import annotations

import pytest

from triskell_sales_tunnel import ai
from triskell_sales_tunnel.data import UserState


def test_encode_decode_roundtrip() -> None:
    plain = "sk-ant-api03-abc123-XyZ_456"
    obf = ai._encode_key(plain)
    assert obf != plain
    assert ai._decode_key(obf) == plain


def test_encode_empty_returns_empty() -> None:
    assert ai._encode_key("") == ""
    assert ai._decode_key("") == ""


def test_decode_invalid_returns_empty() -> None:
    assert ai._decode_key("not-base64!!!") == ""


def test_store_and_clear_api_key() -> None:
    state = UserState()
    ai.store_api_key(state, "secret-key")
    assert state.ai_api_key_obf
    assert state.ai_api_key_obf != "secret-key"
    settings = ai.AISettings.from_state(state)
    assert settings.api_key == "secret-key"

    ai.clear_api_key(state)
    assert state.ai_api_key_obf == ""
    settings = ai.AISettings.from_state(state)
    assert settings.api_key == ""


def test_settings_uses_env_when_present(monkeypatch: pytest.MonkeyPatch) -> None:
    state = UserState()
    state.ai_provider = "anthropic"
    ai.store_api_key(state, "stored-key")

    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    settings = ai.AISettings.from_state(state)
    assert settings.api_key == "env-key"  # env prime


def test_settings_falls_back_to_stored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    state = UserState()
    state.ai_provider = "anthropic"
    ai.store_api_key(state, "stored-key")
    settings = ai.AISettings.from_state(state)
    assert settings.api_key == "stored-key"


def test_settings_default_model() -> None:
    state = UserState()
    state.ai_provider = "anthropic"
    state.ai_model = ""  # vide => défaut
    settings = ai.AISettings.from_state(state)
    assert settings.model == ai.DEFAULT_MODELS["anthropic"]


def test_settings_custom_model() -> None:
    state = UserState()
    state.ai_provider = "openai"
    state.ai_model = "gpt-4-turbo"
    settings = ai.AISettings.from_state(state)
    assert settings.model == "gpt-4-turbo"


def test_settings_unknown_provider_falls_back() -> None:
    state = UserState()
    state.ai_provider = "unknown-provider"
    settings = ai.AISettings.from_state(state)
    assert settings.provider == ai.PROVIDER_ANTHROPIC


def test_has_ai_configured() -> None:
    state = UserState()
    assert ai.has_ai_configured(state) is False
    ai.store_api_key(state, "k")
    assert ai.has_ai_configured(state) is True


def test_generate_rewrite_without_key_raises() -> None:
    state = UserState()
    settings = ai.AISettings.from_state(state)
    with pytest.raises(ai.AIError):
        ai.generate_rewrite(
            settings=settings,
            original="x",
            channel="Email",
            client="Test",
            product="Test",
        )


def test_build_user_prompt_includes_context() -> None:
    out = ai._build_user_prompt(
        original="Bonjour [Prénom]",
        channel="Email",
        client="TPE bretonnes",
        product="Triskell Studio",
        subject="Mon sujet",
    )
    assert "Email" in out
    assert "TPE bretonnes" in out
    assert "Triskell Studio" in out
    assert "Mon sujet" in out
    assert "Bonjour [Prénom]" in out


def test_build_user_prompt_without_subject() -> None:
    out = ai._build_user_prompt(
        original="msg",
        channel="LinkedIn",
        client="X",
        product="Y",
        subject="",
    )
    assert "Objet" not in out
