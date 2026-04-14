# Local Development

This repository uses Docker as the default and supported local execution model.

## Prerequisites

- Docker with the `docker compose` plugin
- `make`
- optional: [CodeRabbit CLI](https://www.coderabbit.ai/cli) for `make review`

## Setup

1. Clone the repository.
2. Build the local image:

```bash
make build
```

3. Run the test suite:

```bash
make test
```

## Local Runtime Model

- [`compose.yaml`](../compose.yaml) mounts the repository into the `app` container at `/cli`
- local account configuration is mounted from `.swocli/` into `/root/.swocli`
- [`Dockerfile`](../Dockerfile) defines a dev image with development dependencies and a prod image with runtime dependencies only

## Common Commands

Use the repository-provided entry points instead of ad hoc host commands:

```bash
make build
make run
make bash
make test
make check
make check-all
make format
make review
```

## Running The CLI

Start an interactive container shell:

```bash
make bash
```

Run CLI commands in Docker:

```bash
docker compose run --rm app python -m cli.swocli --help
docker compose run --rm app python -m cli.swocli accounts list
docker compose run --rm app python -m cli.swocli products list
```

See [usage.md](usage.md) for command-level examples.

## Account Storage

Account metadata is stored in `.swocli/accounts.json` in the repository working copy and mounted into the container.

This keeps CLI credentials and active-account state available across Docker runs without writing into the container image.

## Dependency And Environment Notes

- follow the shared dependency workflow from [packages-and-dependencies.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/standards/packages-and-dependencies.md)
- rebuild the image with `make build` after lockfile or dependency changes
- do not treat direct host Python execution as the supported development path for this repository
