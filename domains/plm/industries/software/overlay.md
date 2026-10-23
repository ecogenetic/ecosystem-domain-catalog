# Software addendum — PLM

## Additional concepts

- **SoftwareRevision** — A revision of a software product definition.
- **ReleaseEngineeringChange** — An engineering change that prepares a software revision for release.

## Additional relationships

- ReleaseEngineeringChange revisesSoftwareRevision SoftwareRevision (many-to-one)

## Additional roles

- **Software Change Approver** — Approves engineering changes to a software revision. Bearer: person. Permissions: EngineeringChange:read, EngineeringChange:write, Revision:read, Revision:write.

## Regulatory notes

- An approved software revision should identify the product edition it will be released as.
