---
applyTo: "**/Makefile,**/*.mk"
---

# Makefile Instructions

## Conventions
- Use lowercase, hyphenated target names.
- Mark non-file targets with `.PHONY`.
- Keep commands deterministic and readable.

## Recommended patterns
- Provide a `help` target.
- Centralize common variables near the top.
- Avoid hidden side effects in default targets.

## Minimal example
```make
.PHONY: help test

help:
	@echo "Available targets: test"

test:
	@echo "Run test suite"
```

## Output
- Keep runtime output in English.
- Use clear success/error messages.
