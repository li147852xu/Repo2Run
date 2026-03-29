# Opening a pull request to bytedance/Repo2Run

Follow common open-source practice so maintainers can review quickly.

## Before you start

1. **Fork** the official repo (if you have not): [bytedance/Repo2Run](https://github.com/bytedance/Repo2Run).
2. **Sync** your default branch with upstream regularly:
   ```bash
   git remote add upstream https://github.com/bytedance/Repo2Run.git  # once
   git fetch upstream
   git checkout main
   git merge upstream/main   # or rebase if you prefer
   ```
3. **Branch** from an up-to-date `main`:
   ```bash
   git checkout -b fix/short-description
   ```

## PR content

- **Title**: imperative, concise (e.g. `Fix OpenAI client usage for openai>=1.0`).
- **Description**: use the repo’s PR template (`.github/PULL_REQUEST_TEMPLATE.md`).
- **Scope**: one concern per PR when possible (bugfix vs docs vs tests). A **single combined PR** is fine if you use clear sections in the description (and optional multiple commits); split only if reviewers ask or you prefer smaller diffs.
- **Breaking changes**: call them out explicitly.
- **Testing**: describe how you ran `build_agent/main.py` (or other checks), OS, Docker, and model used (without pasting secrets).

## Commit messages

- Prefer [Conventional Commits](https://www.conventionalcommits.org/) style for this repo’s changes: `fix:`, `docs:`, `test:`, `refactor:`.
- Keep commits logically scoped; squash noisy WIP commits before merge if asked.

## License

Contributions are under **Apache-2.0**, same as upstream (`LICENSE`).
