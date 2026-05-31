---
name: internal-go
description: Use when creating, editing, or reviewing Go files, modules, or dependency metadata before advanced Go service depth is needed.
---

# Internal Go

## Referenced skills

- `antigravity-golang-pro`: advanced Go architecture, concurrency, profiling, CLIs, services, and production readiness.

## When to use

- `.go`, `go.mod`, or `go.sum` changes.
- Lightweight Go reviews focused on idioms, module hygiene, naming, error handling, or tests.
- Small Go fixes where the target package and validation path are concrete.

## When not to use

- Deep concurrency design, service architecture, profiling, or production-readiness work; use `antigravity-golang-pro`.
- Generic YAML, Docker, Terraform, or CI changes that merely invoke Go tooling.

## Baseline

- Keep Go simple, explicit, and idiomatic.
- Preserve the package declaration and use the package name already established in the directory.
- Prefer early returns, useful zero values, and small interfaces near the consumer.
- Wrap errors with context using `%w` when propagation matters.
- Use the standard library before adding dependencies unless a mature library clearly reduces complexity.
- Run `gofmt`; use `goimports` when imports change and the tool is available.
- Keep tests deterministic and close to public behavior.

## Escalation

Use `antigravity-golang-pro` when goroutine lifecycle, channel design, memory profile, API surface, CLI structure, or production failure modes become the real problem.

## Validation

- `go test ./...` when the repository is a Go module and the scope is broad enough.
- A focused `go test` package command for narrow changes.
- `go mod tidy` only when dependency or module metadata intentionally changes.
