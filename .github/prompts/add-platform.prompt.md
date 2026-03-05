---
agent: agent
description: Add a new platform to cost tracking
---

# Add New Platform

## Context

This prompt helps you add a new platform for cost tracking in the Azure REL system.

## Input Required

- **Platform Name**: ${input:platformName}
- **WBS Code**: ${input:wbsCode}
- **Subscriptions**: ${input:subscriptions}

## Instructions

1. Navigate to `azure/_source_of_truth/`
2. Add the platform to the mapping configuration
3. Update anomaly detection recipients if needed

## Configuration Changes

### Platform Mapping

Add to platform configuration:

```json
{
  "${input:platformName}": {
    "subscriptions": [${input:subscriptions}],
    "wbs": "${input:wbsCode}"
  }
}
```

### Anomaly Recipients (Optional)

If alerts are needed:

```json
{
  "platform": "${input:platformName}",
  "emails": ["team@pagopa.it"]
}
```

## Validations

- [ ] Platform name is unique
- [ ] WBS code is valid
- [ ] Subscriptions exist
- [ ] Configuration files are valid JSON

## References

Follow the conventions in `#file:.github/copilot-instructions.md`
