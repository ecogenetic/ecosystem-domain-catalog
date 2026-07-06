# LMS — Learning Management System

A Learning Management System publishes courses, manages enrollments, delivers lessons, and
issues certificates so learners progress through structured training with measurable outcomes.

## Concepts

- **Course** — a structured program of lessons and assessments published for learners to take.
- **Enrollment** — a learner's registration in a course, tracking progress from start to certification.
- **Lesson** — a single unit of instructional content delivered in sequence within a course.
- **Assessment** — a quiz or exam that evaluates whether an enrollment has met the learning objectives.
- **Certificate** — a credential issued when an enrollment completes the course and passes assessment.
- **Learner** — a person who enrolls in courses to complete training.

## Taxonomy

- Learner is a kind of Person.
- Lesson is a kind of LearningUnit.
- Assessment is a kind of Evaluation.

## Relationships

- Course composedOfLesson Lesson (one-to-many)
- Enrollment joinsLearnerToCourse Course (many-to-one)
- Enrollment forLearner Learner (many-to-one)
- Assessment evaluatesEnrollment Enrollment (one-to-many)
- Certificate awardedForEnrollment Enrollment (one-to-one)

## Attributes

- Course: courseTitle (string), durationHours (decimal)
- Enrollment: enrolledAt (dateTime), progressPercent (decimal), enrollmentStatus (string)
- Lesson: lessonTitle (string), sequenceNumber (integer)
- Assessment: assessmentType (string), passingScore (decimal)
- Certificate: certificateNumber (string), issuedAt (dateTime)
- Learner: fullName (string), email (string)

## Lifecycle

- Enrollment: enrolled → in progress → completed → certified

## Roles

- **LearnerRole** (bearer: person) — enrolls in courses, completes lessons, takes assessments, receives certificates; permissions: Course:read, Lesson:read, Enrollment:read, Assessment:read, Certificate:read
- **InstructorRole** (bearer: person) — publishes courses, authors lessons and assessments, monitors enrollments, issues certificates; permissions: Course:read, Course:write, Lesson:read, Lesson:write, Assessment:read, Assessment:write, Enrollment:read, Certificate:write

## Primary workflow

Publish course → enroll learner → complete lessons → pass assessment → issue certificate
