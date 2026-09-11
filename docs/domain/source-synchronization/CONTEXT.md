# Source Synchronization

This context defines the repository's terms for moving source-managed assets into consumer repositories and supported home runtimes while preserving target ownership.

## Synchronization vocabulary

**Consumer repository**:
A target repository that receives source-managed baseline assets while retaining its local ownership layer.
_Avoid_: Downstream source

**Home runtime**:
A local agent runtime that receives a projection of eligible repository-owned assets.
_Avoid_: Second source repository

**Sync plan**:
The proposed set of create, update, delete, preserve, link, or block operations for one synchronization boundary.
_Avoid_: Immediate apply

**Managed resource**:
A target asset whose source path, identity, and synchronization state are recorded by the synchronization contract.
_Avoid_: Any matching file

**Preservation set**:
The target-owned files and directories that synchronization must leave unchanged.
_Avoid_: Unmanaged drift

**Create-once seed**:
A source template materialized only when the target lacks the corresponding local file.
_Avoid_: Overwrite template

**Canonical link**:
A supported runtime projection that points directly to the source-owned bundle.
_Avoid_: Copied source
