# agents.md - SoftwareOne CLI Development Guide

## Project Overview

**mpt-cli** is a command-line utility for the SoftwareOne Marketplace Platform. It provides tools for managing accounts, products, and price lists through an interactive CLI interface.

- **Language:** Python 3.12
- **Framework:** Typer (CLI framework)
- **Package Manager:** uv
- **Container:** Docker + Docker Compose
- **Code Quality:** Ruff, Flake8
- **Testing:** pytest

## Directory Structure

```
cli/
├── swocli.py              # Main CLI entry point
├── core/                  # Core functionality
│   ├── accounts/          # Account management module
│   ├── products/          # Product management module
│   ├── price_lists/       # Price list management module
│   ├── handlers/          # Request/response handlers
│   ├── models/            # Data models (Pydantic)
│   ├── services/          # Business logic services
│   ├── alias_group.py     # Custom Typer group with command aliases
│   ├── console.py         # Console output utilities
│   ├── plugins.py         # Plugin loader system
│   ├── state.py           # CLI state management
│   └── utils.py           # Utility functions
├── plugins/               # Plugin system
│   └── audit_plugin/      # Example plugin implementation

tests/
├── conftest.py            # pytest configuration and fixtures
├── test_debug_logging.py  # Logging tests
└── cli/                   # CLI tests mirroring core structure
```

## Key Architectural Patterns

### 1. Dependency Injection
- Uses `dependency-injector` library (v4.48)
- Containers manage service instantiation and configuration
- Each module (accounts, products, price_lists) has its own container

### 2. Plugin System
- Dynamic plugin loading via entry points defined in `pyproject.toml`
- Plugins are loaded in `cli/core/plugins.py`
- Entry point: `[project.entry-points."cli.plugins"]`
- Example: `audit = "cli.plugins.audit_plugin.app:app"`

### 3. CLI Structure
- Built with **Typer**, a modern Python CLI framework
- Command groups: `accounts`, `products`, `pricelists`
- Custom `AliasTyperGroup` allows command aliases
- Entry point: `mpt-cli` command

### 4. State Management
- Persistent CLI state via `cli/core/state.py`
- Configuration stored in `~/.swocli` directory (mounted in Docker)

## Development Setup

### Prerequisites
- Docker and Docker Compose plugin
- `make`
- Python 3.12 (for local development without Docker)

### Build & Environment
- **Dockerfile:** Multi-stage build (base → build → dev)
- **Dependencies:** Managed via `pyproject.toml` and `uv.lock`
- **Virtual Environment:** `/opt/venv` in container
- **Volume Mounts:** Current directory → `/cli`, config → `/root/.swocli`

## Development Commands

All commands run via Docker through the makefile:

| Command                | Purpose                                     |
|------------------------|---------------------------------------------|
| `make build`           | Build Docker image                          |
| `make run`             | Run CLI with help and interactive shell     |
| `make test [args=...]` | Run pytest with optional arguments          |
| `make check`           | Run Ruff and Flake8 checks, verify lockfile |
| `make check-all`       | Run checks + tests                          |
| `make format`          | Auto-format code with Ruff, fix imports     |
| `make bash`            | Open bash shell in container                |
| `make review`          | Run CodeRabbit code review                  |
| `make down`            | Stop and remove containers                  |

### Running Tests
```bash
make test                              # Full suite
make test args="-k test_cli -vv"      # Specific tests
make test args="tests/test_cli.py"    # Specific file
```

### Code Quality
```bash
make check      # Verify formatting and linting
make format     # Auto-fix formatting and imports
```

## Important Conventions

### Code Style
- **Formatter:** Ruff (black-compatible)
- **Linter:** Ruff + Flake8 (including AAA plugin for test readability)
- **Import Sorting:** Ruff (isort-compatible)
- Run `make format` before committing

### Testing
- Tests use pytest with Docker execution
- Configuration via `tests/conftest.py`
- Test files mirror source structure: `tests/cli/test_*.py`
- Mock API responses and state using fixtures

### Modules & Naming
- Each core module (accounts, products, price_lists) has:
  - `app.py` - CLI command definitions
  - `models.py` - Pydantic data models
  - `containers.py` - Dependency injection setup
  - `flows.py` - Business logic workflows
  - `handlers/` - Request/response handling
  - `api/` - API client integration

### External Dependencies
- **mpt-api-client:** SoftwareOne Marketplace API client (v0.0.*)
- **pydantic:** Data validation (v2.11)
- **openpyxl:** Excel file handling (v3.1)
- **requests:** HTTP library (v2.32)

## Key Files for Different Features

| Feature                | Key Files                                  |
|------------------------|--------------------------------------------|
| **Account Management** | `cli/core/accounts/`, `cli/core/state.py`  |
| **Product Operations** | `cli/core/products/`                       |
| **Price Lists**        | `cli/core/price_lists/`                    |
| **CLI Framework**      | `cli/swocli.py`, `cli/core/console.py`     |
| **Plugin System**      | `cli/core/plugins.py`, `cli/plugins/`      |
| **API Integration**    | `cli/core/services/`, `cli/core/handlers/` |

## Entry Points

- **CLI Command:** `mpt-cli` (defined in `pyproject.toml`)
- **Main App:** `cli.swocli:app` (Typer application instance)
- **Plugins Base:** `cli.plugins.*` (plugin modules)

## Configuration & State

- **User Config Directory:** `~/.swocli` (persisted via Docker volume)
- **Test Fixtures:** `tests/conftest.py`
- **Environment:** Containerized with `/opt/venv` Python environment

## Quick Reference for Common Tasks

1. **Adding a new CLI command:** Create in `cli/core/<module>/app.py`, register in `swocli.py`
2. **Adding a new plugin:** Create in `cli/plugins/<plugin_name>/`, add entry point in `pyproject.toml`
3. **Adding a new data model:** Define in `cli/core/<module>/models.py` using Pydantic
4. **Adding tests:** Create in `tests/cli/<module>/`, follow conftest patterns
5. **Updating dependencies:** Edit `pyproject.toml`, run `make build` to update `uv.lock`
