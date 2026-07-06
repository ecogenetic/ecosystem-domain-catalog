# Healthcare addendum — BPM

## Additional concepts

- **CarePathway** — a clinically approved ProcessDefinition for a condition's care sequence.
- **ClinicalTask** — a Task performed by a clinician, subject to scope-of-practice rules.
- **PatientCase** — a Case tracking one patient's journey through a pathway, with an acuity level.
- **ConsentRecord** — documented patient consent gating clinical tasks and data sharing.

## Additional relationships

- PatientCase follows exactly one CarePathway (1..1).
- ClinicalTasks that require consent must not start until the linked ConsentRecord is granted.
- Escalations route by acuity level (routine, urgent, emergency) with tighter SLAs at higher acuity.

## Additional roles

- **Clinical Governance Lead** — approves care pathways and reviews escalated cases.

## Regulatory notes

- Consent must be modeled and checked before consent-gated tasks; generated flows need an explicit consent gate.
- Patient data in cases is health data: access is role-restricted and every access is auditable.
- Pathway changes require clinical governance approval before activation (versioned pathways).
