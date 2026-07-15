# Telco addendum — ITSM

## Additional concepts

- **NetworkIncident** — An ITSM incident affecting network or BSS/OSS services.
- **ChangeWindow** — An approved maintenance window for network or BSS changes.
- **ServiceImpactAssessment** — Assessment of customer impact before a change is approved.

## Additional relationships

- NetworkIncident relatesToContext within the ITSM base model (many-to-one).
- ChangeWindow is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **NOC Incident Manager** — Coordinates network incidents and change windows with impact assessment.

## Regulatory notes

- Changes with customer impact require a completed service impact assessment.
- Incident severity for network outages drives regulatory and SLA clocks.
