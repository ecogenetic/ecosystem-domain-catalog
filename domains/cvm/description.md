# CVM — Customer Value Management

A Customer Value Management system is the decision engine a business uses to grow the value of
every customer relationship: it consolidates customer behaviour into value, churn, and propensity
scores; segments the base; matches products and price plans to each segment through eligibility
and pricing rules; selects the next best action per customer; and delivers offers as campaign
treatments across channels — measuring uplift against control groups so every retention, cross-sell,
and pricing decision is evidence-based.

## Concepts

### Customer base and analytics

- **Customer** — a person or organisation whose value and behaviour the business manages.
- **Segment** — a defined group of customers sharing value, behaviour, or risk characteristics.
- **ValueScore** — a computed measure of a customer's current and predicted lifetime value.
- **ChurnRisk** — a computed probability that a customer will lapse or defect.
- **PropensityScore** — a computed likelihood that a customer accepts a specific offer or buys a specific product.
- **CustomerEvent** — a recorded behavioural signal (purchase, usage, complaint, channel visit) that feeds scoring models.
- **PredictiveModel** — a versioned scoring model (value, churn, propensity) whose outputs drive targeting decisions.

### Products and pricing

- **Product** — a product or service in the commercial catalog whose uptake and margin the business manages.
- **PricePlan** — a priced commercial construct (tariff, subscription tier, fee structure) a customer can be on.
- **EligibilityRule** — a rule constraining which customers or segments may receive a product, price plan, or offer.

### Offers and decisioning

- **Offer** — an incentive (discount, upgrade, reward, bundle) designed to change customer behaviour.
- **NextBestAction** — the ranked recommendation of the most valuable treatment for one customer at a point in time.
- **Treatment** — one delivery of an offer to one customer through a channel, with a recorded response.
- **Channel** — a delivery route (SMS, email, app, call center, web) with cost and consent characteristics.

### Campaigns and measurement

- **Campaign** — a targeted delivery of offers to one or more segments with measured outcomes.
- **ControlGroup** — a held-out subset of a campaign's target audience used to measure true uplift.

## Taxonomy

- Customer is a kind of Party.
- ValueScore is a kind of Score.
- ChurnRisk is a kind of Score.
- PropensityScore is a kind of Score.
- NextBestAction is a kind of Recommendation.
- Treatment is a kind of CustomerInteraction.
- ControlGroup is a kind of AudienceSubset.

## Relationships

- Customer assignedToSegment Segment (many-to-many)
- Customer subscribedToPricePlan PricePlan (many-to-one)
- CustomerEvent recordedForCustomer Customer (many-to-one)
- ValueScore scoresCustomer Customer (many-to-one)
- ChurnRisk assessesCustomer Customer (many-to-one)
- PropensityScore estimatesCustomer Customer (many-to-one)
- PropensityScore estimatesForProduct Product (many-to-one)
- ValueScore producedByModel PredictiveModel (many-to-one)
- ChurnRisk computedByModel PredictiveModel (many-to-one)
- PropensityScore generatedByModel PredictiveModel (many-to-one)
- PricePlan pricesProduct Product (many-to-many)
- EligibilityRule restrictsOffer Offer (many-to-one)
- EligibilityRule appliesToSegment Segment (many-to-many)
- Offer targetedAtSegment Segment (many-to-many)
- Offer promotesProduct Product (many-to-many)
- NextBestAction recommendsOffer Offer (many-to-one)
- NextBestAction recommendedForCustomer Customer (many-to-one)
- Treatment deliversOfferToCustomer Customer (many-to-one)
- Treatment executesOffer Offer (many-to-one)
- Treatment deliveredViaChannel Channel (many-to-one)
- Treatment partOfCampaign Campaign (many-to-one)
- Campaign deliversOffer Offer (one-to-many)
- Campaign targetsSegment Segment (many-to-many)
- Campaign heldOutControlGroup ControlGroup (one-to-one)

## Attributes

- Customer: externalRef (string), joinedAt (dateTime), consentToMarketing (boolean), tenureMonths (integer), currentMonthlySpend (decimal)
- Segment: segmentName (string), criteria (string), memberCount (integer)
- ValueScore: scoreValue (decimal), computedAt (dateTime), model (string)
- ChurnRisk: probability (decimal), computedAt (dateTime), band (string)
- PropensityScore: propensityValue (decimal), scoredAt (dateTime), targetAction (string)
- CustomerEvent: eventType (string), eventAt (dateTime), eventValue (decimal)
- PredictiveModel: modelName (string), modelVersion (string), modelType (string), trainedAt (dateTime), accuracy (decimal)
- Product: productCode (string), productName (string), marginPercent (decimal)
- PricePlan: planName (string), monthlyFee (decimal), contractMonths (integer), planStatus (string)
- EligibilityRule: ruleName (string), ruleExpression (string), rulePriority (integer)
- Offer: offerName (string), incentiveType (string), validUntil (date), offerCost (decimal), expectedUplift (decimal)
- NextBestAction: rank (integer), expectedValue (decimal), decidedAt (dateTime), decisionReason (string)
- Treatment: deliveredAt (dateTime), responseStatus (string), respondedAt (dateTime)
- Channel: channelName (string), channelType (string), costPerContact (decimal)
- Campaign: campaignName (string), campaignStatus (string), upliftMeasured (decimal), campaignBudget (decimal)
- ControlGroup: holdoutPercent (decimal), controlSize (integer)

## Lifecycle

- Campaign: draft → targeted → launched → measured → closed
- Offer: designed → approved → active → expired | withdrawn
- Treatment: selected → delivered → responded | no_response | suppressed
- PredictiveModel: training → validated → deployed → retired
- PricePlan: draft → active → grandfathered → retired

## Roles

- **MarketingAnalystRole** (bearer: person) — builds segments, designs offers, and configures campaigns with control groups; permissions: Segment:read, Segment:write, Offer:read, Offer:write, Campaign:read, Campaign:write, ControlGroup:read, ControlGroup:write, Customer:read
- **RetentionManagerRole** (bearer: person) — monitors churn risk and value trends, approves retention offers and campaigns; permissions: ChurnRisk:read, ValueScore:read, NextBestAction:read, Campaign:read, Campaign:write, Offer:read, Customer:read
- **PricingManagerRole** (bearer: person) — owns the product and price-plan catalog, sets eligibility rules, and approves offer economics; permissions: Product:read, Product:write, PricePlan:read, PricePlan:write, EligibilityRule:read, EligibilityRule:write, Offer:read
- **DataScientistRole** (bearer: person) — builds, validates, and deploys the scoring models behind value, churn, and propensity; permissions: PredictiveModel:read, PredictiveModel:write, ValueScore:read, ChurnRisk:read, PropensityScore:read, CustomerEvent:read
- **CampaignOperatorRole** (bearer: person) — executes launched campaigns across channels and monitors treatment delivery; permissions: Campaign:read, Treatment:read, Treatment:write, Channel:read, Offer:read, Customer:read

## Primary workflow

Ingest customer events → score value, churn, and propensity → segment the base → match products, price plans, and eligibility → decide next best action → deliver treatments via channels → measure uplift against control group

Supporting workflows:

- Pricing: design price plan → check eligibility rules → approve economics → activate → grandfather or retire
- Model management: train model → validate accuracy → deploy → monitor drift → retire
- Retention: detect rising churn risk → rank save offers by expected value → deliver treatment → track response
