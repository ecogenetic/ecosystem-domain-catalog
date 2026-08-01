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

## Business value chain

1. Register and correctly identify the patient and responsible payer.
2. Capture consent, eligibility, referral and prior-authorisation decisions.
3. Schedule and deliver encounters, observations, diagnoses, procedures and medication.
4. Coordinate care plans, orders, results, discharge and follow-up.
5. Code, bill, adjudicate and reconcile provider and payer transactions.
6. Measure clinical quality, safety, outcomes and population health.

## Cross-domain capability map

| Capability | Typical owning domain |
|---|---|
| Patient relationship and communications | CRM |
| Clinical record and care concepts | HEALTH |
| Medicines and dispensing | MED |
| Scheduling, tasks and clinical workflow | BPM |
| Billing and financial settlement | FIN |
| Consent, documents and master identity | CMS / MDM |
| Quality, risk and compliance | QMS / GRC |

## Modeling rules

- Distinguish patient, practitioner, provider organisation, guarantor and payer.
- Use dated identifiers and provenance-aware patient matching; never silently merge identities.
- Represent corrections as amendments and retain authorship, time and source-system provenance.
- Keep clinical observations separate from diagnoses and decision-support recommendations.
- Apply consent, purpose-of-use and minimum-necessary access to every health-data disclosure.
