# SoftwareONE CLI
`swo-marketplace-cli` is a command-line utility for SoftwareOne Marketplace operations.

The repository contains:

- account management for Marketplace environments
- product export and synchronization workflows
- price list export and synchronization workflows
- a plugin mechanism for optional command groups such as `audit`
- a Docker-based local development environment

## Documentation

Start here:

- [AGENTS.md](AGENTS.md): entry point for AI agents
- [docs/architecture.md](docs/architecture.md): repository structure and boundaries
- [docs/local-development.md](docs/local-development.md): Docker-based setup and local workflow
- [docs/usage.md](docs/usage.md): CLI commands, examples, and troubleshooting
- [docs/plugin-development.md](docs/plugin-development.md): how to build and register CLI plugins
- [docs/contributing.md](docs/contributing.md): repository-specific development workflow
- [docs/testing.md](docs/testing.md): testing strategy and commands
- [docs/documentation.md](docs/documentation.md): repository documentation rules

## Quick Start

Prerequisites:

- Docker with the `docker compose` plugin
- `make`

Recommended setup:

```bash
make build
make test
```

Inspect the CLI from Docker:

```bash
docker compose run --rm app python -m cli.swocli --help
```

## Repository Layout

- [`cli/`](cli): CLI source code
- [`tests/`](tests): pytest suite
- [`make/`](make): modular make targets
- [`docs/`](docs): repository documentation

## Common Commands

```bash
make build
make bash
make test
make check
make check-all
make format
```
