# AGENTS.md

Working protocol for any task in this repository:

1. Identify the task type and select only the local repository files that are relevant to that task.
2. Read only those relevant local files before making changes.
3. If any selected local file references shared standards or shared operational guidance that are relevant to the same task, read those shared documents too before proceeding.
4. Treat repository-local documents as repository-specific additions, restrictions, or overrides to shared guidance.
5. If a repository-local rule conflicts with a shared rule, the local repository rule takes precedence.

When applicable, read this repository in the following order:

1. [README.md](README.md) for the repository purpose, quick start, and documentation map.
2. [docs/architecture.md](docs/architecture.md) for the CLI structure, domains, and boundaries.
3. [docs/local-development.md](docs/local-development.md) for the Docker-based local workflow and supported commands.
4. [docs/usage.md](docs/usage.md) for end-user CLI commands, examples, and troubleshooting.
5. [docs/plugin-development.md](docs/plugin-development.md) when a task involves adding, changing, or debugging CLI plugins.
6. [docs/contributing.md](docs/contributing.md) for repository-specific contribution guidance.
7. [docs/testing.md](docs/testing.md) before changing code or tests.
8. [docs/documentation.md](docs/documentation.md) when changing repository documentation.

Then inspect the code paths relevant to the task:

- [`cli/swocli.py`](cli/swocli.py): main Typer application, global options, and plugin loading
- [`cli/core/accounts/`](cli/core/accounts): account configuration, persistence, activation, and account-aware flows
- [`cli/core/mpt/`](cli/core/mpt): Marketplace API client setup, API adapters, and shared Marketplace models
- [`cli/core/products/`](cli/core/products): product export and sync workflows
- [`cli/core/price_lists/`](cli/core/price_lists): price list export and sync workflows
- [`cli/core/handlers/`](cli/core/handlers): shared file handling and Excel/JSON helpers
- [`cli/core/services/`](cli/core/services): service abstractions and orchestration helpers
- [`cli/plugins/`](cli/plugins): plugin discovery and bundled plugin commands such as `audit`
- [`tests/`](tests): pytest coverage by domain area
- [`make/`](make): canonical local commands
- [`compose.yaml`](compose.yaml) and [`Dockerfile`](Dockerfile): Docker-based local execution model

Operational guidance:

- Use Docker-backed commands only. Prefer `make` targets and `docker compose run --rm app ...` over host Python execution.
- Keep `README.md` short and navigational. Put end-user command details in [`docs/usage.md`](docs/usage.md).
- Keep repository policy in `docs/` and keep [`.github/copilot-instructions.md`](.github/copilot-instructions.md) thin.
