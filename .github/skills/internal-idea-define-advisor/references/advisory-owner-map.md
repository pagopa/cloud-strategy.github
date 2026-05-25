# Advisory Owner Map

Use this reference when `internal-idea-define-advisor` must explain which simple path or support should be recommended next without turning the skill into a hidden router.

## Relationship Labels

- `candidate next path`: the direct path that should be taken if the user approves it.
- `optional support`: support that may be loaded only when its trigger is positively met.
- `not this skill`: work that should be rejected or handed off because it is outside the advisory contract.

Use these labels explicitly when the distinction matters. Keep surrounding flow ownership out of this file.

## Decision Classes

| Decision class | Typical signal | Best relationship | Typical path or support |
| --- | --- | --- | --- |
| One quick concrete lane | Target, action, and validation are already concrete. | `candidate next path` | `internal-gateway-simple-task` |
| Defer to another approved path | The task needs a path that is not owned by this lightweight advisor. | `not this skill` | another path chosen outside this bundle |
| Exploratory option shaping | Multiple credible directions remain and the choice is still concept-heavy. | `optional support` | `idea-refine` |
| User-only unresolved decisions | Repository evidence cannot settle scope, owner, validation, or anti-scope. | `optional support` | `grill-me` |

## `idea-refine` Rules

Positive triggers:

- The question is about choosing among multiple plausible boundaries, paths, or concept directions.
- Divergent exploration can still change the recommended path or next action.
- Hidden assumptions are likely to invalidate a fast recommendation.

Negative triggers:

- The decision is mainly deterministic and recoverable from local evidence.
- Only a single user confirmation or narrow preference is missing.
- The choice is between executing an already-approved plan and not executing it.

Fallback:

- If positive triggers are weak or absent, stay with the minimum evidence pass plus `grill-me`.

## Stop Conditions

- Stop when the user has not approved the next visible path.
- Stop when the request is already in `execute`, `apply-plan`, `review`, or critical mode and the lane is settled.
- Stop when the work becomes catalog governance, consumer propagation, or broad sync maintenance.
- Stop when local evidence shows that only a concrete implementation step remains.
