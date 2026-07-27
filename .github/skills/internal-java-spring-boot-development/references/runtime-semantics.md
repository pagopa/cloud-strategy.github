# Spring Boot Runtime Semantics

Load this reference when Boot dependency management, bean wiring, transaction
proxies, scheduling, startup behavior, or virtual-thread enablement determines
correctness.

## Dependency management

- Identify the active Boot parent, plugin, BOM, Java compatibility, wrapper, and
  repository dependency-management mechanism before changing versions.
- Prefer Boot-managed dependency versions and starters. Avoid redundant
  overrides unless the project has an explicit compatibility or security reason
  and the resulting dependency graph is validated.
- Check the active project's build and current official documentation for
  version-sensitive plugin, BOM, starter, and auto-configuration behavior.

## Bean wiring

- Use constructor injection for required dependencies and represent optional
  dependencies explicitly in the type or configuration contract.
- Keep bean responsibilities focused. Treat excessive constructor arguments as
  a design review cue and split collaborators when the boundaries are clear.
- Diagnose bean cycles from the ownership graph and correct the boundary or
  lifecycle rather than hiding the cycle with incidental lazy behavior.

## Transactions

- Enter a transaction through the proxy-visible public boundary that owns the
  atomic behavior. Self-invocation does not cross the proxy in the usual
  proxy-based model, so verify the actual wiring before changing annotations.
- Check rollback rules, annotation placement, transaction-manager selection, and
  whether the code uses an imperative or reactive model.
- Keep the transaction narrow and do not assume a database transaction covers
  external calls or messaging without an explicit coordination contract.

## Scheduling and startup

- Confirm scheduling enablement, executor and scheduler ownership, lifecycle,
  overlap behavior, and shutdown semantics against the active Boot line.
- Make startup failures visible. Do not convert missing required configuration,
  bean wiring failures, or scheduler initialization errors into silent fallback.

## Virtual-thread enablement

- Evaluate `spring.threads.virtual.enabled` only after checking Java and Boot
  compatibility, the blocking or non-blocking execution model, and the effects
  on Boot-managed executors and schedulers.
- Account for daemon-thread keep-alive behavior, context propagation,
  observability, and downstream resource bounds. Virtual threads do not remove
  database, connection-pool, rate-limit, or remote-service limits.
- Validate the choice with representative load and failure behavior, including
  cancellation, timeouts, tracing, metrics, and application shutdown.
