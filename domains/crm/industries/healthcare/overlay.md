# Healthcare addendum — CRM

In healthcare, CRM is patient relationship management: managing referrals into the organisation,
scheduling and confirming appointments, running consent-gated outreach programmes (screening
reminders, chronic-care follow-up), and resolving patient inquiries — under strict health-data
privacy and explicit, revocable consent.

## Additional concepts

- **Patient** — a Person receiving or seeking care, identified by a medical record number (MRN); may differ from the guarantor who pays.
- **ProviderOrganization** — an Organisation representing a practice, clinic, hospital, or referring organisation.
- **PatientRelationship** — a CustomerRelationship connecting the patient to the care organisation without duplicating clinical records.
- **Referral** — a Lead-like intake: a request from a referring provider (or self-referral) for a patient to receive a service, qualified and scheduled like a lead is converted.
- **Appointment** — an Activity that books a patient with a provider at a time; confirmations, reminders, and no-show follow-up are core CRM work.
- **ConsentRecord** — a healthcare specialisation of the base CRM consent record representing the patient's explicit, scoped, revocable permission for communication and data sharing; every outreach checks it.
- **OutreachProgram** — a Campaign specialised for care outreach (screening reminders, vaccination drives, chronic-care follow-up) rather than selling.

## Additional relationships

- PatientRelationship relatesToPatient Patient (many-to-one) and registeredWithProvider ProviderOrganization (many-to-one); the patient's home practice anchors the relationship.
- Referral refersPatient Patient (many-to-one) and referredByProvider ProviderOrganization (many-to-one); referral-to-appointment conversion time is the key intake metric.
- Appointment bookedForPatient Patient (many-to-one); reminders and confirmations are Activities against the appointment's patient.
- ConsentRecord consentGivenByPatient Patient (many-to-one); outreach programmes must check scope (marketing vs care communication) before contact.
- OutreachProgram enrollsPatient Patient (many-to-many); enrollment respects consent scope and can be revoked at any time.
- Patient inquiries and complaints follow the base Case flow with slaDueAt for statutory or contractual response times.

## Additional roles

- **PatientAccessCoordinatorRole** (bearer: person) — manages referral intake, verifies coverage, and schedules appointments; permissions: Referral:read, Referral:write, Appointment:read, Appointment:write, Patient:read, Patient:write, ProviderOrganization:read
- **OutreachCoordinatorRole** (bearer: person) — runs consent-gated outreach programmes and follow-up activities; permissions: OutreachProgram:read, OutreachProgram:write, ConsentRecord:read, Patient:read, Activity:read, Activity:write

## Regulatory notes

- Health-data privacy (HIPAA/GDPR) demands least-privilege access and an audit of every patient-record access; CRM views expose demographics and relationship data, never clinical detail beyond what the role requires.
- Consent is scoped and revocable: care communications (appointment reminders) and marketing outreach (wellness programmes) require different consent scopes — check the ConsentRecord scope before every contact.
- Patient identity matching must avoid duplicate records; merges are audited, never silent.
- Referral handling often carries contractual or statutory turnaround times — track them with slaDueAt on the intake workflow.
