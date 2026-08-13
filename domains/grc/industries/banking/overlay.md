# Banking addendum — GRC

## Additional concepts
- **RegulatoryObligation** — a requirement imposed by law, regulation, licence, or supervisory rule.
- **ConductRisk** — risk of poor customer or market conduct outcomes.
- **OperationalRisk** — risk from failed processes, people, systems, or external events.
- **ComplianceAttestation** — a periodic attestation against an obligation or control.

## Additional relationships
- RegulatoryObligation obligationMandatesControl Control (one-to-many)
- ComplianceAttestation attestsToObligation RegulatoryObligation (many-to-one)

## Additional roles
- **Bank Compliance Manager** — Owns regulatory obligations, controls, attestations, and remediation. Bearer: person.

## Regulatory notes
- Obligations, policies, controls, evidence, and attestations should preserve effective dates and jurisdiction.
- Compliance decisions should reference the policy or regulatory version applied.
