# Banking addendum — HCM

## Additional concepts
- **RegulatedPosition** — a Position subject to fit-and-proper, licensing, or conduct requirements.
- **DelegatedAuthority** — a dated authority allowing an employee to approve banking actions up to stated limits.
- **SegregationOfDutiesRule** — a control preventing incompatible responsibilities from being assigned to the same employee.
- **FitAndProperAssessment** — an assessment recording whether an employee satisfies regulated-role requirements.

## Additional relationships
- DelegatedAuthority grantedToEmployee Employee (many-to-one)
- DelegatedAuthority appliesToPosition Position (many-to-one)
- FitAndProperAssessment evaluatesRegulatedPosition RegulatedPosition (many-to-one)

## Additional roles
- **Bank HR Compliance Role** — manages regulated positions, delegated authorities, and fit-and-proper evidence.

## Regulatory notes
- Delegated authorities must be effective-dated, reviewable, and revocable.
- Segregation-of-duties conflicts should be detectable before incompatible assignments become active.
