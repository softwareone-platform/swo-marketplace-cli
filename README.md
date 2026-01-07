[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=softwareone-platform_swo-marketplace-cli&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=softwareone-platform_swo-marketplace-cli) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=softwareone-platform_swo-marketplace-cli&metric=coverage)](https://sonarcloud.io/summary/new_code?id=softwareone-platform_swo-marketplace-cli)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# SoftwareONE CLI
Command line utility for SoftwareOne Marketplace Platform

## Prerequisites

- Docker and Docker Compose plugin (`docker compose` CLI)
- `make`
- [CodeRabbit CLI](https://www.coderabbit.ai/cli) (optional. Used for running review check locally)

## Make targets overview

Common development workflows are wrapped in the `makefile`:

- `make help` – list available commands
- `make bash` – start the app container and open a bash shell
- `make build` – build the application image for development
- `make check` – run code quality checks (ruff, flake8, lockfile check)
- `make check-all` – run checks, formatting, and tests
- `make format` – apply formatting and import fixes
- `make down` – stop and remove containers
- `make review` –  check the code in the cli by running CodeRabbit
- `make run` – run the CLI tool
- `make test` – run the test suite with pytest

## Running CLI commands

Run the CLI tool:
```bash
make run
```

## Running tests

Tests run inside Docker using the dev configuration.

Run the full test suite:

```bash
make test
```

Pass additional arguments to pytest using the `args` variable:

```bash
make test args="-k test_cli -vv"
make test args="tests/test_cli.py"
```

## Developer utilities

Useful helper targets during development:

```bash
make bash      # open a bash shell in the app container
make check     # run ruff, flake8, and lockfile checks
make check-all # run checks and tests
make format    # auto-format code and imports
make review    # check the code in the cli by running CodeRabbit
```

## Using the CLI

### Getting Started

Launch the CLI tool:

```bash
make run
```

To see all available commands and options:

```bash
mpt-cli --help
```

### Account Management

Before using the CLI, you need to configure at least one account.

#### Add an Account

Add a new account with your API token and endpoint:

```bash
mpt-cli accounts add <token_id> -e <api_endpoint>
```

**Example:**
```bash
mpt-cli accounts add idt:xxxxx -e https://api.s1.show/public/v1
```

#### List Accounts

View all configured accounts and see which one is active:

```bash
mpt-cli accounts list
```

#### Activate an Account

If you have multiple accounts, switch between them:

```bash
mpt-cli accounts activate <account_id>
```

#### Remove an Account

Delete an account from your configuration:

```bash
mpt-cli accounts remove <account_id>
```

### Working with Products

#### List Products

Display available products:

```bash
mpt-cli products list
```

**Options:**
- `--page <number>` – Specify page number (default: 1)
- `--limit <number>` – Results per page (default: 25)

#### Export Products

Export one or more products to Excel files:

```bash
mpt-cli products export <product_id> [<product_id>...] -o <output_folder>
```

**Example:**
```bash
mpt-cli products export PRD-1234-5678 PRD-9876-5432 -o ./exports
```

If no output folder is specified, files are saved to the current directory with the format `<product-id>.xlsx`.

#### Sync Products

Synchronize products from Excel definition files:

```bash
mpt-cli products sync <file_path> [<file_path>...]
```

**Example:**
```bash
mpt-cli products sync PRD-1234-5678.xlsx PRD-9876-5432.xlsx
```

### Working with Price Lists

#### Sync Price Lists

Upload and synchronize price lists from Excel files:

```bash
mpt-cli pricelists sync <file_path> [<file_path>...]
```

**Example:**
```bash
mpt-cli pricelists sync PRC-1234-5678.xlsx
```

#### Export Price Lists

Export price list data to Excel files:

```bash
mpt-cli pricelists export <pricelist_id> [<pricelist_id>...] -o <output_folder>
```


### Tips

- Use `--help` with any command to see detailed usage information:
  ```bash
  mpt-cli products --help
  mpt-cli products export --help
  ```
- File paths support glob patterns for batch operations
- The active account is used for all API operations
