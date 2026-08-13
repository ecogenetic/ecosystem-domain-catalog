# Banking addendum — LMS

## Additional concepts
- **MandatoryComplianceCourse** — a Course required for a banking role or employee population.
- **RoleCertification** — a Certificate demonstrating completion or competence required for a regulated role.
- **TrainingAttestation** — an employee attestation acknowledging a policy, conduct, or compliance obligation.

## Additional relationships
- RoleCertification certifiesLearner Learner (many-to-one)
- TrainingAttestation attestedByLearner Learner (many-to-one)
- MandatoryComplianceCourse requiredForRole RoleReference (many-to-many)

## Additional roles
- **Bank Learning Compliance Role** — manages mandatory curricula, overdue training, certifications, and attestations.

## Regulatory notes
- Mandatory training must preserve assigned date, due date, completion evidence, assessment result, and certificate expiry.
- Regulated-role access may depend on current certification status.
