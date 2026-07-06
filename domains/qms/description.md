# QMS — Quality Management System

A Quality Management System manages inspections, non-conformances, CAPA, and product
specifications so quality teams contain defects at the point of detection and prevent
recurrence through verified corrective action.

## Concepts

- **Inspection** — a scheduled or triggered examination of product or process against specifications.
- **NonConformance** — a documented deviation from a specification found during inspection.
- **CAPA** — a corrective and preventive action plan that remediates a non-conformance and prevents recurrence.
- **Specification** — a controlled definition of acceptable characteristics and tolerance limits for a product or process.
- **Sample** — a unit or portion of product drawn during an inspection for measurement against a specification.
- **Certificate** — a formal document attesting that an inspection was passed and requirements were met.

## Taxonomy

- Inspection is a kind of QualityEvent.
- NonConformance is a kind of Deviation.
- CAPA is a kind of ActionPlan.

## Relationships

- Inspection drawsSample Sample (one-to-many)
- Sample checkedAgainstSpecification Specification (many-to-one)
- NonConformance raisedFromInspection Inspection (many-to-one)
- CAPA remediatesNonConformance NonConformance (one-to-one)
- Certificate attestsInspection Inspection (one-to-one)

## Attributes

- Inspection: inspectionType (string), inspectedAt (dateTime)
- NonConformance: severity (string), defectDescription (string), nonConformanceStatus (string)
- CAPA: actionPlan (string), targetDate (date)
- Specification: specificationName (string), toleranceLimit (decimal)
- Sample: sampleCode (string), collectedAt (dateTime)
- Certificate: certificateNumber (string), issuedAt (dateTime)

## Lifecycle

- NonConformance: recorded → capa initiated → verified → closed

## Roles

- **QualityInspectorRole** (bearer: person) — performs inspections, draws samples, raises non-conformances; permissions: Inspection:read, Inspection:write, Sample:read, Sample:write, NonConformance:read, NonConformance:write
- **QualityManagerRole** (bearer: person) — approves specifications, initiates CAPA, verifies effectiveness, issues certificates; permissions: Specification:read, Specification:write, CAPA:read, CAPA:write, Certificate:read, Certificate:write

## Primary workflow

Schedule inspection → record sample → raise non-conformance → initiate CAPA → verify effectiveness
