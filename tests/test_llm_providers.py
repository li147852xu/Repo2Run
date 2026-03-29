# Copyright (2025) Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Unit tests for build_agent.utils.llm_providers (no network calls)."""

from __future__ import annotations

import pytest

from utils.llm_providers import (
    _normalize_anthropic_usage,
    _normalize_openai_usage,
    _openai_messages_to_anthropic,
    resolve_llm_provider,
    uses_openai_style_conversation_roles,
)


class TestResolveLlmProvider:
    def test_explicit_anthropic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("REPO2RUN_LLM_PROVIDER", raising=False)
        assert resolve_llm_provider("gpt-4", "anthropic") == "anthropic"

    def test_explicit_openai_compatible_aliases(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("REPO2RUN_LLM_PROVIDER", raising=False)
        assert resolve_llm_provider("x", "openai_compatible") == "openai_compatible"
        assert resolve_llm_provider("x", "openai") == "openai_compatible"

    def test_explicit_auto_falls_back_to_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("REPO2RUN_LLM_PROVIDER", "anthropic")
        assert resolve_llm_provider("gpt-4", "auto") == "anthropic"

    def test_env_openai_compatible(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("REPO2RUN_LLM_PROVIDER", "openai_compatible")
        assert resolve_llm_provider("claude-3-opus", None) == "openai_compatible"

    def test_auto_claude_model(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("REPO2RUN_LLM_PROVIDER", "auto")
        assert resolve_llm_provider("anthropic/claude-3-sonnet", None) == "anthropic"

    def test_auto_non_claude_defaults_openai(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("REPO2RUN_LLM_PROVIDER", "auto")
        assert resolve_llm_provider("gpt-4o", None) == "openai_compatible"


class TestUsesOpenaiStyleRoles:
    def test_flags(self) -> None:
        assert uses_openai_style_conversation_roles("openai_compatible") is True
        assert uses_openai_style_conversation_roles("anthropic") is False


class TestNormalizeOpenaiUsage:
    def test_none(self) -> None:
        assert _normalize_openai_usage(None) is None

    def test_dict_sums_tokens_when_total_missing(self) -> None:
        u = _normalize_openai_usage({"prompt_tokens": 3, "completion_tokens": 7})
        assert u is not None
        assert u["total_tokens"] == 10
        assert u["prompt_tokens"] == 3
        assert u["completion_tokens"] == 7

    def test_dict_uses_total_when_present(self) -> None:
        u = _normalize_openai_usage({"total_tokens": 99, "prompt_tokens": 1, "completion_tokens": 2})
        assert u is not None
        assert u["total_tokens"] == 99


class TestNormalizeAnthropicUsage:
    def test_none(self) -> None:
        assert _normalize_anthropic_usage(None) is None

    def test_object_attrs(self) -> None:
        class U:
            input_tokens = 12
            output_tokens = 8

        u = _normalize_anthropic_usage(U())
        assert u is not None
        assert u["total_tokens"] == 20
        assert u["prompt_tokens"] == 12
        assert u["completion_tokens"] == 8


class TestOpenaiMessagesToAnthropic:
    def test_system_then_user(self) -> None:
        system, msgs = _openai_messages_to_anthropic(
            [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "hi"},
            ]
        )
        assert "sys" in system
        assert msgs == [{"role": "user", "content": "hi"}]

    def test_late_system_becomes_user(self) -> None:
        system, msgs = _openai_messages_to_anthropic(
            [
                {"role": "system", "content": "first"},
                {"role": "user", "content": "u"},
                {"role": "system", "content": "observation"},
            ]
        )
        assert "first" in system
        assert msgs[-1]["role"] == "user"
        assert msgs[-1]["content"] == "observation"
