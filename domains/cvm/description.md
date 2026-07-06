# CVM — Customer Value Management

A Customer Value Management system segments customers, scores lifetime value and churn risk,
and targets offers and campaigns so marketing and retention teams grow revenue per customer
and reduce churn with measurable uplift.

## Concepts

- **Customer** — a person or organisation whose value and behaviour the business manages.
- **Segment** — a defined group of customers sharing value, behaviour, or risk characteristics.
- **ValueScore** — a computed measure of a customer's current and predicted lifetime value.
- **ChurnRisk** — a computed probability that a customer will lapse or defect.
- **Offer** — an incentive (discount, upgrade, reward) designed to change customer behaviour.
- **Campaign** — a targeted delivery of offers to one or more segments with measured outcomes.

## Taxonomy

- Customer is a kind of Party.
- ValueScore is a kind of Score.
- ChurnRisk is a kind of Score.

## Relationships

- Customer assignedToSegment Segment (many-to-many)
- ValueScore scoresCustomer Customer (many-to-one)
- ChurnRisk assessesCustomer Customer (many-to-one)
- Offer targetedAtSegment Segment (many-to-many)
- Campaign deliversOffer Offer (one-to-many)
- Campaign targetsSegment Segment (many-to-many)

## Attributes

- Customer: externalRef (string), joinedAt (dateTime), consentToMarketing (boolean)
- Segment: segmentName (string), criteria (string)
- ValueScore: scoreValue (decimal), computedAt (dateTime), model (string)
- ChurnRisk: probability (decimal), computedAt (dateTime), band (string)
- Offer: offerName (string), incentiveType (string), validUntil (date)
- Campaign: campaignName (string), campaignStatus (string), upliftMeasured (decimal)

## Lifecycle

- Campaign: draft → targeted → launched → measured → closed

## Roles

- **MarketingAnalystRole** (bearer: person) — builds segments, designs offers, and configures campaigns; permissions: Segment:read, Segment:write, Offer:read, Offer:write, Campaign:read, Campaign:write
- **RetentionManagerRole** (bearer: person) — monitors churn risk and approves retention campaigns; permissions: ChurnRisk:read, ValueScore:read, Campaign:read, Campaign:write

## Primary workflow

Segment customers → score value and churn risk → design offer → launch campaign → measure uplift
