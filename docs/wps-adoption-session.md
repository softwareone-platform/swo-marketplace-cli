# WPS Adoption Session Log

Date: 2026-02-12
Repository: swo-marketplace-cli

## Scope
Adopt wemake-python-styleguide (WPS) incrementally.

## Actions completed in this session
1. Removed Flake8 explicit selector from check command so checks use `pyproject.toml`:
   - Updated `/Users/susana.vazquez/Projects/swo-marketplace-cli/makefile` `check` target from `flake8 --select AAA .` to `flake8 .`.
2. Generated baseline violations report:
   - `/Users/susana.vazquez/Projects/swo-marketplace-cli/wps-baseline-raw.txt`
3. Extracted unique WPS codes and counts:
   - `/Users/susana.vazquez/Projects/swo-marketplace-cli/wps-error-codes.txt`
   - `/Users/susana.vazquez/Projects/swo-marketplace-cli/wps-error-codes-count.txt`
4. Added temporary Flake8 baseline suppressions in `/Users/susana.vazquez/Projects/swo-marketplace-cli/pyproject.toml` under `[tool.flake8].per-file-ignores` for all currently reported WPS codes.

## Baseline summary
- Total violations: 2143
- Unique WPS codes: 55
- Highest-volume codes currently:
  - WPS110: 133
  - WPS432: 99
  - WPS111: 69
  - WPS300: 44
  - WPS221: 44
  - WPS210: 40

## Iterative cleanup protocol for future PRs
1. Pick one code from `wps-error-codes.txt`.
2. Remove that code from `[tool.flake8].per-file-ignores`.
3. Fix all resulting violations in small scoped changes.
4. Run `make check` and `make test`.
5. Open PR titled with conventional commits (`refactor:`/`fix:`).

## Decision log
- Pending user guidance per code family (requested by team workflow).
- First code to discuss in next step: `WPS110` (highest volume).
