# Banking addendum — ITSM

## Additional concepts
- **CriticalBankingService** — a Service designated as important or critical to customers or financial stability.
- **MajorBankingIncident** — an Incident causing material disruption to a critical banking service.
- **RegulatedChange** — a ChangeRequest requiring enhanced approval, testing, or evidence because it affects a regulated banking service.
- **ResilienceImpactAssessment** — an assessment of customer, regulatory, operational, and recovery impact for an incident or change.

## Additional relationships
- MajorBankingIncident affectsCriticalService CriticalBankingService (many-to-one)
- RegulatedChange changesCriticalService CriticalBankingService (many-to-one)
- ResilienceImpactAssessment assessesIncident MajorBankingIncident (many-to-one)

## Additional roles
- **Bank Service Resilience Manager** — coordinates major incidents, resilience evidence, and regulated changes.

## Regulatory notes
- Critical-service incidents should retain impact, duration, recovery, communications, and decision evidence.
- Changes to critical services should preserve approval, testing, rollback, and segregation-of-duties evidence.
