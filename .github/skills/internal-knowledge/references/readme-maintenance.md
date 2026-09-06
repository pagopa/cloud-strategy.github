# README Maintenance

Use this reference to create or refresh README files for repository-relative directories or explicit README paths supplied by the user.

## Scope

1. Accept repository-relative directories such as `.` or `src/service-a`, and explicit paths named `README.md` such as `README.md` or `src/service-a/README.md`. Normalize directories to `<target>/README.md`; the normalized destinations form the complete README-authoring allowlist. In `sync` and `setup`, those destinations come from the approved plan and form the same closed allowlist.
2. Reject absolute paths, traversal, globs, duplicate normalized destinations, escaping symlinks, missing parent directories, and unusable README destinations. If any target fails, stop before writing any target. Report a preflight table with `input`, `resolved target`, `README destination`, and `resolved / failed`.
3. Read each existing README and capture its current state before drafting. Recheck it immediately before writing and stop on concurrent changes.
4. Read outside a target only for bounded evidence. Never expand the write allowlist while drafting: in `targeted` it is the supplied set, and in `sync` and `setup` it is the approved plan. A component or manifest entry discovered after approval produces a reported gap, not a write.
5. When the repository serves a profile README from `.github/README.md`, treat it as the displayed entry point and the root `README.md` as the in-repository entry point. State which is which, and stop before writing when the two contradict each other.

## Evidence and Content

Apply repository instructions and the nearest documentation contract. Derive claims from source, configuration, interfaces, manifests, tests, workflows, scripts, ADRs, and existing documentation. Treat general technology knowledge as guidance, not evidence of repository behavior.

For each target, record its scope, primary nature, reader outcome, document language, applicable sections, and evidence status. Preserve the existing language unless the user or a local contract requires another. Resolve the profile from the nearest owner or target metadata, direct target behavior and interfaces, repository documentation, then a neutral fallback. Use `evidenced`, `inferred`, `not evidenced`, or `conflicting` for purpose, audience, ownership, consumers, effects, identities, and lifecycle. State only evidenced claims as facts and stop on authoritative conflicts.

When several natures are supported, apply this nature precedence:

1. Use a verified local contract or target metadata as the primary nature when target evidence does not conflict.
2. Select `mixed` only when at least two independently evidenced natures have separate lifecycle phases or interfaces that materially change the reader path. Multiple file types alone do not make a target mixed.
3. Otherwise select the directly evidenced nature that supports the explicit reader outcome. If none is explicit, use this composition precedence as the deterministic tie-breaker: IaC or infrastructure, workflow or custom action, deployable application or service, library or package, CLI or tool, data/configuration/policy, then documentation/reference/integration.

Every README needs a proportionate title, summary, purpose or scope, useful reader path, and validation guidance. When no repository contract states otherwise, use `Purpose`, `Responsibilities`, `Inputs and outputs`, `Dependencies`, and `Validation` as the default component section set, and drop any section the target does not evidence. A repository-owned README contract always wins over this default; preserve a repository-owned README marker exactly as found and never introduce one. Add only sections supported by the target, such as usage, change path, architecture, inputs and outputs, configuration, dependencies, operations, security, ownership, or related documentation. Avoid empty sections and duplicate headings. Treat headings with the same semantic purpose as one section and prefer the most specific evidence-backed heading. Add a table of contents (TOC) when there are at least three authored top-level sections, excluding the title, the TOC itself, and generated sections, or when a local contract requires one. Place the TOC immediately after the title and summary, keep entries in document order, omit the TOC heading itself, and do not enumerate generated Terraform headings. If fewer than three authored top-level sections exist and no local contract requires a TOC, omit it and record `omitted-with-reason`.

Adapt emphasis to the target:

- Applications, services, tools, and workflows: prerequisites, interfaces, usage or change path, operational behavior, and safe validation.
- Infrastructure: distinguish roots from reusable modules; document ownership and state boundaries, inputs, outputs, repository wrappers, existing examples, consumers, and non-mutating validation.
- GitHub actions and workflows: distinguish custom actions, reusable workflows, and internal workflows; document only evidenced triggers, inputs, outputs, secrets metadata, permissions, callers, and release behavior.
- Libraries and CLIs: installation, compatibility, public interface, minimal usage, and tests.
- Data, configuration, and policy: shape, scope, source of truth, consumers, effects, precedence, lifecycle, and validation.
- Documentation and integration surfaces: authority, audience, navigation, related sources, update path, and link or format checks.
- Monorepo roots: concise component map and cross-component boundaries, linking existing component READMEs without reproducing them.

