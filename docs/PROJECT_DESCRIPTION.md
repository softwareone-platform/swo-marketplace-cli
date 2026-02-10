# mpt-cli

mpt-cli is a command-line utility to manage products, price lists, and accounts in the SWO Marketplace.

## Quick Start

1. **Launch the tool:**
    ```bash
    make run
    ```

2. **Add a new account with your API token and endpoint:**
    ```bash
    mpt-cli accounts add <token_id> -e <api_endpoint>
    ```

    **Example:**
    ```bash
    mpt-cli accounts add idt:xxxxx -e https://api.s1.show
    ```

## Installation

Install with pip or your favorite PyPI package manager:

```bash
pip install swo-marketplace-cli
```

```bash
uv add swo-marketplace-cli
```

## Prerequisites

- Python 3.12+ in your environment
- Access to the SWO Marketplace API endpoint

## Configuration

### Account Storage

The CLI stores account configurations in JSON files under `~/.swocli` by default. Each account includes:
- API token
- API endpoint URL
- Account metadata

## Usage

### Account Management

Before using the CLI, you need to configure at least one account.

#### Adding an Account

Add a new account with your API token and endpoint:

```bash
mpt-cli accounts add <token_id> -e <api_endpoint>
```

**Example:**
```bash
mpt-cli accounts add idt:xxxxx -e https://api.s1.show
```

**Options:**
- `-e, --endpoint <url>` – API endpoint URL (required)

#### Listing Accounts

View all configured accounts and see which one is active:

```bash
mpt-cli accounts list
```

The output shows all accounts with their IDs and endpoints. The active account is marked with an asterisk (*).

#### Activating an Account

If you have multiple accounts, switch between them:

```bash
mpt-cli accounts activate <account_id>
```

The active account is used for all subsequent API operations.

#### Removing an Account

Delete an account from your configuration:

```bash
mpt-cli accounts remove <account_id>
```

**Note:** You cannot remove the currently active account. Activate a different account first.

### Working with Products

#### Listing Products

Display available products:

```bash
mpt-cli products list
```

**Options:**
- `--page <number>` – Specify page number (default: 1)
- `--limit <number>` – Results per page (default: 25)

The output shows product ID, name, status, and version information.

#### Exporting Products

Export one or more products to Excel files:

```bash
mpt-cli products export <product_id> [<product_id>...] -o <output_folder>
```

**Example:**
```bash
mpt-cli products export PRD-1234-5678 PRD-9876-5432 -o ./exports
```

**Options:**
- `-o, --output-dir <folder>` – Output directory for exported files

If no output folder is specified, files are saved to the current directory with the format `<product-id>.xlsx`.

**Exported data includes:**
- General product information
- Product settings
- Items and item groups
- Parameters (agreement, assets, item, request, subscription)
- Parameter groups
- Templates

#### Synchronizing Products

Synchronize products from Excel definition files:

```bash
mpt-cli products sync <file_path> [<file_path>...]
```

**Options:**
- `-r, --dry-run` – Do not sync Product Definition. Check the file consistency only
- `-f, --force-create` – Force create a new product even if the Product ID exists

**Example:**
```bash
mpt-cli products sync PRD-1234-5678.xlsx PRD-9876-5432.xlsx
```
```bash
mpt-cli products sync --force-create PRD-1234-5678.xlsx
```

### Working with Price Lists

#### Synchronizing Price Lists

Upload and synchronize price lists from Excel files:

```bash
mpt-cli pricelists sync <file_path> [<file_path>...]
```

**Example:**
```bash
mpt-cli pricelists sync PRC-1234-5678.xlsx
```

#### Exporting Price Lists

Export price list data to Excel files:

```bash
mpt-cli pricelists export <pricelist_id> [<pricelist_id>...] -o <output_folder>
```

**Example:**
```bash
mpt-cli pricelists export PRC-1234-5678 -o ./exports
```

**Options:**
- `-o, --output-dir <folder>` – Output directory for exported files

If no output folder is specified, files are saved to the current directory with the format `<pricelist-id>.xlsx`.

### Getting Help

Run `mpt-cli --help` to see all available commands and options:

```bash
mpt-cli --help
mpt-cli accounts --help
mpt-cli products --help
mpt-cli products export --help
mpt-cli pricelists --help
```

## Troubleshooting

### Common Issues

**Account not found:**
- Error: "Account not found" or similar
- Cause: The specified account ID doesn't exist
- Solution: Run `mpt-cli accounts list` to see available accounts

**Authentication failed:**
- Error: "Authentication failed" or 401 errors
- Cause: Invalid or expired API token
- Solution: Verify your token is correct and has not expired. Add the account again with a valid token

**API endpoint unreachable:**
- Error: Connection errors or timeouts
- Cause: Invalid endpoint URL or network issues
- Solution: Verify the endpoint URL is correct and accessible from your network

**Product/Price list not found:**
- Error: "Product not found" or "Price list not found"
- Cause: The specified ID doesn't exist or you don't have access
- Solution: Verify the ID is correct and your account has appropriate permissions

**Invalid Excel file format:**
- Error: "Invalid file format" or validation errors
- Cause: The Excel file doesn't match the expected structure
- Solution: Export a valid product/price list to see the correct format, then modify your file to match

**Permission denied:**
- Error: "Permission denied" or 403 errors
- Cause: Your account doesn't have sufficient permissions
- Solution: Contact your administrator to verify your account has the required permissions

**File not found:**
- Error: "File not found" when syncing
- Cause: The specified file path doesn't exist
- Solution: Verify the file path is correct and the file exists
