#!/usr/bin/env bash
# Defective input: form fields without --method GET turn this read into a POST.
gh api /orgs/example-org/audit-log -f phrase='action:repository_ruleset.update' -f per_page=100
