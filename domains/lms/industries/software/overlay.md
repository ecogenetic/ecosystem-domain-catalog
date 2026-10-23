# Software addendum — LMS

## Additional concepts

- **ProductEnablementCourse** — A course that teaches a software product edition.
- **CertificationEnrollment** — An enrollment that can yield a product certification.

## Additional relationships

- CertificationEnrollment certifiesProductEnablement ProductEnablementCourse (many-to-one)

## Additional roles

- **Enablement Instructor** — Publishes product enablement courses and certifications. Bearer: person. Permissions: Course:read, Course:write, Enrollment:read, Certificate:write.

## Regulatory notes

- A certification should name the product edition the learner was assessed on.
