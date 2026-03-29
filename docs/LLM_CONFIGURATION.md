# LLM API configuration

Repo2Run calls an LLM in a multi-turn loop. You can use **OpenAI-compatible** endpoints (OpenAI, DeepSeek, Moonshot, Groq, Together, local vLLM, Azure OpenAI, etc.) or **Anthropic** (Claude).

## Choose a backend

| Mechanism | Description |
|-----------|-------------|
| `--llm-provider auto` (default) | If the model id contains `claude` → Anthropic; otherwise OpenAI-compatible. |
| `--llm-provider openai_compatible` | Chat Completions API (OpenAI SDK). |
| `--llm-provider anthropic` | Anthropic Messages API. |
| `REPO2RUN_LLM_PROVIDER` | Same values as above; CLI overrides when not `auto`. |

## OpenAI-compatible providers

Uses the official `openai` Python SDK (`OpenAI().chat.completions.create`).

Set credentials (typical):

```bash
export OPENAI_API_KEY="sk-..."
# Optional: third-party or Azure base URL
export OPENAI_BASE_URL="https://api.deepseek.com"
```

Repo2Run-specific overrides (optional, take precedence over the above for the client constructor only):

```bash
export REPO2RUN_OPENAI_API_KEY="..."
export REPO2RUN_OPENAI_BASE_URL="https://api.deepseek.com"
```

Examples:

| Provider | `OPENAI_BASE_URL` (if not default) | Example `--llm` |
|----------|-----------------------------------|-----------------|
| OpenAI | (omit) | `gpt-4o-2024-05-13` |
| DeepSeek | `https://api.deepseek.com` | `deepseek-chat` |
| Moonshot (Kimi) | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| Together | `https://api.together.xyz/v1` | per Together docs |
| Local vLLM | `http://localhost:8000/v1` | your served model name |

Always check each vendor’s docs for the exact base URL and model id.

## Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Use a Claude model id, for example:

```bash
python build_agent/main.py ... --llm "claude-3-5-sonnet-20241022" --llm-provider anthropic
```

With `--llm-provider auto`, any model name containing `claude` selects Anthropic.

## DeepSeek `deepseek-reasoner` vs `deepseek-chat`

DeepSeek’s **reasoner** models enforce **strict user/assistant alternation** in the chat history (see DeepSeek API docs and community notes). Repo2Run sends environment feedback as **`user` turns** so the sequence stays valid. If you still see provider errors, try `deepseek-chat`, which is more permissive for the same base URL.

## Security

- Do not commit API keys. Use environment variables or a local untracked `.env` (never push `.env`).
- Copy `.env.example` to `.env` for a template.

## Further reading

- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python)
- [DeepSeek API](https://api-docs.deepseek.com/)
