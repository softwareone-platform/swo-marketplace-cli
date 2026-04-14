# Usage

`mpt-cli` manages SoftwareOne Marketplace accounts, products, and price lists from the command line.

## Installation

Install the package from PyPI:

```bash
pip install mpt-cli
```

With `uv`:

```bash
uv tool install mpt-cli
```

With Poetry in a project environment:

```bash
poetry add mpt-cli
```

After installation, the CLI is available as:

```bash
mpt-cli --help
```

## Quick Start

Inspect the CLI:

```bash
mpt-cli --help
```

## Global Options

Top-level options:

- `--version`: print the CLI version and exit
- `--verbose`: enable debug logging to the console
- `--log-file <path>`: write debug logs to a file instead of the console

Example:

```bash
mpt-cli --verbose products list
```

## Account Management

Before using Marketplace commands, configure at least one account.

### Add An Account

```bash
mpt-cli accounts add <token> -e <api-base-url>
```

Example:

```bash
mpt-cli accounts add idt:xxxxx -e https://api.platform.softwareone.com
```

Notes:

- the CLI validates the token against the target environment before saving it
- the new account becomes the active account

### List Accounts

```bash
mpt-cli accounts list
mpt-cli accounts list --active
```

### Activate An Account

```bash
mpt-cli accounts activate <account-id>
```

### Remove An Account

```bash
mpt-cli accounts remove <account-id>
```

## Products

### List Products

```bash
mpt-cli products list
mpt-cli products list --page 25
mpt-cli products list --query "eq(status,Published)"
```

Notes:

- `--page` controls the page size, not the page number
- the command fetches pages interactively until there are no more results or the user stops

### Export Products

```bash
mpt-cli products export PRD-1234-5678 -o ./exports
mpt-cli products export PRD-1234-5678 PRD-9876-5432 -o ./exports
```

Notes:

- export writes `<product-id>.xlsx`
- the command requires an operations account
- existing files trigger an overwrite confirmation

### Sync Product Definitions

Validate only:

```bash
mpt-cli products sync ./definitions/PRD-1234-5678.xlsx --dry-run
```

Sync a product:

```bash
mpt-cli products sync ./definitions/PRD-1234-5678.xlsx
```

Force creation when the product id already exists:

```bash
mpt-cli products sync ./definitions/PRD-1234-5678.xlsx --force-create
```

Notes:

- the command validates the Excel definition before any write
- update mode currently supports item updates and related component synchronization through the implemented workflow

## Price Lists

### Export Price Lists

```bash
mpt-cli pricelists export PRC-1234-5678 -o ./exports
```

Notes:

- export writes `<pricelist-id>.xlsx`
- the command requires an operations account

### Sync Price Lists

```bash
mpt-cli pricelists sync ./definitions/PRC-1234-5678.xlsx
mpt-cli pricelists sync ./definitions/pricelists/*.xlsx
```

Notes:

- the command resolves all provided paths before syncing
- it creates a price list when the target does not exist and updates it otherwise

## Audit Plugin

The repository ships with an `audit` plugin command group.

Inspect help:

```bash
mpt-cli audit --help
```

Compare the two most recent audit records for an object:

```bash
mpt-cli audit diff-by-object-id OBJ-12345
```

Compare specific audit record ids:

```bash
mpt-cli audit diff-by-records-id AUD-1 AUD-2
```

## Troubleshooting

### Account Not Found

Cause:

- the account id is not present in the local account store

What to do:

- run `mpt-cli accounts list`
- verify the active account before product or price list operations

### Authentication Failed

Cause:

- the token is invalid, expired, or points to the wrong environment

What to do:

- re-add the account with the correct token and `--environment`

### File Not Found

Cause:

- the path passed to a sync command does not exist in the current working directory or accessible filesystem paths

What to do:

- verify the local path and target filenames
- run the command from a directory where those files are accessible

### Export Command Rejected

Cause:

- the active account is not an operations account

What to do:

- activate the correct account and rerun the export
