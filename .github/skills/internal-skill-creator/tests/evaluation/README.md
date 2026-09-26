# Internal Skill Creator Evaluation

`evals.json` is the fixed structural and behavioral case pack for the creator.
Case specifications are `generated` or `not-run`; no runtime run records exist. `generated`,
`not-run`, and `blocked` describe specification evidence state. `passed` is
only available in a separate run record after an observed, graded run.
The pack migrates all six delegation cases: three eligible modes, two local or
parent-owned near-misses, and the Copilot agent competing-owner route.

## Validate

From the repository root, run:

```bash
python3 .github/skills/internal-skill-creator/scripts/check_eval_pack.py \
  .github/skills/internal-skill-creator/tests/evaluation/evals.json \
  --bundle-root .github/skills/internal-skill-creator \
  --skill-name internal-skill-creator --format compact
```

The host validator may check the same pack when the host provides that gate.
The bundle checker remains usable without the host tool.

## Runtime plan and current gap

No runtime run record is included. A runtime pilot requires explicit user
approval. Start with GPT-6 and pin the host, model, tools, inputs, and budget
before comparing isolated with-skill and baseline sessions. Keep each case's
criteria fixed, include held-out tasks, inspect artifacts and transcripts, and
record every result separately. Three repeats per case and variant are a pilot,
not statistical proof.

Runtime invocation and downstream effectiveness remain unmeasured because no
executable skill resolver or approved model run is available in this repository.
The cases provide structural coverage and a reviewable run plan only.
