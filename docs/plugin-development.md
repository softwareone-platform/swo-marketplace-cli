# Plugin Development

This document explains the basic plugin model for `mpt-cli`.

## How Plugins Are Loaded

The main CLI loads plugins through Python entry points defined in the `cli.plugins` group.

The loading logic lives in [`cli/core/plugins.py`](../cli/core/plugins.py):

- `entry_points().select(group="cli.plugins")` discovers installed plugins
- each discovered entry point is loaded
- the returned Typer app is attached to the main CLI with `app.add_typer(plugin_app, name=entrypoint.name)`

This means a plugin must expose a Typer application object, not just plain functions.

## Minimal Plugin Shape

A plugin package needs these pieces:

1. A Python package that contains a Typer app.
2. A `pyproject.toml` entry point in the `cli.plugins` group.
3. A dependency on a compatible `mpt-cli` version.

Example `pyproject.toml`:

```toml
[project]
name = "mpt-cli-example-plugin"
version = "0.1.0"
requires-python = ">=3.12,<4"
dependencies = [
  "mpt-cli==2.0.*",
  "mpt-api-client==5.4.*",
  "typer==0.24.*",
]

[project.entry-points."cli.plugins"]
example = "example_plugin.app:app"
```

Example root app:

```python
import typer

from example_plugin.feature.app import app as feature_app

app = typer.Typer(
    name="example",
    help="Example plugin commands.",
)
app.add_typer(feature_app, name="feature")
```

After installation, the main CLI will expose the plugin as:

```bash
mpt-cli example --help
mpt-cli example feature --help
```

## Repository Example

The bundled audit plugin in this repository follows the same pattern:

- entry point in [`pyproject.toml`](../pyproject.toml): `audit = "cli.plugins.audit_plugin.app:app"`
- Typer app in [`cli/plugins/audit_plugin/app.py`](../cli/plugins/audit_plugin/app.py)

## Recommended Structure

For a standalone plugin repository, keep the structure simple:

```text
example_plugin/
  __init__.py
  app.py
  feature/
tests/
pyproject.toml
README.md
```

If the plugin grows, split command groups by feature directory and mount them from the root Typer app.

## Command Design Guidance

- expose one top-level Typer app from the plugin package
- use subcommand groups for larger features instead of putting everything into one file
- keep shared API or formatting helpers outside `app.py`
- reuse `mpt-cli` account and client helpers when the plugin needs Marketplace access

A practical pattern is:

- root `app.py` only wires command groups together
- feature-specific code lives in dedicated subpackages
- each feature can expose its own Typer app and be mounted into the root app

For example, the bundled audit plugin uses:

- [`cli/core/accounts/app.py`](../cli/core/accounts/app.py) to resolve the active account
- [`cli/core/mpt/mpt_client.py`](../cli/core/mpt/mpt_client.py) to create the Marketplace client

## Testing Plugins

At minimum, test:

- the plugin entry point imports correctly
- the root Typer app registers expected commands
- command behavior for the plugin-specific workflows

Keep plugin tests close to the plugin package structure, the same way this repository keeps plugin coverage under [`tests/cli/plugins/`](../tests/cli/plugins) and [`tests/plugins/`](../tests/plugins).

## Local Validation

For repository-local plugin work, reuse the local workflow from [`local-development.md`](local-development.md) and the validation guidance from [`testing.md`](testing.md).

For a standalone plugin repository, make sure the plugin is installed into the same environment where `mpt-cli` is executed, otherwise the entry point will not be discovered.
