# Contributing

This document captures repository-specific contribution guidance.

Shared engineering rules live in `mpt-extension-skills` and should not be duplicated here:

- documentation standard: [documentation.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/standards/documentation.md)
- makefile structure: [makefiles.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/standards/makefiles.md)
- commit message rules: [commit-messages.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/standards/commit-messages.md)
- dependency management: [packages-and-dependencies.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/standards/packages-and-dependencies.md)
- pull request rules: [pull-requests.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/standards/pull-requests.md)
- Python coding conventions: [python-coding.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/standards/python-coding.md)

Shared operational knowledge also applies:

- build and validation flow: [knowledge/build-and-checks.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/knowledge/build-and-checks.md)
- common make target meanings: [knowledge/make-targets.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/knowledge/make-targets.md)

## Development Model

The supported development model for this repository is Docker-based.

- use `make build` to build the local image
- use `make bash` for an interactive shell in the app container
- use `make run` to run the repository container setup
- use Docker-backed CLI invocations for manual command checks

## Code Organization Expectations

Repository-specific expectations:

- keep top-level CLI wiring in [`cli/swocli.py`](../cli/swocli.py)
- keep account-specific behavior under [`cli/core/accounts/`](../cli/core/accounts)
- keep shared Marketplace API behavior under [`cli/core/mpt/`](../cli/core/mpt)
- keep product workflows under [`cli/core/products/`](../cli/core/products)
- keep price list workflows under [`cli/core/price_lists/`](../cli/core/price_lists)
- keep shared file and service abstractions under [`cli/core/handlers/`](../cli/core/handlers) and [`cli/core/services/`](../cli/core/services)
- keep extensibility and optional commands under [`cli/plugins/`](../cli/plugins)
- keep tests under [`tests/`](../tests), mirroring production structure where practical
- update the matching file under [`docs/`](.) when user-facing behavior, workflow, or repository policy changes

## Validation Before Review

Follow the shared validation flow in [knowledge/build-and-checks.md](https://github.com/softwareone-platform/mpt-extension-skills/blob/main/knowledge/build-and-checks.md).

Repository-specific entry points are the `make` targets documented in [`local-development.md`](local-development.md) and [`testing.md`](testing.md).

## Documentation Changes

Documentation rules live in [documentation.md](documentation.md).

When changing docs, update the smallest relevant file instead of duplicating policy across multiple documents.
