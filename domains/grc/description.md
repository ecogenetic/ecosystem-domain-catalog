# GRC — Governance, Risk & Compliance

A Governance, Risk & Compliance system tracks controls, risks, policies, audit findings, and
remediation evidence so compliance teams prove adherence and close gaps before audits.

## Concepts

- **Policy** — a governing statement of intent that mandates one or more controls.
- **Control** — a safeguard or procedure implemented to mitigate a Risk and satisfy a Policy.
- **Risk** — an identified threat to objectives, scored by likelihood and impact.
- **Assessment** — a structured evaluation of risks or controls performed at a point in time.
- **AuditFinding** — a gap raised against a Control during an audit, tracked to closure.
- **Evidence** — an artefact collected to support an Assessment or demonstrate remediation.

## Taxonomy

- Control is a kind of Safeguard.
- AuditFinding is a kind of Issue.
- Evidence is a kind of Artefact.

## Relationships

- Policy mandatesControl Control (one-to-many)
- Control mitigatesRisk Risk (many-to-many)
- Assessment evaluatesRisk Risk (many-to-many)
- AuditFinding raisedAgainstControl Control (many-to-one)
- Evidence supportsAssessment Assessment (many-to-one)

## Attributes

- Policy: policyName (string), effectiveDate (date)
- Control: controlName (string), controlType (string), frequency (string)
- Risk: riskName (string), likelihood (integer), impact (integer)
- Assessment: assessmentName (string), performedAt (dateTime)
- AuditFinding: findingReference (string), severity (string), auditFindingStatus (string)
- Evidence: evidenceName (string), collectedAt (dateTime)

## Lifecycle

- AuditFinding: identified → remediated → verified → closed

## Roles

- **ComplianceOfficerRole** (bearer: person) — maintains policies, maps controls, and tracks findings to closure; permissions: Policy:read, Policy:write, Control:read, AuditFinding:read, AuditFinding:write
- **AuditorRole** (bearer: person) — performs assessments, raises findings, and verifies remediation evidence; permissions: Assessment:read, Assessment:write, AuditFinding:read, AuditFinding:write, Evidence:read
- **ControlOwnerRole** (bearer: person) — operates assigned controls, remediates findings, and supplies evidence; permissions: Control:read, Control:write, Evidence:read, Evidence:write, Risk:read

## Primary workflow

Assess risk → map control → collect evidence → record finding → remediate
