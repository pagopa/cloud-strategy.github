# Refinement and Evaluation Criteria

Adapted from `addyosmani/agent-skills` release `0.6.1`. See `LICENSE.idea-refine-upstream`.

Use this rubric during Phase 2 (Evaluate and Converge) to stress-test idea directions. Not every criterion applies to every idea, so use judgment about which dimensions matter most for the specific context.

## Core Evaluation Dimensions

### 1. User Value

This is the most important dimension. If the value is not clear, nothing else matters.

**Painkiller vs. Vitamin:**

- **Painkiller:** Solves an acute, frequent problem. Users will actively seek this out, switch from their current solution, and often describe the problem with emotion.
- **Vitamin:** Nice to have. Makes something marginally better, but users do not go out of their way to adopt it.

**Questions to ask:**

- Can you name three specific people who have this problem right now?
- What are they doing today instead? The real competitor is usually the current workaround.
- Would they switch from their current approach? What would make them switch?
- How often do they encounter this problem?
- Is this a pull problem or a push problem?

**Red flags:**

- "Everyone could use this" - if you cannot name a specific user, the value is not clear.
- "It is like X but better" - marginal improvements rarely drive adoption.
- The problem is real but rare - high intensity and low frequency rarely justify a product.

### 2. Feasibility

Can you actually build this, not just technically but practically?

**Technical feasibility:**

- Does the core technology exist and work reliably?
- What is the hardest technical problem? Is it known-hard or novel?
- Are there dependencies on third parties, APIs, or data sources you do not control?
- What is the minimum technical stack needed?

**Resource feasibility:**

- What is the minimum team or effort needed to build an MVP?
- Does it require specialized expertise you do not have?
- Are there regulatory, legal, or compliance requirements?

**Time-to-value:**

- How quickly can you get something in front of users?
- Is there a version that delivers value in days or weeks, not months?
- What is the critical path? What has to happen first?

**Red flags:**

- "We just need to solve [very hard research problem] first."
- Multiple dependencies that all need to work simultaneously.
- The MVP still requires months of work.

### 3. Differentiation

What makes this genuinely different, not just better?

**Questions to ask:**

- If a user described this to a friend, what would they say? Is that description compelling?
- What is the one thing this does that nothing else does?
- Is this differentiation durable? Can a competitor copy it in a week?
- Is the difference something users actually care about or just something builders find interesting?

**Types of differentiation (strongest to weakest):**

1. **New capability:** Does something that was previously impossible.
2. **10x improvement:** So much better on a key dimension that it changes behavior.
3. **New audience:** Brings an existing capability to people who were excluded.
4. **New context:** Works in a situation where existing solutions fail.
5. **Better UX:** Same capability, dramatically simpler experience.
6. **Cheaper:** Same thing, lower cost.

**Red flags:**

- Differentiation is entirely about technology, not user experience.
- "We are faster, cheaper, prettier" without a structural reason why.
- The feature that differentiates is not the feature users care most about.

## Assumption Audit

For every idea direction, explicitly list assumptions in three categories.

### Must Be True (Dealbreakers)

Assumptions that, if wrong, kill the idea entirely. These need validation before building.

### Should Be True (Important)

Assumptions that significantly impact success but do not kill the idea. You can adjust the approach if they are wrong.

### Might Be True (Nice to Have)

Assumptions about secondary features or optimizations. Do not validate these until the core is proven.

## Decision Framework

When choosing between directions, rank them on this matrix:

|                    | High Feasibility | Low Feasibility |
|--------------------|------------------|-----------------|
| **High Value**     | Do this first    | Worth the risk  |
| **Low Value**      | Only if trivial  | Do not do this  |

Use differentiation as the tiebreaker between options in the same quadrant.

## MVP Scoping Principles

When defining MVP scope for the chosen direction:

1. **One job, done well.** The MVP should nail exactly one user job.
2. **The riskiest assumption first.** The MVP should test the assumption most likely to be wrong.
3. **Time-box, not feature-list.** Ask what you can build and test in a fixed timeframe.
4. **The "Not Doing" list is mandatory.** Explicitly name what you are cutting and why.
5. **If it is not embarrassing, you waited too long.** The first version should feel incomplete to the builder.
