# Healthcare

Providers (hospitals, clinics, practices) and payers: patient administration, clinical
workflows, coding and billing, consent management, and strict health-data privacy. Clinical
safety and privacy constraints shape every workflow.

## Terminology

- Patient — the person receiving care; may differ from the guarantor who pays.
- Encounter — a clinical interaction (visit, admission, telehealth session).
- Clinical coding — standardized codes (ICD, SNOMED CT, CPT) for diagnoses and procedures.
- Care plan — the planned set of interventions for a patient condition.
- Payer / Plan — the insurer or scheme funding care; prior authorization gates some services.
- Consent — patient permission for treatment and for data sharing, scoped and revocable.

## Regulatory notes

- Health-data privacy (HIPAA/GDPR) requires role-based access minimization and audit of every
  record access; generated security layers should default to least privilege.
- Consent must be modeled explicitly and checked before data sharing workflows.
- Clinical records are append-only in spirit: corrections are amendments, never silent edits.
- Identity matching (patient master index) must avoid duplicate or merged-in-error records.
