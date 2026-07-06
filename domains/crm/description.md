# CRM — Customer Relationship Management

A Customer Relationship Management system manages the full customer-facing lifecycle: marketing
campaigns generate leads, sales teams qualify them into opportunities and progress deals through
pipeline stages with quotes and negotiated contracts, and service teams resolve post-sale cases —
so the whole business shares one forecastable, auditable view of every customer relationship
from first touch to renewal.

## Concepts

### Customer master

- **Account** — an organisation the business sells to or has a commercial relationship with.
- **Contact** — a person affiliated with an Account who participates in the buying process.
- **Territory** — a named market segment (geography, industry, or size band) that accounts are assigned to for coverage and quota purposes.

### Marketing and lead management

- **Campaign** — a planned marketing initiative (event, email, ads, webinar) with a budget that generates and influences leads.
- **Lead** — an unqualified prospect captured from marketing or outreach, not yet linked to a deal.

### Sales execution

- **Opportunity** — a potential deal with monetary value, a probability, and an expected close date.
- **Pipeline** — the ordered set of stages an Opportunity moves through toward close.
- **Product** — a sellable product or service in the catalog that opportunities and quotes reference.
- **Quote** — a priced, time-limited proposal presented to the customer for an opportunity.
- **QuoteLine** — a single product line on a quote with quantity, unit price, and discount.
- **Contract** — the negotiated agreement that governs a won deal, with value, term, and renewal dates.
- **Forecast** — a periodic projection of expected revenue for a territory, built from weighted open opportunities.

### Engagement and service

- **Activity** — a logged interaction (call, email, meeting, note) against a Contact, Opportunity, or Case.
- **Case** — a post-sale service request or complaint raised by a contact, tracked to resolution.

## Taxonomy

- Contact is a kind of Person.
- Account is a kind of Organisation.
- Lead is a kind of Prospect.
- Quote is a kind of CommercialDocument.
- Contract is a kind of CommercialDocument.
- Case is a kind of ServiceRequest.
- Campaign is a kind of MarketingInitiative.

## Relationships

- Contact belongsToAccount Account (many-to-one)
- Account assignedToTerritory Territory (many-to-one)
- Campaign generatesLead Lead (one-to-many)
- Lead convertsToOpportunity Opportunity (one-to-one)
- Opportunity pursuedWithAccount Account (many-to-one)
- Opportunity hasPrimaryContact Contact (many-to-one)
- Opportunity progressesThroughPipeline Pipeline (many-to-one)
- Opportunity influencedByCampaign Campaign (many-to-one)
- Opportunity includesProduct Product (many-to-many)
- Quote quotesOpportunity Opportunity (many-to-one)
- QuoteLine partOfQuote Quote (many-to-one)
- QuoteLine forQuotedProduct Product (many-to-one)
- Contract resultsFromOpportunity Opportunity (one-to-one)
- Contract governsAccount Account (many-to-one)
- Case raisedByContact Contact (many-to-one)
- Case filedAgainstAccount Account (many-to-one)
- Case aboutProduct Product (many-to-one)
- Activity loggedAgainstOpportunity Opportunity (many-to-one)
- Activity loggedAgainstCase Case (many-to-one)
- Activity involvesContact Contact (many-to-one)
- Forecast coversTerritory Territory (many-to-one)

## Attributes

- Account: accountName (string), industry (string), annualRevenue (decimal), website (string), accountType (string), employeeCount (integer)
- Contact: fullName (string), email (string), phone (string), jobTitle (string), department (string)
- Territory: territoryName (string), region (string)
- Campaign: campaignName (string), campaignType (string), campaignStartDate (date), campaignEndDate (date), budgetedCost (decimal), campaignStatus (string)
- Lead: leadSource (string), capturedAt (dateTime), company (string), leadScore (integer), leadStatus (string)
- Opportunity: opportunityName (string), amount (decimal), probability (decimal), closeDate (date), opportunityStatus (string)
- Pipeline: pipelineName (string), stageCount (integer)
- Product: productCode (string), productName (string), listPrice (decimal)
- Quote: quoteNumber (string), quoteDate (date), validUntil (date), quoteTotal (decimal), quoteStatus (string)
- QuoteLine: quotedQuantity (decimal), quotedUnitPrice (decimal), discountPercent (decimal)
- Contract: contractNumber (string), contractStart (date), contractEnd (date), contractValue (decimal), contractStatus (string)
- Forecast: forecastPeriod (string), forecastAmount (decimal), commitAmount (decimal), bestCaseAmount (decimal)
- Activity: activityType (string), occurredAt (dateTime), summary (string)
- Case: caseNumber (string), subject (string), priority (string), openedAt (dateTime), resolvedAt (dateTime), caseStatus (string)

## Lifecycle

- Lead: new → contacted → qualified → converted | disqualified
- Opportunity: lead → qualified → proposal → won | lost
- Quote: draft → presented → accepted | rejected | expired
- Contract: draft → active → expired | terminated
- Case: new → in_progress → waiting_on_customer → resolved → closed
- Campaign: planned → active → completed

## Roles

- **SalesRepRole** (bearer: person) — captures leads, owns opportunities, builds quotes, logs activities; permissions: Lead:read, Lead:write, Opportunity:read, Opportunity:write, Quote:read, Quote:write, Activity:read, Activity:write, Account:read, Contact:read, Product:read
- **SalesManagerRole** (bearer: person) — configures pipelines and territories, reviews forecasts, approves discounts and closes; permissions: Pipeline:read, Pipeline:write, Territory:read, Territory:write, Forecast:read, Forecast:write, Opportunity:read, Quote:read, Account:read
- **MarketingSpecialistRole** (bearer: person) — plans campaigns, manages budgets, and routes generated leads to sales; permissions: Campaign:read, Campaign:write, Lead:read, Lead:write, Account:read, Contact:read
- **ServiceAgentRole** (bearer: person) — owns cases from intake to resolution and logs customer interactions; permissions: Case:read, Case:write, Activity:read, Activity:write, Account:read, Contact:read, Product:read
- **ContractAdminRole** (bearer: person) — drafts and administers contracts for won deals and tracks renewals; permissions: Contract:read, Contract:write, Opportunity:read, Account:read

## Primary workflow

Run campaign → capture lead → qualify → open opportunity → quote products → negotiate → close won → sign contract

Supporting workflows:

- Service: raise case → assign agent → log interactions → resolve → close
- Forecasting: weight open opportunities by probability → roll up per territory → commit forecast
- Renewal: track contract end dates → open renewal opportunity → re-quote → extend or terminate
