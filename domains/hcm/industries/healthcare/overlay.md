# Healthcare addendum — HCM

## Additional concepts

- **ClinicianCredential** — A verified license or board certification required before clinical rostering.
- **ShiftRoster** — A scheduled set of clinical shifts for a ward or unit.
- **MandatoryTrainingRecord** — Proof of completed compliance or clinical training tied to an employee.

## Additional relationships

- ClinicianCredential relatesToContext within the HCM base model (many-to-one).
- ShiftRoster is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Clinical Workforce Lead** — Approves rosters and verifies credentials before shifts go live.

## Regulatory notes

- Credential verification gates roster activation for clinical roles.
- Workforce records that imply clinical privilege are health data — least privilege and audit apply.
