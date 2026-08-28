# CRM — Customer Relationship Management

A Customer Relationship Management system manages the full customer-facing lifecycle: it identifies
people and organisations as parties, maintains their customer relationships, captures campaign and
outreach responses as leads, converts qualified demand into opportunities, progresses deals through
pipeline stages and quotes, and hands won business to contracts and fulfilment. Service teams then
resolve post-sale cases while every assignment, interaction, consent decision, and stage transition
remains auditable.

## Concepts

### Party and relationship management

- **Party** — a person or organisation that participates in a prospect, customer, partner, or other business relationship.
- **Person** — an individual party who may be a customer, prospect, contact, or representative.
- **Organisation** — an organisational party such as a company, public body, partnership, or non-profit.
- **Account** — an organisation the business sells to or maintains a commercial relationship with; retained as the familiar B2B CRM term.
- **Contact** — a person who participates in a customer relationship, optionally representing an Account.
- **CustomerRelationship** — the managed CRM relationship between the enterprise and a customer party, including owner, status, start date, and lifecycle.
- **Territory** — a named market segment such as geography, industry, or size band used for coverage and quota management.
- **Assignment** — a dated allocation of a lead, relationship, opportunity, activity, or case to a responsible user or team.
- **ConsentRecord** — auditable permission or refusal for a party to be contacted for a stated purpose through a channel.

### Marketing and lead management

- **Campaign** — a planned marketing initiative with a budget, audience, and measurable responses.
- **CampaignMember** — one party's participation in a campaign, including targeting, delivery, response, and suppression status.
- **Lead** — an unqualified demand or prospect record captured from marketing, referral, or outbound activity.
- **LeadConversion** — the auditable event that qualifies a Lead and links or creates its Party, CustomerRelationship, and Opportunity.

### Sales execution

- **Opportunity** — a potential deal with monetary value, probability, owner, expected close date, and current pipeline stage.
- **Pipeline** — the ordered set of stages through which an Opportunity progresses.
- **PipelineStage** — one named, ordered stage within a Pipeline.
- **StageTransition** — the history record of an Opportunity moving from one stage to another.
- **Product** — a sellable product or service referenced by opportunities and quotes.
- **OpportunityLine** — one Product included in an Opportunity with quantity, expected price, revenue, and term.
- **Quote** — a priced, time-limited proposal presented for an Opportunity.
- **QuoteLine** — a Product line on a Quote with quantity, unit price, and discount.
- **Contract** — the negotiated agreement governing a won deal, including value, term, and renewal dates.
- **Forecast** — a periodic projection of expected revenue for a Territory based on weighted open opportunities.

### Engagement and service

- **Activity** — a logged customer interaction such as a call, email, meeting, task, or note.
- **Case** — a post-sale request, complaint, or service matter tracked through resolution.

## Taxonomy

- Person is a kind of Party.
- Organisation is a kind of Party.
- Account is a kind of Organisation.
- Contact is a kind of Person.
- Lead is a kind of ProspectRecord.
- CustomerRelationship is a kind of BusinessRelationship.
- CampaignMember is a kind of CampaignParticipation.
- OpportunityLine is a kind of CommercialLine.
- Quote is a kind of CommercialDocument.
- Contract is a kind of CommercialDocument.
- Case is a kind of ServiceRequest.
- ConsentRecord is a kind of PermissionRecord.

## Relationships

- Contact belongsToAccount Account (many-to-one)
- CustomerRelationship relatesToParty Party (many-to-one)
- CustomerRelationship assignedToTerritory Territory (many-to-one)
- Assignment assignsParty Party (many-to-one)
- Assignment assignsOpportunity Opportunity (many-to-one)
- Assignment assignsCase Case (many-to-one)
- ConsentRecord recordsConsentFor Party (many-to-one)
- Campaign hasCampaignMember CampaignMember (one-to-many)
- CampaignMember memberOfCampaign Campaign (many-to-one)
- CampaignMember representsParty Party (many-to-one)
- CampaignMember sourcedLead Lead (one-to-one)
- Campaign generatesLead Lead (one-to-many)
- LeadConversion convertsLead Lead (one-to-one)
- LeadConversion resolvesToParty Party (many-to-one)
- LeadConversion createsRelationship CustomerRelationship (one-to-one)
- LeadConversion createsOpportunity Opportunity (one-to-one)
- Opportunity pursuedForRelationship CustomerRelationship (many-to-one)
- Opportunity hasPrimaryContact Contact (many-to-one)
- Opportunity progressesThroughPipeline Pipeline (many-to-one)
- Opportunity atPipelineStage PipelineStage (many-to-one)
- PipelineStage partOfPipeline Pipeline (many-to-one)
- StageTransition recordsOpportunity Opportunity (many-to-one)
- StageTransition fromPipelineStage PipelineStage (many-to-one)
- StageTransition toPipelineStage PipelineStage (many-to-one)
- Opportunity influencedByCampaign Campaign (many-to-many)
- Opportunity hasOpportunityLine OpportunityLine (one-to-many)
- OpportunityLine partOfOpportunity Opportunity (many-to-one)
- OpportunityLine forOpportunityProduct Product (many-to-one)
- Quote quotesOpportunity Opportunity (many-to-one)
- QuoteLine partOfQuote Quote (many-to-one)
- QuoteLine forQuotedProduct Product (many-to-one)
- Contract resultsFromOpportunity Opportunity (one-to-one)
- Contract governsRelationship CustomerRelationship (many-to-one)
- Contract renewsIntoOpportunity Opportunity (many-to-one)
- Case raisedByParty Party (many-to-one)
- Case filedForRelationship CustomerRelationship (many-to-one)
- Case aboutProduct Product (many-to-one)
- Activity loggedAgainstOpportunity Opportunity (many-to-one)
- Activity loggedAgainstCase Case (many-to-one)
- Activity involvesParty Party (many-to-many)
- Forecast coversTerritory Territory (many-to-one)