For cloud account or execution-boundary targets, keep these concepts separate when evidenced:

- the logical infrastructure root or reusable module;
- the physical account, subscription, project, tenant, or execution context and its state boundary;
- the bootstrap, payer, management, or foundation owner and the target it provisions;
- the workflow caller, assumed identity, runtime identity, and managed target identity or resource.

Use stable checked-in names instead of live identifiers. Document only direct trust, caller, and identity edges supported by code or configuration; naming alone does not prove separate accounts or direct invocation.

When declarative source drives a runtime effect, explain the phases separately: desired state, coordinator or trigger, side effect, downstream consumer, and retry or recovery. Use a table only when it makes comparison, effect, or ownership clearer than prose.

Preserve still-valid facts, links, commands, badges, and generated blocks. Keep every existing generated block byte-for-byte; report conflicts instead of rewriting or regenerating it. Authored prose and diagrams go before the opening marker of a generated block: content placed after it sits in territory the generator owns and disappears on its next run, which the current diff never shows. Never include secrets, personal data, state content, sensitive output, or unnecessary live identifiers.

Use Mermaid only when at least three material evidenced relationships are clearer as a diagram. Prefer stable `flowchart` and `sequenceDiagram` syntax. Include `accTitle` and `accDescr`, use stable ASCII identifiers, and explain the diagram in adjacent prose. Forbidden features unless a compatible renderer is verified: beta diagram types, icon packs, HTML labels, `click`, themes, and custom styling. Create at most two diagrams.

Include a diagram only when the threshold is met and it improves the stated reader outcome. Otherwise omit it; when the omission needs explanation, record `omitted-with-reason` in the completion report. If another document already draws the relationship, link to it in the report or surrounding prose rather than redrawing a diagram a second document owns. Do not add fixed in-document diagram boilerplate merely to account for an omission.

Verify each diagram before writing it, by rendering it or by parsing it offline when no renderer is reachable. An unreachable renderer neither excuses the verification nor justifies dropping a warranted diagram. Write the arrows as literal `-->` and `->>`: an editing tool that emits `&gt;` or `&lt;` inside the fence produces a block that reads correctly in the diff and fails to parse.

## Validation and Completion

Before writing, verify every target path, material claim, local link, command, heading, placeholder, generated block, and security-sensitive value. Resolve local links from the README directory; check external-link syntax and test reachability only when a safe network tool is available. Confirm that commands use evidenced working directories and repository wrappers. Execute only safe non-mutating checks, and distinguish static checks, executed checks, and checks not run with reasons.

Treat local templates, coverage manifests, README validators, and documentation generators as optional integrations. A manifest may inform coverage but never expands the write allowlist. Run an existing README validator only when its scope is understood. Run a documentation generator only when a repository owner requires it and its verified write scope is the selected README; never regenerate an existing block during maintenance.

Prepare and validate every selected draft before the first write. Recheck destination snapshots and generated blocks immediately before writing; any draft failure or concurrent change means zero writes for the batch. That batch consistency check is not an atomic-write or rollback promise: do not promise filesystem-level atomic writes or destructive rollback. Leave byte-equivalent README files untouched. Report each target as created, refreshed, unchanged, or failed, including static, executed, and not-run validation and every `omitted-with-reason` entry.

A local README validator proves only the paths it actually covered. It is not universal proof of the supplied target set, of unselected paths, or of semantic heading equivalence.

When a check resolves links or anchors, exclude generated blocks from the scanned body while still collecting the anchors they define, such as the HTML anchors a Terraform documentation generator emits. Scanning their body reports links the document does not own; ignoring their anchors reports valid references as broken. Derive an anchor from a heading by replacing each whitespace character, not each run of them: a heading that loses a punctuation mark keeps the two spaces around it, and the resulting anchor carries a double separator that a collapsing implementation never produces.
