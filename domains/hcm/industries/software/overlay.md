# Software addendum — HCM

## Additional concepts

- **EngineerEmployee** — An employee who designs, builds, or operates software.
- **EngineeringPosition** — A position in a product, platform, or architecture team.

## Additional relationships

- EngineerEmployee holdsEngineeringPosition EngineeringPosition (many-to-one)

## Additional roles

- **Engineering Manager** — Manages engineering positions and the employees who hold them. Bearer: person. Permissions: Employee:read, Position:read, Position:write, Appraisal:read.

## Regulatory notes

- Access to production systems should follow the engineering position, not an informal team list.
