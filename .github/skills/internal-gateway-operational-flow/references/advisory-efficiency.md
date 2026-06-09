# Advisory Efficiency And Stop Conditions

Use this reference when the operational flow needs detailed guidance on workflow efficiency without weakening mandatory evidence or user checkpoints.

- Prefer fewer model turns, compact handoffs, and bounded evidence passes when correctness is unchanged.
- classify -> bounded evidence pass -> action-readiness checkpoint -> focused action -> focused validation -> one broad final validation.
- Set an evidence-pass budget, batch independent reads/searches when runtime permits, and stop broadening when the budget is spent or the next exact patch target is known.
- Prefer compact decision projections over rereading full structured outputs.
- Do not rerun an unchanged validation command unless external state changed or the prior result was incomplete.
- Stop when evidence is complete, a falsifiable hypothesis exists, next owner and action are exact, and a validation path exists.
- Replan when scope, owner, target state, validation, rollout, or anti-scope changes.
- Do not treat call count or token count as permission to skip mandatory evidence, gates, approvals, or validation. Metrics are advisory only.
