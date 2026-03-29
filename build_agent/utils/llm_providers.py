# Copyright (2025) Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Resolve which backend to use for LLM calls and normalize usage metrics.

Supported:
  * openai_compatible — OpenAI Chat Completions API (OpenAI, DeepSeek, Moonshot,
    Groq, Together, vLLM, Azure OpenAI with base URL, etc.)
  * anthropic — Anthropic Messages API (Claude)
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Literal, Optional, Tuple

ProviderName = Literal["openai_compatible", "anthropic"]


def resolve_llm_provider(model: str, explicit: Optional[str] = None) -> ProviderName:
    """
    Choose API backend.

    Env REPO2RUN_LLM_PROVIDER (optional): auto | openai_compatible | anthropic
    CLI ``--llm-provider`` overrides env when set to a value other than ``auto``.
    """
    model_l = (model or "").lower()
    env_choice = (os.environ.get("REPO2RUN_LLM_PROVIDER") or "auto").strip().lower()
    ex = (explicit or "").strip().lower()
    if ex and ex != "auto":
        choice = ex
    else:
        choice = env_choice

    if choice == "anthropic":
        return "anthropic"
    if choice in ("openai_compatible", "openai"):
        return "openai_compatible"

    # auto
    if "claude" in model_l:
        return "anthropic"
    return "openai_compatible"


def uses_openai_style_conversation_roles(provider: ProviderName) -> bool:
    """If True, use system/user/assistant roles like OpenAI; else Anthropic-style (observations as user)."""
    return provider == "openai_compatible"


def _normalize_openai_usage(usage: Any) -> Optional[Dict[str, int]]:
    """Map Chat Completions ``usage`` to prompt/completion/total token counts."""
    if usage is None:
        return None
    try:
        if hasattr(usage, "model_dump"):
            u = usage.model_dump()
        elif isinstance(usage, dict):
            u = usage
        else:
            u = {
                "prompt_tokens": getattr(usage, "prompt_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            }
        total = u.get("total_tokens")
        if total is None:
            pt = u.get("prompt_tokens") or 0
            ct = u.get("completion_tokens") or 0
            total = pt + ct
        return {
            "total_tokens": int(total or 0),
            "prompt_tokens": int(u.get("prompt_tokens") or 0),
            "completion_tokens": int(u.get("completion_tokens") or 0),
        }
    except Exception:
        return {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}


def _normalize_anthropic_usage(usage: Any) -> Optional[Dict[str, int]]:
    """Map Anthropic ``usage`` (input/output tokens) to the same shape as OpenAI usage."""
    if usage is None:
        return None
    try:
        inp = int(getattr(usage, "input_tokens", 0) or 0)
        out = int(getattr(usage, "output_tokens", 0) or 0)
        return {
            "total_tokens": inp + out,
            "prompt_tokens": inp,
            "completion_tokens": out,
        }
    except Exception:
        return {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}


def chat_openai_compatible(
    model: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.0,
    n: int = 1,
    max_tokens: int = 4096,
) -> Tuple[List[Optional[str]], Optional[Dict[str, int]]]:
    """
    Call the OpenAI-compatible Chat Completions API (network).

    Uses ``OPENAI_API_KEY`` / ``OPENAI_BASE_URL`` or ``REPO2RUN_OPENAI_*`` overrides.
    Returns ``(choice_texts, usage_dict)`` with one entry per ``n``.
    """
    import openai

    # Optional project-specific override; else SDK reads OPENAI_API_KEY / OPENAI_BASE_URL
    base_url = os.environ.get("REPO2RUN_OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE")
    api_key = os.environ.get("REPO2RUN_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

    kwargs: Dict[str, Any] = {}
    if base_url:
        kwargs["base_url"] = base_url.rstrip("/")
    if api_key:
        kwargs["api_key"] = api_key

    client = openai.OpenAI(**kwargs)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        n=n,
        max_tokens=max_tokens,
    )
    choices = [c.message.content for c in response.choices if c.message]
    usage = _normalize_openai_usage(getattr(response, "usage", None))
    return choices if choices else [None], usage


def chat_anthropic(
    model: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.0,
    n: int = 1,
    max_tokens: int = 4096,
) -> Tuple[List[Optional[str]], Optional[Dict[str, int]]]:
    """
    Call Anthropic Messages API (network). Only ``n=1`` is used; extra completions are not requested.

    Reads ``ANTHROPIC_API_KEY`` from the environment via the SDK.
    """
    import anthropic

    if n != 1:
        # Anthropic batching differs; keep single completion for agent loop
        pass

    client = anthropic.Anthropic()
    system_text, api_messages = _openai_messages_to_anthropic(messages)

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_text or "You are a helpful assistant.",
        messages=api_messages,
    )
    texts: List[str] = []
    for block in response.content:
        if hasattr(block, "text"):
            texts.append(block.text)
        elif isinstance(block, dict) and block.get("type") == "text":
            texts.append(block.get("text", ""))
    content = "".join(texts) if texts else None
    usage = _normalize_anthropic_usage(response.usage)
    return ([content] if content else [None], usage)


def _openai_messages_to_anthropic(
    messages: List[Dict[str, Any]],
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Convert OpenAI-style message list to Anthropic system + messages[].
    Mid-conversation 'system' turns (observations) become user messages.
    """
    system_chunks: List[str] = []
    out: List[Dict[str, str]] = []
    seen_any_non_system = False

    for m in messages:
        role = m.get("role", "")
        content = m.get("content", "")
        if not isinstance(content, str):
            content = str(content)

        if role == "system":
            if not seen_any_non_system:
                system_chunks.append(content)
            else:
                out.append({"role": "user", "content": content})
        elif role == "user":
            seen_any_non_system = True
            out.append({"role": "user", "content": content})
        elif role == "assistant":
            seen_any_non_system = True
            out.append({"role": "assistant", "content": content})

    return "\n\n".join(system_chunks), out
