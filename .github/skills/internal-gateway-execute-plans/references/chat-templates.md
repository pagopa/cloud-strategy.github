# Plan Run Chat Templates

This reference owns localized executor chat states and progress summaries. Keep paths and commands in inline code without emoji.

<!-- protocol:chat-states -->
```text
STARTED 🚀 -> RUNNING
RUNNING 🔄 -> RUNNING
RESUMED 🔁 -> RUNNING
PAUSED ⏸️ -> PARTIAL
NEEDS CONFIRMATION 🟡 -> BLOCKED
BLOCKED 🛑 -> BLOCKED
NOT STARTED 🛑 (preflight) -> none
NOT STARTED ⚪ (query) -> none
PLAN TO REWRITE 📜 -> none
DONE ✅ -> DONE
```

## Message rules

- Localize every label and description to the user's language.
- Keep each message to at most five lines.
- The first line includes the state emoji, localized state, plan name, Task n/tot, progress bar, checkpoint, and 🧭 Reason. This combines the header and reason to meet the five-line limit.
- Follow with 🔍 Evidence, 📂 So far, and 🧪 Checks, in that order.
- Put one bold 🛠️ Action on the final line, except STARTED and RESUMED have no action line.
- Show changed paths in inline code. List included pre-existing files as Preexisting and unrelated changes as Foreign in the 📂 So far line; omit empty categories. Identify unattributed anomalies in Evidence or Rulings, never as proven authorship.
- Use one action that matches the current ledger or preflight result. Do not imply that resume grants approval or that a chat-only stop was persisted.
- A dirty-consent offer identifies the paths and current content identities, with the delta visible in the accompanying evidence. Renew it when content changes. For a conflicting run, name its plan and overlap and offer reconciliation of inactivity and pending writes, not a dirty-consent bypass or unconditional resume.
- Checks describe the observed checkout. Keep Foreign-related test failures visible; a passing check does not establish isolated-patch reproducibility.

## Progress bar

```text
cells = min(total_tasks, 10)
filled = floor(completed_tasks * cells / total_tasks)
bar = "▰" * filled + "▱" * (cells - filled)
n/tot is authoritative
```

A plan must contain at least one task. The bar has one cell per task up to ten tasks; for larger plans, it scales the completed fraction to ten cells.

## Per-task progress

```text
✔️ Task <n>/<tot> <bar> **<title>** · 🧪 <command> ok · CP<n>
```

## State templates

### STARTED 🚀

```text
🚀 <localized started> · <plan name> · Task <n>/<tot> <bar> · CP<n> · 🧭 <reason>
🔍 <task and posture>
📂 So far: <no task changes yet>
🧪 Checks: <commands and results>
```

### RUNNING 🔄

```text
🔄 <localized running> · <plan name> · Task <n>/<tot> <bar> · CP<n> · 🧭 <reason>
🔍 <evidence>
📂 So far: <paths or none>
🧪 Checks: <commands and results>
🛠️ **Action:** <continue the active task>
```

### RESUMED 🔁

```text
🔁 <localized resumed> · <plan name> · Task <n>/<tot> <bar> · CP<n> · 🧭 <reason>
🔍 <resume evidence>
📂 So far: <preserved partial changes>
🧪 Checks: <commands and results>
```

### PAUSED ⏸️

```text
⏸️ <localized paused> · <plan name> · Task <n>/<tot> <bar> · CP<n> · 🧭 <reason>
🔍 <evidence>
📂 So far: <completed work and preserved partial changes>
🧪 Checks: <commands and results>
🛠️ **Action:** resume
```

### NEEDS CONFIRMATION 🟡

```text
🟡 <localized needs confirmation> · <plan name> · Task <n>/<tot> <bar> · CP<n> · 🧭 <reason>
🔍 <evidence>
📂 So far: <paths or none>
🧪 Checks: <commands and results>
🛠️ **Action:** <the exact consent command offered>
```

### BLOCKED 🛑

```text
🛑 <localized blocked> · <plan name> · Task <n>/<tot> <bar> · CP<n> · 🧭 <reason>
🔍 <evidence>
📂 So far: <paths or none>
🧪 Checks: <commands and results>
🛠️ **Action:** <the one action from the controlling stop code>
```

### NOT STARTED 🛑 (preflight)

```text
🛑 <localized not started> · <plan name> · Task <n>/<tot> <bar> · CP<n> · 🧭 <reason>
🔍 <evidence>
📂 So far: no run initialized
🧪 Checks: <commands and results>
🛠️ **Action:** <resolve the failed preflight decision>
```

### NOT STARTED ⚪ (query)

```text
⚪ <localized not started> · <plan name> · Task <n>/<tot> <bar> · CP<n> · 🧭 <reason>
🔍 no run directory or ledger exists
📂 So far: no run initialized
🧪 Checks: <commands and results>
🛠️ **Action:** await an explicit execute request
```

### PLAN TO REWRITE 📜

```text
📜 <localized plan to rewrite> · <plan name> · Task <n>/<tot> <bar> · CP<n> · 🧭 <reason>
🔍 PLAN_INVALID/legacy
📂 So far: no task ran
🧪 Checks: <commands and results>
🛠️ **Action:** re-author <plan path> through /internal-gateway-writing-plans
```

### DONE ✅

```text
✅ <localized done> · <plan name> · Task <tot>/<tot> <bar> · CP<n> · 🧭 all planned tasks and final review passed
🔍 <final review evidence> · 📂 Changed: <paths or none> · Preexisting: <paths when included> · Foreign: <unrelated paths>
🧪 Checks: <commands and results> · Review: fresh <model> or self (weaker)
⚖️ Rulings: <ledger rulings or none> · 🧹 Deferred minors: <items or none>
🛠️ **Action:** <one final action or none>
```

The final message combines Evidence and So far on one line, preserving the ordered facts and the five-line limit. Omit empty Preexisting and Foreign categories. The Checks line always names the review kind; a self-review is marked weaker than a fresh review. Use the bold final action even when the action is none.
