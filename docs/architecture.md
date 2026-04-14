# Architecture

This repository contains a Typer-based command-line client for SoftwareOne Marketplace operations.

## Main Components

- [`cli/swocli.py`](../cli/swocli.py): top-level CLI entry point, global options, banner rendering, and plugin registration
- [`cli/core/accounts/`](../cli/core/accounts): account storage, activation, token-backed account discovery, and account lookup
- [`cli/core/mpt/`](../cli/core/mpt): shared Marketplace API client creation, API access helpers, and common Marketplace models
- [`cli/core/products/`](../cli/core/products): product export, validation, create, and update workflows based on Excel definition files
- [`cli/core/price_lists/`](../cli/core/price_lists): price list export and synchronization workflows
- [`cli/core/handlers/`](../cli/core/handlers): shared file handlers and file-manager abstractions
- [`cli/core/services/`](../cli/core/services): service context, orchestration helpers, and reusable service plumbing
- [`cli/plugins/`](../cli/plugins): extensibility layer for optional Typer subcommands loaded from entry points

## Execution Model

The application is a local CLI, not a long-running service.

- users invoke `mpt-cli` or `python -m cli.swocli`
- commands authenticate against SoftwareOne Marketplace using the active account from the local account store
- export and sync commands read or write Excel files on the local filesystem
- plugin commands extend the main Typer app through Python entry points

## Domain Boundaries

### Accounts

The accounts domain owns local credential metadata and active-account selection.

- configuration is persisted through JSON handling in [`cli/core/accounts/handlers/`](../cli/core/accounts/handlers)
- the active account is the source of API configuration for other domains

### Products

The products domain owns product definition import and export.

- Marketplace-facing models live under [`cli/core/products/models/`](../cli/core/products/models)
- file import and export logic lives under [`cli/core/products/handlers/`](../cli/core/products/handlers)
- workflow orchestration lives in [`cli/core/products/app.py`](../cli/core/products/app.py) and the related services

### Price Lists

The price lists domain owns price list definition import and export.

- API adapters live under [`cli/core/price_lists/api/`](../cli/core/price_lists/api)
- Excel parsing and writing lives under [`cli/core/price_lists/handlers/`](../cli/core/price_lists/handlers)
- command orchestration lives in [`cli/core/price_lists/app.py`](../cli/core/price_lists/app.py)

### Plugins

The plugin layer allows repository-local or installed extensions to register additional subcommands.

- plugin discovery is implemented in [`cli/core/plugins.py`](../cli/core/plugins.py)
- the bundled audit feature lives in [`cli/plugins/audit_plugin/`](../cli/plugins/audit_plugin)
- external plugins must register a Typer app through the `cli.plugins` entry point group

See [plugin-development.md](plugin-development.md) for the plugin contract and a minimal example.

## Supporting Structure

- [`tests/`](../tests): pytest suite covering core domains and plugin behavior
- [`make/`](../make): canonical local commands that wrap Docker-based execution
- [`compose.yaml`](../compose.yaml): local container runtime wiring
- [`Dockerfile`](../Dockerfile): dev and prod image definitions

## Repository Constraints

- The supported local workflow is Docker-based.
- Documentation for end-user commands belongs in [`usage.md`](usage.md), not in `README.md`.
