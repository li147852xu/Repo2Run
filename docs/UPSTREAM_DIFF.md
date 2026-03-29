# Differences from upstream (bytedance/Repo2Run)

This document helps reviewers compare **this fork / branch** with the official repository  
`https://github.com/bytedance/Repo2Run` (`upstream/main` or `origin/main` when both point at Bytedance).

**Latest diff stat** — regenerate with:

```bash
git fetch upstream && git diff upstream/main...HEAD --stat
```

Files vs upstream include: `.env.example`, `.github/PULL_REQUEST_TEMPLATE.md`, `.gitignore`, `CONTRIBUTING.md`, `README.md`, `build_agent/agents/configuration.py`, `build_agent/docker_templates/Dockerfile` (renamed from `docker/`), `build_agent/main.py`, `build_agent/multi_main.py`, `build_agent/utils/download.py`, `build_agent/utils/errorformat_list.py`, `build_agent/utils/integrate_dockerfile.py`, `build_agent/utils/llm.py`, `build_agent/utils/llm_providers.py`, `build_agent/utils/sandbox.py`, `build_agent/utils/waiting_list.py`, `docs/LLM_CONFIGURATION.md`, `docs/PR_TO_UPSTREAM.md`, `docs/UPSTREAM_DIFF.md`, `requirements.txt`, `requirements-dev.txt`, `tests/conftest.py`, `tests/test_llm_providers.py`, `tests/test_docker_integration.py`.

## Summary of changes (intended for upstream PRs)

| Area | Upstream | This branch |
|------|----------|-------------|
| OpenAI SDK | Mixed / broken combo of `openai==1.x` + deprecated `ChatCompletion` | Uses `client.chat.completions.create` (v1 SDK) |
| `main.py` | `Configuration(..., 100)` passed model as `100`, ignored `--llm` | `llm=llm`, `max_turn=100` |
| `integrate_dockerfile.py` | Undefined `outer_command` | Guarded `COPY` lines when `patch/` exists |
| Disk check | Assumes `/dev/vdb` | Safe when device missing (e.g. macOS) |
| `sandbox.py` | Hardcoded `chown huruida:huruida`; typo `os.sytem` | `getpass` + `sudo chown`; `os.system`; fixed `chown` path |
| Imports | `from parser.*` shadows stdlib `parser` on Python 3.9+ | Relative imports `.parser.*` |
| Dependencies | `pipreqs` used but not listed | `pipreqs` in `requirements.txt` |
| LLM APIs | OpenAI-only assumptions (`"gpt" in model`) | Pluggable: OpenAI-compatible + Anthropic; env + `--llm-provider` |
| Git | — | `.gitignore`: `**/utils/repo/` |
| `build_agent/docker/` folder | Sample Dockerfile only | Renamed to `docker_templates/` so `import docker` loads PyPI **docker** SDK, not a local namespace package |
| `sandbox.switch_to_pre_image` | `cpuset_cpus=0-19`, `mem_limit=30g` | Removed (Docker Desktop / laptops often have &lt;20 CPUs) |
| `sandbox.edit` | `file_path('/')` typo | Fixed to `file_path.split('/')` |
| `integrate_dockerfile` | Wrong `COPY search_patch`; missing `git checkout`; unconditional `code_edit` | `COPY patch /patch`; append `checkout_st`; `code_edit` only if file exists; optional `pipdeptree.json` |
| `download.py` apt `-v` | Passed package name instead of version | Fixed |
| `configuration.run` | Invalid reply overwrote last `outer_commands` entry (e.g. GPT_time) | Append dedicated error record |
| `configuration.run` (multi-turn LLM) | Observation appended as `role: "system"` after `assistant` | Observations use `role: "user"` so OpenAI-compatible APIs (e.g. **DeepSeek `deepseek-reasoner`**) get strict user/assistant alternation |
| `change_python_version` | Failure paths still set `returncode: 0`; str error from sandbox misreported success | Fixed control flow |
| `multi_main.py` | `/dev/vdb` check crashes on macOS | Guarded like `configuration.py` |
| Docs | — | `docs/LLM_CONFIGURATION.md`, PR template, `.env.example`, this file |
| Tests | — | `tests/test_llm_providers.py` + optional `tests/test_docker_integration.py` (`REPO2RUN_DOCKER_IT=1`) + `requirements-dev.txt` (`pytest`) |
| Docstrings | — | New public helpers in `llm_providers.py` documented per CONTRIBUTING |

## How to regenerate a clean diff against upstream

```bash
git fetch upstream
git diff upstream/main...HEAD --stat
```

When opening a PR to Bytedance, you can use **one combined PR** with a clear description (and optional multiple commits), or **one logical change per PR** if reviewers prefer smaller diffs.
