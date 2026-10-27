# GitHub Actions migration

## Goal

Move the release pipeline from the legacy CI server to GitHub Actions.

## Plan

1. Recreate the release job as `release.yml`.
2. Run both pipelines in parallel for two releases.
3. Retire the legacy job after two clean parallel releases.

## Owners

The platform team owns the migration and the rollback decision.
