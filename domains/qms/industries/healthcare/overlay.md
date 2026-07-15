# Healthcare addendum — QMS

## Additional concepts

- **ClinicalCAPA** — A corrective and preventive action raised from a clinical quality event.
- **DocumentedProcedure** — A controlled quality procedure or SOP under document control.
- **AuditFinding** — A finding from an internal or external quality audit.

## Additional relationships

- ClinicalCAPA relatesToContext within the QMS base model (many-to-one).
- DocumentedProcedure is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Quality Assurance Lead** — Owns CAPA closure and controlled document approvals.

## Regulatory notes

- CAPA due dates are compliance commitments — track SLA and escalation.
- Documented procedures require version control; superseded copies must not be used operationally.
