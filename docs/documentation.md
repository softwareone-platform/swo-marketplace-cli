# Documentation

This repository follows the shared documentation standard:

- [standards/documentation.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/standards/documentation.md)

This file documents repository-specific documentation rules only.

## Repository Rules

- `README.md` must stay short and act as the main human entry point.
- `AGENTS.md` must stay operational and tell AI agents which files to read first.
- end-user command walkthroughs belong in [`usage.md`](usage.md), not in `README.md`.
- local workflow details belong in [`local-development.md`](local-development.md).
- `.github/copilot-instructions.md` must remain a thin adapter that points back to [`AGENTS.md`](../AGENTS.md).
- when behavior or workflow changes, update the corresponding document in the same change.

## Current Documentation Map

- [`README.md`](../README.md): human entry point, overview, quick start, and documentation map
- [`AGENTS.md`](../AGENTS.md): AI entry point and reading order
- [`architecture.md`](architecture.md): repository structure, domains, and boundaries
- [`local-development.md`](local-development.md): Docker-based setup and execution model
- [`usage.md`](usage.md): CLI commands, examples, and troubleshooting
- [`plugin-development.md`](plugin-development.md): plugin registration and implementation basics
- [`contributing.md`](contributing.md): repository-specific development workflow
- [`testing.md`](testing.md): testing strategy and command mapping

## Documentation Change Rule

When documentation changes, prefer updating the smallest relevant document instead of creating overlapping summary files.
