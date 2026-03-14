# Cloud Auth Snippets for GitHub Actions

## AWS — OIDC Federation
```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@<FULL_SHA>
    with:
      role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
      aws-region: eu-south-1
```

Prerequisites:
- IAM OIDC provider for `token.actions.githubusercontent.com`
- IAM role with trust policy scoped to repo/branch
- No long-lived access keys

## Azure — OIDC Federation
```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: azure/login@<FULL_SHA>
    with:
      client-id: ${{ secrets.AZURE_CLIENT_ID }}
      tenant-id: ${{ secrets.AZURE_TENANT_ID }}
      subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

Prerequisites:
- App registration with federated credential for GitHub Actions
- Service principal with minimal RBAC role
- No client secrets

## GCP — Workload Identity Federation
```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: google-github-actions/auth@<FULL_SHA>
    with:
      workload_identity_provider: ${{ secrets.GCP_WIF_PROVIDER }}
      service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}
```

Prerequisites:
- Workload Identity Pool with GitHub provider
- Service account with minimal IAM roles
- No service account keys
