# EHR / EMR — Electronic Health Records

An Electronic Health Records system manages patients, appointments, medical records, and
prescriptions so clinicians coordinate care with complete patient context at the point of service.

## Concepts

- **Patient** — a person receiving care whose demographics, history, and visits are recorded.
- **Appointment** — a scheduled encounter between a patient and a clinician at a facility.
- **MedicalRecord** — the longitudinal clinical documentation of a patient's conditions, visits, and results.
- **Prescription** — a clinician's order for medication issued to a patient with dosage instructions.
- **Clinician** — a licensed practitioner who conducts appointments, documents care, and prescribes.
- **Facility** — a physical care location such as a clinic, ward, or practice where appointments occur.

## Taxonomy

- Patient is a kind of Person.
- Clinician is a kind of Person.
- Facility is a kind of Location.
- Prescription is a kind of ClinicalOrder.

## Relationships

- Patient hasAppointment Appointment (one-to-many)
- Appointment withClinician Clinician (many-to-one)
- Appointment atFacility Facility (many-to-one)
- MedicalRecord documentsPatient Patient (one-to-one)
- Prescription issuedByClinician Clinician (many-to-one)
- Prescription prescribedForPatient Patient (many-to-one)

## Attributes

- Patient: fullName (string), dateOfBirth (date), medicalRecordNumber (string)
- Appointment: scheduledAt (dateTime), reason (string), appointmentStatus (string)
- MedicalRecord: createdAt (dateTime), summary (string)
- Prescription: medicationName (string), dosage (string), issuedAt (dateTime)
- Clinician: clinicianName (string), specialty (string), licenseNumber (string)
- Facility: facilityName (string), address (string)

## Lifecycle

- Appointment: scheduled → checked in → completed → follow-up

## Roles

- **ClinicianRole** (bearer: person) — conducts appointments, documents medical records, and issues prescriptions; permissions: Appointment:read, Appointment:write, MedicalRecord:read, MedicalRecord:write, Prescription:read, Prescription:write, Patient:read
- **ReceptionistRole** (bearer: person) — registers patients and schedules appointments at facilities; permissions: Patient:read, Patient:write, Appointment:read, Appointment:write, Facility:read
- **PatientRole** (bearer: person) — attends appointments and views their own records and prescriptions; permissions: Appointment:read, MedicalRecord:read, Prescription:read

## Primary workflow

Register patient → schedule appointment → document visit → prescribe → follow up
