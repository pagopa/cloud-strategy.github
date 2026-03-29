# Skill Evaluation Loop

Use this loop when improving a repository-owned skill without Claude-specific benchmarking infrastructure.

1. Pick 2-5 realistic prompts that should trigger the skill.
2. Add 2-5 near misses that should not trigger it.
3. Save the prompts somewhere disposable while iterating if that helps comparison.
4. Compare before and after behavior, or with-skill and without-skill behavior, using the same prompts.
5. Record the repeated mistakes:
   - trigger misses
   - trigger collisions
   - vague instructions
   - wasted steps
   - missing helper material
6. Improve the skill to solve the repeated mistakes, not just one example.
7. Rerun the same prompt set and confirm the change actually helped.
