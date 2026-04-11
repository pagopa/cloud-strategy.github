# AWS Governance Guardrail Map

Use this reference when the user needs a clearer split between AWS governance surfaces.

## Quick split

| Need | Use first | Why |
| --- | --- | --- |
| Limit what principals can ever do across many accounts | SCP | Org-level preventive guardrail |
| Define what a role or workload can do in one account | IAM policy plus trust policy | Execution-level authorization |
| Constrain delegated builders or automation | Permission boundary or session policy | Limits delegated execution |
| Standardize metadata expectations | Tag policy plus local enforcement | Governance consistency |
| Permit emergency access | Break-glass role design plus audit path | Exceptional access with visibility |

## Review questions

1. Is this question about where a control lives or what a principal may do?
2. Is the mechanism preventing permission, granting permission, or constraining delegated permission?
3. Is the scope root, OU, account set, or single account?
4. What exception path is required, if any?
5. What should be simulated before rollout?

## Reminder

- Structure chooses placement.
- Governance chooses permissions and guardrails.
- Operations verifies that the chosen governance behaves as intended after rollout.
