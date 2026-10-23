# Software addendum — BPM

## Additional concepts

- **ReleaseApprovalCase** — A case that approves a software release for a release target.
- **ArchitectureDecisionTask** — A human task that records an architecture decision inside a case.

## Additional relationships

- ArchitectureDecisionTask decidesReleaseApproval ReleaseApprovalCase (many-to-one)

## Additional roles

- **Release Process Owner** — Owns the workflow that approves software releases. Bearer: person. Permissions: Case:read, Case:write, Task:read, Task:write.

## Regulatory notes

- Release approval should preserve the approver, the release identifier, and the decision time.
