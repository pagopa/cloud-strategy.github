---
name: superpowers-brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
---

# Brainstorming Ideas Into Designs

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then Ask clarifying questions in numbered bulk question blocks. Each question must include a short recommendation, a short reason for that recommendation, and the default that will be treated as accepted when the user accepts the suggestions. Once you understand what you're building, decide whether a retained spec adds real design value or whether moving directly to an implementation plan is the better next step.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

## Checklist

You MUST create a task for each of these items and complete them in order:

1. **Explore project context** — check files, docs, recent commits
2. **Offer the visual companion just-in-time** — NOT upfront. The first time a question would genuinely be clearer shown than described, offer it then (its own message); on approval its browser tab opens for you. If no visual question ever arises, never offer it. See the Visual Companion section below.
3. **Ask clarifying questions** — use numbered bulk question blocks with `Question`, `Recommendation`, `Why`, and `Default if accepted`
4. **Propose 2-3 approaches** — with trade-offs and your recommendation
5. **Present design** — in sections scaled to their complexity, get user approval after each section
6. **Run the Design-Depth Gate** — choose `Decision: direct plan` or `Decision: spec first`, and tell the user why
7. **Write design doc when needed** — if the gate chooses `spec first` and the user wants a retained file, save it to `tmp/superpowers/specs/YYYY-MM-DD-<topic>-design.md`; never commit files from `tmp/`
8. **Spec self-review when needed** — quick inline check for placeholders, contradictions, ambiguity, scope (see below)
9. **User reviews written spec when needed** — ask user to review the spec file before proceeding
10. **Transition to implementation planning** — invoke writing-plans skill after the user approves either the design or the direct-plan recommendation

## Process Flow

```dot
digraph brainstorming {
    "Explore project context" [shape=box];
    "Ask bulk clarifying questions" [shape=box];
    "Propose 2-3 approaches" [shape=box];
    "Present design sections" [shape=box];
    "User approves design?" [shape=diamond];
    "Design-Depth Gate" [shape=diamond];
    "Write design doc" [shape=box];
    "Spec self-review\n(fix inline)" [shape=box];
    "User reviews spec?" [shape=diamond];
    "Invoke writing-plans skill" [shape=doublecircle];

    "Explore project context" -> "Ask bulk clarifying questions";
    "Ask bulk clarifying questions" -> "Propose 2-3 approaches";
    "Propose 2-3 approaches" -> "Present design sections";
    "Present design sections" -> "User approves design?";
    "User approves design?" -> "Present design sections" [label="no, revise"];
    "User approves design?" -> "Design-Depth Gate" [label="yes"];
    "Design-Depth Gate" -> "Invoke writing-plans skill" [label="direct plan"];
    "Design-Depth Gate" -> "Write design doc" [label="spec first"];
    "Write design doc" -> "Spec self-review\n(fix inline)";
    "Spec self-review\n(fix inline)" -> "User reviews spec?";
    "User reviews spec?" -> "Write design doc" [label="changes requested"];
    "User reviews spec?" -> "Invoke writing-plans skill" [label="approved"];
}
```

**The terminal state is invoking writing-plans.** Do NOT invoke frontend-design, mcp-builder, or any other implementation skill. The ONLY skill you invoke after brainstorming is writing-plans. The path to writing-plans may be either `Decision: direct plan` or `Decision: spec first`.

## The Process

**Understanding the idea:**

