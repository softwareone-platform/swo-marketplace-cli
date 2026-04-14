# Testing

Shared unit-test rules live in [unittests.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/standards/unittests.md).

Shared build and target knowledge also applies:

- [knowledge/build-and-checks.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/knowledge/build-and-checks.md)
- [knowledge/make-targets.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/knowledge/make-targets.md)

This file documents repository-specific testing behavior.

## Test Scope

The repository has coverage in these areas:

- account management under [`tests/cli/core/accounts/`](../tests/cli/core/accounts)
- shared handler and service behavior under [`tests/cli/core/handlers/`](../tests/cli/core/handlers) and [`tests/cli/core/`](../tests/cli/core)
- Marketplace integration helpers under [`tests/cli/core/mpt/`](../tests/cli/core/mpt)
- product workflows under [`tests/cli/core/products/`](../tests/cli/core/products)
- price list workflows under [`tests/cli/core/price_lists/`](../tests/cli/core/price_lists)
- plugin behavior under [`tests/cli/plugins/`](../tests/cli/plugins) and [`tests/plugins/`](../tests/plugins)

## Commands

Use the repository make targets:

```bash
make test
make check
make check-all
```

Repository command mapping:

- `make test` runs `pytest`
- `make check` runs `ruff format --check`, `ruff check`, `flake8`, `mypy`, and `uv lock --check`
- `make check-all` runs both checks and tests

## Pytest Configuration

Repository-specific test settings come from [`pyproject.toml`](../pyproject.toml):

- tests are discovered under `tests`
- `pythonpath` includes the repository root
- coverage is collected for `cli`
- tests run with `--import-mode=importlib`
- the repository defines an `integration` marker

## Writing Tests

Repository-specific guidance:

- add or update tests next to the affected domain area instead of creating catch-all test files
- prefer existing fixtures and helpers from nearby `conftest.py` files
- keep Marketplace API and file I/O dependencies isolated through the repository abstractions already used in the tests
- cover plugin registration or plugin behavior when changing entry points under [`cli/plugins/`](../cli/plugins)

## When Tests Are Required

Add or update tests when a change modifies:

- account handling or active-account selection
- Marketplace API orchestration
- product export or sync flows
- price list export or sync flows
- plugin loading or plugin command behavior

If a change only affects documentation, tests are not required.