## Attributes

- Party: partyExternalRef (string), partyStatus (string)
- Person: fullName (string), email (string), phone (string)
- Organisation: organisationName (string), registrationNumber (string), industry (string), website (string)
- Account: accountName (string), annualRevenue (decimal), accountType (string), employeeCount (integer)
- Contact: jobTitle (string), department (string), preferredChannel (string)
- CustomerRelationship: relationshipNumber (string), relationshipType (string), relationshipStatus (string), relationshipStartDate (date)
- Territory: territoryName (string), region (string)
- Assignment: assignedAt (dateTime), assignmentEndedAt (dateTime), assigneeRef (string), assignmentRole (string)
- ConsentRecord: consentPurpose (string), consentChannel (string), consentStatus (string), consentCapturedAt (dateTime), consentWithdrawnAt (dateTime), consentSource (string)
- Campaign: campaignName (string), campaignType (string), campaignStartDate (date), campaignEndDate (date), budgetedCost (decimal), campaignStatus (string)
- CampaignMember: memberStatus (string), targetedAt (dateTime), respondedAt (dateTime), responseType (string), suppressionReason (string)
- Lead: leadSource (string), capturedAt (dateTime), company (string), leadScore (integer), leadStatus (string)
- LeadConversion: convertedAt (dateTime), convertedBy (string), conversionOutcome (string), matchedExistingParty (boolean)
- Opportunity: opportunityName (string), amount (decimal), probability (decimal), closeDate (date), opportunityStatus (string)
- Pipeline: pipelineName (string), stageCount (integer)
- PipelineStage: stageName (string), stageOrder (integer), defaultProbability (decimal)
- StageTransition: transitionedAt (dateTime), transitionedBy (string), transitionReason (string)
- Product: productCode (string), productName (string), listPrice (decimal)
- OpportunityLine: opportunityQuantity (decimal), expectedUnitPrice (decimal), expectedRevenue (decimal), termMonths (integer)
- Quote: quoteNumber (string), quoteDate (date), validUntil (date), quoteTotal (decimal), quoteStatus (string)
- QuoteLine: quotedQuantity (decimal), quotedUnitPrice (decimal), discountPercent (decimal)
- Contract: contractNumber (string), contractStart (date), contractEnd (date), contractValue (decimal), contractStatus (string)
- Forecast: forecastPeriod (string), forecastAmount (decimal), commitAmount (decimal), bestCaseAmount (decimal)
- Activity: activityType (string), occurredAt (dateTime), summary (string)
- Case: caseNumber (string), subject (string), priority (string), openedAt (dateTime), resolvedAt (dateTime), slaDueAt (dateTime), escalated (boolean), caseStatus (string)

## Lifecycle

- CustomerRelationship: prospect → active → dormant | ended
- CampaignMember: targeted → delivered → responded | no_response | suppressed
- Lead: new → contacted → qualified → converted | disqualified
- LeadConversion: initiated → matched → completed | rejected
- Opportunity: lead → qualified → proposal → won | lost
- Quote: draft → configured → priced → approved → presented → accepted | rejected | expired
- Contract: draft → active → expired | terminated
- Case: new → in_progress → waiting_on_customer → resolved → closed
- Campaign: planned → active → completed
- ConsentRecord: captured → active → withdrawn | expired

## Roles

- **SalesRepRole** (bearer: person) — owns relationships and opportunities, qualifies leads, builds quotes, and logs activities; permissions: Party:read, CustomerRelationship:read, CustomerRelationship:write, Lead:read, Lead:write, LeadConversion:write, Opportunity:read, Opportunity:write, OpportunityLine:write, Quote:read, Quote:write, Activity:read, Activity:write
- **SalesManagerRole** (bearer: person) — configures pipelines and territories, reviews forecasts, approves discounts, and manages assignments; permissions: Pipeline:read, Pipeline:write, Territory:read, Territory:write, Forecast:read, Forecast:write, Assignment:read, Assignment:write, Opportunity:read, Quote:read
- **MarketingSpecialistRole** (bearer: person) — plans campaigns, manages audiences and responses, and routes leads to sales; permissions: Campaign:read, Campaign:write, CampaignMember:read, CampaignMember:write, Lead:read, Lead:write, ConsentRecord:read
- **ServiceAgentRole** (bearer: person) — owns cases through resolution and logs customer interactions; permissions: Case:read, Case:write, Activity:read, Activity:write, Party:read, CustomerRelationship:read, Product:read
- **ContractAdminRole** (bearer: person) — administers contracts and renewal handoffs; permissions: Contract:read, Contract:write, Opportunity:read, CustomerRelationship:read
- **DataStewardRole** (bearer: person) — resolves duplicate parties and maintains source-to-master identity links; permissions: Party:read, Party:write, LeadConversion:read, CustomerRelationship:read

## Primary workflow

Run campaign → target parties → capture responses and leads → qualify and convert → establish customer relationship → open opportunity → progress stages → configure and quote products → close won → sign contract → hand off to fulfilment

Supporting workflows:

- Consumer acquisition: capture person → verify consent → qualify → establish customer relationship → sell product
- B2B acquisition: capture organisation and contacts → qualify buying group → establish account relationship → open opportunity
- Service: raise case → assign agent → log interactions → resolve → close
- Forecasting: analyse stage history → weight open opportunities → roll up by territory → commit forecast
- Renewal: monitor contract end dates → open renewal opportunity → re-quote → extend or terminate