- Check out the current project state first (files, docs, recent commits)
- Before asking detailed questions, assess scope: if the request describes multiple independent subsystems (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately. Don't spend questions refining details of a project that needs to be decomposed first.
- If the project is too large for a single spec, help the user decompose into sub-projects: what are the independent pieces, how do they relate, what order should they be built? Then brainstorm the first sub-project through the normal design flow. Each sub-project gets its own spec → plan → implementation cycle.
- For appropriately-scoped projects, ask clarifying questions in numbered bulk question blocks to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Each numbered question must use this format: `Question`, `Recommendation`, `Why`, and `Default if accepted`
- The recommendation and why must be clear and brief
- The user may accept all suggested defaults, accept only some numbered defaults, or override any numbered recommendation
- Accepted defaults do not mean discovery is complete. If the accepted answers create contradictions, weak assumptions, unresolved risks, or dependent decisions, ask another focused numbered bulk question block.
- Ask another focused numbered bulk question block only for unresolved, dependent, or reopened branches. Do not ask questions that project evidence can answer.
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**

- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**

- Once you believe you understand what you're building, present the design
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

**Design-Depth Gate:**

Before writing a retained spec, decide whether the spec has meaningful marginal value over going directly to an implementation plan.

Choose `Decision: direct plan` when the target, owner, scope, constraints, rejected alternatives, and validation path are already clear, and a retained spec would mostly duplicate the implementation plan.

Choose `Decision: spec first` when product, design, architecture, data flow, user experience, rollout, or risk decisions are still material enough that a retained spec would reduce the chance of building the wrong thing.

In both cases, tell the user the decision and one short reason:

- `Decision: direct plan`
- `Why: <one short evidence-based sentence>`
- `Decision: spec first`
- `Why: <one short evidence-based sentence>`

Ask for user approval before invoking writing-plans. Direct plan skips the retained spec, not the user approval gate.

**Design for isolation and clarity:**

- Break the system into smaller units that each have one clear purpose, communicate through well-defined interfaces, and can be understood and tested independently
- For each unit, you should be able to answer: what does it do, how do you use it, and what does it depend on?
- Can someone understand what a unit does without reading its internals? Can you change the internals without breaking consumers? If not, the boundaries need work.
- Smaller, well-bounded units are also easier for you to work with - you reason better about code you can hold in context at once, and your edits are more reliable when files are focused. When a file grows large, that's often a signal that it's doing too much.

**Working in existing codebases:**

- Explore the current structure before proposing changes. Follow existing patterns.
- Where existing code has problems that affect the work (e.g., a file that's grown too large, unclear boundaries, tangled responsibilities), include targeted improvements as part of the design - the way a good developer improves code they're working in.
- Don't propose unrelated refactoring. Stay focused on what serves the current goal.

## After the Design

**Documentation:**

- Write the validated design (spec) to chat by default
- Persist it to `tmp/superpowers/specs/YYYY-MM-DD-<topic>-design.md` only when `Decision: spec first` is chosen and the user explicitly wants a retained file
  - (User preferences for spec location override this default)
- Use elements-of-style:writing-clearly-and-concisely skill if available
- Never commit files from `tmp/`

**Spec Self-Review:**
After writing the spec document, look at it with fresh eyes:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. **Internal consistency:** Do any sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope check:** Is this focused enough for a single implementation plan, or does it need decomposition?
4. **Ambiguity check:** Could any requirement be interpreted two different ways? If so, pick one and make it explicit.

Fix any issues inline. No need to re-review — just fix and move on.

**User Review Gate:**
After the spec review loop passes, ask the user to review the written spec before proceeding:

> "Spec written to `<path>`. Please review it and let me know if you want to make any changes before we start writing out the implementation plan."

Wait for the user's response. If they request changes, make them and re-run the spec review loop. Only proceed once the user approves.

**Implementation:**

- Invoke the writing-plans skill to create a detailed implementation plan after the user approves either `Decision: direct plan` or the reviewed spec
- Do NOT invoke any other skill. writing-plans is the next step.

## Key Principles

- **Bulk guided question blocks** - Ask the full known question set together, with recommendations, reasons, and defaults
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design, get approval before moving on
- **Be flexible** - Go back and clarify when something doesn't make sense

## Visual Companion

A browser-based companion for showing mockups, diagrams, and visual options during brainstorming. Available as a tool — not a mode. Accepting the companion means it's available for questions that benefit from visual treatment; it does NOT mean every question goes through the browser.

**Offering the companion (just-in-time):** Do NOT offer it upfront. Wait until a question would genuinely be clearer shown than told — a real mockup / layout / diagram question, not merely a UI *topic*. The first time that happens, offer it then, as its own message:
> "This next part might be easier if I show you — I can put together mockups, diagrams, and comparisons in a browser tab as we go. It's still new and can be token-intensive. Want me to? I'll open it for you."

**This offer MUST be its own message.** Only the offer — no clarifying question, summary, or other content. Wait for the user's response. If they accept, start the server with `--open` so their browser opens to the first screen automatically. If they decline, continue text-only and don't offer again unless they raise it.

**Per-question decision:** Even after the user accepts, decide FOR EACH QUESTION whether to use the browser or the terminal. The test: **would the user understand this better by seeing it than reading it?**

- **Use the browser** for content that IS visual — mockups, wireframes, layout comparisons, architecture diagrams, side-by-side visual designs
- **Use the terminal** for content that is text — requirements questions, conceptual choices, tradeoff lists, A/B/C/D text options, scope decisions

A question about a UI topic is not automatically a visual question. "What does personality mean in this context?" is a conceptual question — use the terminal. "Which wizard layout works better?" is a visual question — use the browser.

If they agree to the companion, read the detailed guide before proceeding:
`skills/brainstorming/visual-companion.md`
