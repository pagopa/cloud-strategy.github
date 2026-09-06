# Codebase-improvement gateway evaluation

This harness scores sanitized observations from controlled Chat Debug runs. It
does not parse gateway instructions or generated report prose.

Use the same model identifier and seeded-target fingerprint for every case in a
run. Record the model identifier, SHA-256 fingerprints of the gateway, core,
critic, and seeded target, and the loaded skill identities in the run metadata.
Remove repository content, prompts, report prose, and other sensitive material
before saving the observation.

Each case records the completed report and its critic input:

```json
{
  "case_id": "CLEAR_REPORT_STOP",
  "direct_skills": [
    "mattpocock-improve-codebase-architecture",
    "internal-gateway-critical-master"
  ],
  "report_fingerprint": "sha256:<normalized-completed-report-analysis>",
  "critic_input_fingerprint": "sha256:<same-value>",
  "report_written_before_critique": true,
  "critical_outcome": "route-to-execution-owner",
  "defense": "none",
  "unresolved_material_issue": false,
  "reran_external_report_flow": false,
  "report_returned": true,
  "resume_condition": null,
  "post_report_actions": []
}
```

Hash the normalized completed report analysis before critique. The normalized
value covers `scope`, `evidence`, `candidates`, `top_recommendation`,
`assumptions`, and `evidence_gaps`; serialize it deterministically and hash the
resulting bytes with SHA-256. The critic input fingerprint must match the
completed report fingerprint, and critique must occur after report generation.

Use only the critic's canonical outcomes and Defense values. A non-clear result
must trigger a fresh external report flow or provide a non-empty resume
condition. Only a clear result may return the report, and no candidate
selection, grilling, domain modeling, planning, or implementation action may
occur after the report.

Run the scorer with:

```bash
python3 tests/internal_gateway/codebase_improvement/evaluation/score_gateway_eval.py --manifest tests/internal_gateway/codebase_improvement/evaluation/benchmark.json --run <sanitized-run.json>
```

Exit `0` means accepted, `1` means the structured run was scored and rejected,
and `2` means a file or schema error. Pytest validates scorer behavior and
fixture shape. Only a controlled runtime run supplies behavioral evidence for
the gateway itself.

No diagram is provided because this README records a sanitized evaluation
schema and review sequence rather than a component or data-flow relationship.
