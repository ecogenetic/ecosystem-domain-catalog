# Insurance addendum — GRC

## Additional concepts

- **SolvencyRisk** — capital adequacy risk against regulatory solvency requirements; specializes Risk.
- **ConductRisk** — risk of unfair customer outcomes in product, sales, or claims; specializes Risk.
- **RegulatoryReturn** — periodic supervisory filing with a due date and sign-off chain.
- **ActuarialSignOff** — the appointed actuary's formal approval of reserves and solvency figures.

## Additional relationships

- RegulatoryReturn covers an Assessment period (1..1) and requires an ActuarialSignOff before filing.
- Controls map to SolvencyRisk and ConductRisk categories for coverage reporting.

## Additional roles

- **Appointed Actuary** — signs off reserves and solvency in returns; read access to risks and assessments.

## Regulatory notes

- Returns must not be filed without actuarial sign-off; generated workflows must gate filing on sign-off.
- Conduct-risk findings require customer-remediation tracking with evidence.
- Solvency positions are recalculated on material risk events, not only at period end.
