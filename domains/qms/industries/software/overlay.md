# Software addendum — QMS

## Additional concepts

- **ReleaseInspection** — An inspection performed before a software release is deployed.
- **DefectNonConformance** — A defect found in a release inspection.

## Additional relationships

- ReleaseInspection findsDefectNonConformance DefectNonConformance (one-to-many)

## Additional roles

- **Release Quality Manager** — Accepts release inspections and defect closure. Bearer: person. Permissions: Inspection:read, Inspection:write, NonConformance:read, CAPA:read.

## Regulatory notes

- A release inspection should reference the release identifier and the defects that block deployment.
