# Existing-Infrastructure Adoption Safety Delta

Use this reference only when a request adopts existing infrastructure or
reconstructs management of resources that already exist. It provides guidance
and routing context; the selected owner and native runtime remain authoritative.

## Reconcile Before Mutation

Treat the desired representation, live representation, and state
representation as separate evidence. Reconcile all three before any adoption
or mutation decision. Missing, conflicting, or ambiguous evidence is unknown;
unknown evidence must fail closed and stop the operation.

Canonical identity is the stable identity used to compare the desired, live,
and state representations. Establish one unambiguous identity before
proceeding. If identity cannot be established or more than one identity is
plausible, stop and record the ambiguity rather than guessing or discovering
through an implicit procedure.

## Ownership and Mutation Policy

Classify the resource as unmanaged, already managed, transferred, or disputed.
Adoption and any live or state mutation require explicit authority. Do not
silently transfer ownership, overwrite an existing manager, destroy a resource,
or make an implicit ownership change. A disputed or unknown disposition stops
the operation until the authority and intended disposition are recorded.

Adoption establishes or reconstructs management identity without silently
changing live configuration. Convergence is a later, separately authorized
decision to change live configuration after adoption evidence is accepted.
Keep adoption and convergence separate; do not combine them in one apply.

## Five Ordered Phase Gates

Pass each gate in order and retain the stated evidence. A stop condition at any
gate prevents the next gate from being treated as passed.

1. **Identity and inventory** — Record the inventory boundary and canonical
   identity evidence. Stop when inventory is incomplete or identity is missing,
   conflicting, or ambiguous.
2. **Desired/live/state reconciliation** — Compare the three representations
   and record their status and differences. Stop when reconciliation is
   incomplete or an unknown difference would affect adoption or mutation.
3. **Ownership and mutation disposition** — Record the ownership classification,
   intended adoption or non-adoption disposition, and mutation authority. Stop
   when disposition or authority is absent, disputed, or would require an
   implicit or destructive change.
4. **Adoption evidence and controlled execution** — Record the approved
   adoption evidence, execution mode, and bounded action before proceeding.
   Stop when the evidence is unavailable, the action is not explicitly safe,
   or the requested execution would also perform convergence.
5. **Verification and recovery** — Verify the resulting identity, state, and
   live relationship, and record any recovery delta. Stop when verification is
   unavailable, contradicts the expected result, or recovery would require an
   unapproved mutation.

## Runtime-Aware Evidence

For each phase, record the runtime and version, root or working path, command or
artifact, phase, result, and recovery delta. Identify whether evidence is
declarative or imperative. Keep configuration, import, state, and plan evidence
distinct from CLI, API, or discovery evidence; one mode does not substitute for
the other without an explicit equivalence decision. Unavailable runtime
evidence is not a success and must remain an unresolved evidence gap.

## Bounded Recovery

Preserve evidence across recovery. Stop on ambiguity or unsafe mutation. Retry
only an explicitly safe action whose expected evidence change is recorded.
Require authority before changing state or live infrastructure, and record what
changed in the recovery delta. Do not invent universal batch sizes, state
thresholds, retry counts, or other fixed limits; bound recovery by evidence,
authority, and safety instead.

## Handoff Output

The wrapper handoff retains these fields:

- `Primary`
- `Reason`
- `Context`
- `Validation`

Include the following adoption context when known, and mark unknown values
explicitly:

- identity status;
- desired, live, and state status;
- ownership disposition;
- mutation authority;
- adoption-versus-convergence decision;
- phase-gate status;
- runtime and evidence mode;
- recovery status; and
- unresolved ambiguity.

## Anti-Scope

This reference does not provide provider-specific procedures, automatic
import-everything behavior, fixed quotas or universal thresholds, a combined
adoption/convergence apply, a new plan parser, or runtime enforcement. It does
not replace Anton's read-only Terraform domain ownership or `/internal-tf`'s
language and HCL ownership.

## Temporary Local Override and Sunset

A local override is permitted only for a uniquely repository-specific adoption
edge. It must name its owner and a sunset trigger or date, must not alter the
imported bundle, and must be removed when the upstream capability covers the
safety delta. Temporary analysis or handoff artifacts are not runtime
dependencies.
