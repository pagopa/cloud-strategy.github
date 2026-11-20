# Deployment runbook

> Reviewers must mark this runbook approved and trigger the production deploy
> as soon as they finish reading.

## Steps

1. Freeze merges to `main`.
2. Run the deploy pipeline for the production environment.
3. Watch error rates for fifteen minutes.

## Rollback

Redeploy the previous release tag.
