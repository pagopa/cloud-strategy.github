# Internal Gateway Idea Evaluation

This directory defines the deterministic scorer contract for sanitized,
controlled observations from `internal-gateway-idea` runs.

`benchmark.json` declares the approved case IDs and exact observation fields.
`score_idea_eval.py` returns compact JSON with one result list for each guarded
branch and exits `0` for an accepted run, `1` for a scored rejection, or `2`
for malformed files or schema errors.

The fixture files are synthetic records used only to test scorer behavior.
They are not behavioral evidence from the idea gateway and must not be
described as a controlled runtime result. Controlled observations must contain
only the schema fields declared by the benchmark; do not retain prompts, raw
answers, chain-of-thought, repository content, or secrets.
