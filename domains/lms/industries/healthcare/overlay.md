# Healthcare addendum — LMS

## Additional concepts

- **ClinicalCompetencyCourse** — A learning course required for clinical competency or privilege.
- **ComplianceCertificate** — A certificate evidencing completion of mandatory compliance training.
- **PrivilegeLinkedCurriculum** — A curriculum linked to clinical privileges that must stay current.

## Additional relationships

- ClinicalCompetencyCourse relatesToContext within the LMS base model (many-to-one).
- ComplianceCertificate is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Clinical Education Coordinator** — Assigns competency curricula and tracks certificate expiry.

## Regulatory notes

- Expired mandatory certificates may block clinical rostering.
- Training records tied to privilege are auditable health-workforce evidence.
