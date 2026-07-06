# BPM — Business Process Management

A Business Process Management system runs process definitions, human tasks, cases, and
SLA-tracked workflows so teams execute repeatable processes with visible bottlenecks and
escalations.

## Concepts

- **ProcessDefinition** — a reusable model of a business process that can be instantiated as running cases.
- **Case** — a single running instance of a ProcessDefinition, tracked from start to close.
- **Task** — a unit of human or automated work assigned within a Case.
- **Form** — a structured data-entry screen presented to complete a Task.
- **Decision** — a gateway that evaluates rules or data to route a Case along a path.
- **SLA** — a service-level agreement that constrains how long a Case or Task may take before escalation.

## Taxonomy

- Task is a kind of WorkItem.
- Decision is a kind of Gateway.
- SLA is a kind of Commitment.

## Relationships

- ProcessDefinition instantiatedAsCase Case (one-to-many)
- Case comprisesTask Task (one-to-many)
- Task presentsForm Form (many-to-one)
- Decision routesCase Case (one-to-many)
- SLA constrainsCase Case (one-to-many)

## Attributes

- ProcessDefinition: processName (string), processVersion (string)
- Case: caseNumber (string), startedAt (dateTime), caseStatus (string)
- Task: taskName (string), assignee (string), dueAt (dateTime)
- Form: formName (string), fieldCount (integer)
- Decision: decisionName (string), ruleExpression (string)
- SLA: slaName (string), targetDuration (string)

## Lifecycle

- Case: started → in progress → decision → closed

## Roles

- **ProcessOwnerRole** (bearer: person) — designs process definitions, monitors case throughput, and tunes SLAs; permissions: ProcessDefinition:read, ProcessDefinition:write, Case:read, SLA:read, SLA:write
- **TaskAssigneeRole** (bearer: person) — claims tasks, completes forms, and progresses cases; permissions: Task:read, Task:write, Form:read, Form:write, Case:read

## Primary workflow

Start case → assign tasks → complete forms → decision gateway → close case
