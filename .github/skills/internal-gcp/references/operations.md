# GCP Operations

Audit, inventory, posture, monitoring, backup and recovery, and stage-aware
rollout evidence for Google Cloud. Rows with a source were verified on
2026-09-27; recheck them when they drive a decision.

## Evidence discipline

- Separate expected evidence (defined before the change) from observed
  evidence (recorded after it).
- Name the owner, rollback trigger, and widening condition before the first
  unit changes.
- Report missing or unobservable evidence as a gap, not as a pass.

## Audit logs

| Log | Default | Operational rule |
| --- | --- | --- |
| Admin Activity | Always on; cannot be disabled | Primary evidence for IAM, Org Policy, and configuration changes |
| Data Access | Off by default except some BigQuery logs; BigQuery Data Access logs cannot be disabled ([Data Access](https://docs.cloud.google.com/logging/docs/audit/configure-data-access)) | Enable per service or `allServices` at organization or folder; child scopes cannot disable what a parent enabled |
| Policy (Org Policy and VPC-SC) | Written on violations | Dry-run results carry `dryRunResult` or `metadata.dryRun`; use them as the first rollout stage |

Rules:

- `roles/editor` cannot read Data Access logs; use `roles/logging.privateLogViewer`.
- Data Access logs can be large; state the cost impact when enabling them.
- Use `iam.disableAuditLoggingExemption` to stop new audit exemptions.
- Route organization or folder logs through aggregated sinks with
  `--include-children` to a central project, and grant the sink writer
  identity on the destination.

## Inventory and drift

- Cloud Asset Inventory search and export show projects, IAM bindings,
  and control surfaces at a point in time.
- Asset feeds to Pub/Sub detect changes, including PAM grants
  (`privilegedaccessmanager.googleapis.com/Grant`).
- Compare inventory before and after each rollout unit.

## Posture

- Security Command Center findings are rollout evidence for misconfiguration
  and threat signals on the affected scope.
- Some PAM features (multi-level approval, scope customization) require the
  Security Command Center Enterprise or Premium tier.

## Monitoring

- Alert on the signals that the affected surface depends on: error rates,
  denied requests, connectivity, and job failures.
- Confirm alerting still fires after the change, not only before.

## Backup and recovery

| Need | Evidence |
| --- | --- |
| Backup posture exists | Protected-resource inventory, backup plan attachment, recent successful backups |
| Backups resist tampering | Backup vault with enforced minimum retention (immutable and indelible) ([Backup and DR](https://docs.cloud.google.com/backup-disaster-recovery/docs/concepts/backup-dr)) |
| Restore is viable | Restore exercise, observed recovery time and recovery point, integrity check after restore |
| Recovery is credible | Recovery workflow exercised for the scoped critical service |

Backup and DR covers Compute Engine, Persistent Disk, Filestore, Cloud SQL,
AlloyDB, self-managed databases on VMs, and Bare Metal Solution. Verify the
support matrix and vault location compatibility for the target workload.

## Stage-aware rollout evidence

| Stage | Evidence before widening |
| --- | --- |
| Dry-run (Org Policy or VPC-SC) | Dry-run violations reviewed; each is fixed or covered by an exception |
| First folder or project set | Inheritance behaves as expected, monitoring stays present, rollback owner confirmed |
| First Shared VPC or central-service slice | Connectivity, audit logs, and ownership paths behave as intended |
| Broad project or region expansion | Prior-wave observations recorded, regressions investigated, escalation path confirmed |

## Surface signals

| Surface | Signals | What they confirm |
| --- | --- | --- |
| IAM or Org Policy rollout | Intended actions succeed, denied actions are visible, audit records exist | Controls permit intended work and expose regressions |
| Shared VPC or topology change | Connectivity and logging work for scoped projects | The change preserves shared networking behavior |
| Inventory and reporting | Intended projects, identities, and controls remain visible | Rollout state is tracked and drift is detectable |
