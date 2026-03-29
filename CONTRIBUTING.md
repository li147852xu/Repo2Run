# Contributing to Repo2Run

Thank you for your interest in contributing to Repo2Run! We welcome contributions from the community to help make this project better.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct principles:
- Be respectful and inclusive
- Exercise consideration and empathy in your speech and actions
- Focus on what is best for the community
- Show courtesy and respect towards other community members

## How to Contribute

### Upstream vs fork

The canonical repository is **[bytedance/Repo2Run](https://github.com/bytedance/Repo2Run)**. If you work from a personal fork:

- Keep an `upstream` remote pointing at Bytedance and sync before large changes.
- See **[docs/PR_TO_UPSTREAM.md](docs/PR_TO_UPSTREAM.md)** for PR hygiene and **[docs/UPSTREAM_DIFF.md](docs/UPSTREAM_DIFF.md)** for a maintained diff summary (on branches that track upstream).

### 1. Setting Up Your Development Environment

1. Fork the repository (upstream: bytedance/Repo2Run)
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Repo2Run.git
   cd Repo2Run
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Optional — run repository unit tests (e.g. `tests/test_llm_providers.py`):
   ```bash
   pip install -r requirements-dev.txt
   python -m pytest tests/
   ```
4. Ensure you have Docker installed and running
5. Copy `.env.example` to `.env` for local API keys (never commit `.env`); see **[docs/LLM_CONFIGURATION.md](docs/LLM_CONFIGURATION.md)**

### 2. Making Changes

1. Create a new branch for your bugfix (or larger change):
   ```bash
   git checkout -b fix/your-bugfix-name
   ```

2. Make your changes following our coding conventions:
   - Use clear, descriptive variable and function names
   - Write docstrings for new functions and classes
   - Add comments for complex logic
   - Follow PEP 8 style guidelines for Python code
   - Keep functions focused and single-purpose
   - Add appropriate error handling

3. Test your changes:
   - Ensure all existing tests pass
   - Add new tests for new functionality
   - Verify Docker-based builds work correctly

### 3. Submitting Changes

1. Commit your changes with clear, descriptive commit messages (prefer `fix:` / `docs:` / `test:` prefixes):
   ```bash
   git commit -m "fix: short description of your changes"
   ```

2. Push to your fork (remote may be named `origin` or `fork` depending on your `git remote -v`):
   ```bash
   git push origin fix/your-bugfix-name
   ```

3. Open a Pull Request:
   - Use the template in `.github/PULL_REQUEST_TEMPLATE.md` when available
   - Provide a clear title and description
   - Reference any related issues
   - Include screenshots or examples if applicable
   - List any breaking changes
   - Do **not** include API keys or other secrets

### 4. Pull Request Process

1. Your PR will be reviewed by maintainers
2. Address any requested changes or feedback
3. Once approved, your PR will be merged
4. Celebrate your contribution! 🎉

## Development Guidelines

### Project Structure
- Place new agent implementations in `build_agent/agents/`
- Add utility functions to `build_agent/utils/`
- Docker-related sample files go in `build_agent/docker_templates/`
- Main functionality should be in appropriate modules

### Testing
- Write unit tests for new functionality (`tests/` at repo root; dev deps in `requirements-dev.txt`)
- Include integration tests for Docker-related features: by default `pytest tests/` runs only fast, deterministic tests. To verify the Docker daemon locally before a PR, run:
  ```bash
  REPO2RUN_DOCKER_IT=1 python -m pytest tests/test_docker_integration.py -v
  ```
  End-to-end agent runs (`build_agent/main.py` with a small example repo) remain the authoritative check for container builds; describe what you ran in the PR.
- Test edge cases and error conditions
- Ensure tests are deterministic

### Documentation
- Update README.md for significant changes
- Add docstrings to new classes and functions
- Include example usage where appropriate
- Document any new dependencies

### Best Practices
- Handle errors gracefully with meaningful messages
- Log important operations and state changes
- Consider backward compatibility
- Follow security best practices

## Getting Help

- Open an issue for bugs or feature requests
- Ask questions in pull requests
- Check existing issues and documentation

## License

By contributing to Repo2Run, you agree that your contributions will be licensed under the Apache-2.0 License.
