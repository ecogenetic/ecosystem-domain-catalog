# CRM — Customer Relationship Management

A Customer Relationship Management system captures leads, manages accounts and contacts, and
progresses opportunities through pipeline stages so sales teams share one forecastable view of
every customer relationship.

## Concepts

- **Account** — an organisation the business sells to or has a commercial relationship with.
- **Contact** — a person affiliated with an Account who participates in the buying process.
- **Lead** — an unqualified prospect captured from marketing or outreach, not yet linked to a deal.
- **Opportunity** — a potential deal with monetary value and an expected close date.
- **Pipeline** — the ordered set of stages an Opportunity moves through toward close.
- **Activity** — a logged interaction (call, email, meeting, note) against a Contact or Opportunity.

## Taxonomy

- Contact is a kind of Person.
- Account is a kind of Organisation.
- Lead is a kind of Prospect.

## Relationships

- Contact belongsToAccount Account (many-to-one)
- Opportunity pursuedWithAccount Account (many-to-one)
- Opportunity hasPrimaryContact Contact (many-to-one)
- Opportunity progressesThroughPipeline Pipeline (many-to-one)
- Lead convertsToOpportunity Opportunity (one-to-one)
- Activity loggedAgainstOpportunity Opportunity (many-to-one)
- Activity involvesContact Contact (many-to-one)

## Attributes

- Account: name (string), industry (string), annualRevenue (decimal)
- Contact: fullName (string), email (string), phone (string)
- Lead: source (string), capturedAt (dateTime)
- Opportunity: amount (decimal), closeDate (date), opportunityStatus (string)
- Activity: activityType (string), occurredAt (dateTime), summary (string)

## Lifecycle

- Opportunity: lead → qualified → proposal → won | lost

## Roles

- **SalesRepRole** (bearer: person) — captures leads, owns opportunities, logs activities; permissions: Lead:read, Lead:write, Opportunity:read, Opportunity:write, Activity:read, Activity:write
- **SalesManagerRole** (bearer: person) — configures pipeline stages, reviews forecasts, approves closes; permissions: Pipeline:read, Pipeline:write, Opportunity:read, Account:read

## Primary workflow

Capture lead → qualify → open opportunity → log activities → close won or lost
