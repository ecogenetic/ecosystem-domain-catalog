# Telco addendum — CRM

Telecommunications CRM manages the relationship and journey around a customer rather than replacing
the operator's subscription, billing, charging, network, provisioning, assurance, fraud, number, or
partner systems. It gives sales, care, retention, digital, dealer, and enterprise teams a joined view
of the paying party, service identities, subscriptions, products, interactions, consent, cases,
commercial opportunities, service impact, and fulfilment progress.

A **CustomerParty** is the person or organisation responsible for the commercial relationship. A
**Subscriber** is the operational service identity or line that consumes services and may differ from
the payer, authorised contact, device user, or beneficiary. This distinction must be preserved.

## Additional concepts

### Customer and relationship

- **CustomerParty** — a Person or Organisation that owns, pays for, administers, or is otherwise responsible for a telco relationship.
- **AuthorisedContact** — a Person permitted to enquire about or change a relationship, account, or subscription within an assigned authority.
- **SubscriberRelationship** — a CustomerRelationship connecting a CustomerParty to one or more customer accounts, subscriptions, and service identities.
- **Subscriber** — a service identity or line that consumes network services; distinct from the paying CustomerParty.
- **Subscription** — the contracted commercial service relationship governed by a plan and lifecycle.
- **ServiceLine** — the operational line activated by a Subscription and represented to CRM as a Subscriber.
- **RatePlan** — the tariff governing recurring charges, usage rates, allowances, and commitment terms.
- **Device** — customer equipment associated with a service line for sales, care, warranty, and upgrade journeys.
- **CustomerAccount** — the subscription-domain commercial account holding one or more Subscriptions.
- **BillingAccountReference** — the CRM-visible reference to the billing account used for invoice enquiries and payment-related cases.
- **ChargingAccountReference** — the CRM-visible reference to balances and allowances used for real-time charging enquiries.

### Acquisition and commercial journeys

- **AcquisitionJourney** — the tracked journey from campaign or dealer lead through identity verification, product selection, order, provisioning, and activation.
- **UpgradeJourney** — a commercial journey that changes a plan, device, bundle, or service while preserving the customer relationship.
- **PortabilityJourney** — a tracked port-in or port-out journey linked to the number-management PortingRequest and its events.
- **DealerReferral** — attribution of a Lead, Opportunity, or AcquisitionJourney to a dealer or partner.
- **ServiceOrderHandoff** — the traceable handoff from a won Opportunity or accepted Quote to a provisioning ServiceOrder.
- **ContractRenewalJourney** — a renewal journey triggered by commitment end dates and informed by value, propensity, and churn risk.

### Care, retention, and service experience

- **BillingEnquiry** — a Case concerning a billing account, invoice, adjustment, credit, or payment.
- **BalanceEnquiry** — a Case concerning a prepaid or hybrid balance, allowance, charge, or reservation.
- **ServiceEnquiry** — a Case concerning a live ServiceInstance, ServiceLine, configuration, or product-service mapping.
- **ProvisioningEnquiry** — a Case concerning an order, activation, configuration change, delay, or provisioning fallout.
- **NetworkExperienceCase** — a Case linked to customer impact from degradation, outage, or an SLA violation.
- **RetentionJourney** — a consent-aware journey initiated by churn risk, contract end, service dissatisfaction, port-out intent, or declining usage.
- **FraudOrRiskReferral** — a restricted referral from CRM to a revenue-assurance or fraud Investigation; CRM retains only the operational reference and permitted status.
- **InteractionOutcome** — the outcome of a call, message, store visit, digital session, complaint, save attempt, or treatment response.

### Enterprise and partner relationships

- **EnterpriseRelationship** — a SubscriberRelationship for an Organisation with multiple contacts, sites, billing accounts, contracts, subscriptions, and service lines.
- **PartnerRelationship** — a CustomerRelationship with a dealer, distribution partner, service partner, MVNO, or wholesale counterparty.
- **ServiceSite** — an enterprise location at which fixed, mobile, IoT, or managed services are delivered.

## Taxonomy

- CustomerParty is a kind of Party.
- AuthorisedContact is a kind of Person.
- SubscriberRelationship is a kind of CustomerRelationship.
- Subscriber is a kind of telco Service Identity and ServiceLine, not a kind of Person.
- EnterpriseRelationship is a kind of SubscriberRelationship.
- PartnerRelationship is a kind of CustomerRelationship.
- AcquisitionJourney, UpgradeJourney, PortabilityJourney, RetentionJourney, and ContractRenewalJourney are kinds of CustomerJourney.
- BillingEnquiry, BalanceEnquiry, ServiceEnquiry, ProvisioningEnquiry, and NetworkExperienceCase are kinds of Case.
- DealerReferral and ServiceOrderHandoff are kinds of TraceableHandoff.

## Relationships

- SubscriberRelationship relationshipWithCustomerParty CustomerParty (many-to-one)
- SubscriberRelationship hasAuthorisedContact AuthorisedContact (many-to-many)
- SubscriberRelationship ownsCustomerAccount CustomerAccount (one-to-many)
- SubscriberRelationship coversSubscription Subscription (one-to-many)
- Subscription activatesSubscriber Subscriber (one-to-many)
- Subscription usesRatePlan RatePlan (many-to-one)
- Subscriber usesMobileNumber MobileNumber (many-to-one)
- Subscriber usesSimProfile SIMProfile (many-to-one)
- Subscriber usesDevice Device (many-to-many)
- SubscriberRelationship usesBillingAccount BillingAccount (one-to-many)
- SubscriberRelationship usesChargingAccount ChargingAccount (one-to-many)
- Opportunity changesSubscription Subscription (many-to-one)
- Opportunity recommendsRatePlan RatePlan (many-to-one)
- Opportunity createsServiceOrder ServiceOrder (one-to-one)
- ServiceOrderHandoff handsOpportunityToServiceOrder ServiceOrder (one-to-one)
- AcquisitionJourney originatedFromCampaignMember CampaignMember (many-to-one)
- AcquisitionJourney originatedFromDealer Partner (many-to-one)
- AcquisitionJourney createsSubscription Subscription (one-to-one)
- PortabilityJourney tracksPortingRequest PortingRequest (one-to-one)
- BillingEnquiry concernsInvoice Invoice (many-to-one)
- BalanceEnquiry concernsChargingAccount ChargingAccount (many-to-one)
- ServiceEnquiry concernsServiceInstance ServiceInstance (many-to-one)
- ProvisioningEnquiry concernsFalloutCase FalloutCase (many-to-one)
- NetworkExperienceCase concernsCustomerImpact CustomerImpact (many-to-one)
- NetworkExperienceCase concernsAssuranceCase AssuranceCase (many-to-one)
- RetentionJourney informedByChurnRisk ChurnRisk (many-to-one)
- RetentionJourney producesOpportunity Opportunity (one-to-one)
- FraudOrRiskReferral refersInvestigation Investigation (many-to-one)
- PartnerRelationship representsPartner Partner (many-to-one)
- PartnerRelationship representsWholesalePartner WholesalePartner (many-to-one)

## Attributes

- CustomerParty: customerPartyId (string), partyRole (string), identityVerified (boolean)
- AuthorisedContact: authorityType (string), authorityStart (date), authorityEnd (date)
- SubscriberRelationship: relationshipStatus (string), relationshipSegment (string), relationshipStartDate (date)
- Subscriber: subscriberId (string), serviceStatus (string), activatedAt (dateTime)
- Subscription: subscriptionId (string), subscriptionType (string), contractEndDate (date), subscriptionStatus (string)
- ServiceLine: serviceLineId (string)
- RatePlan: planCode (string), planName (string), recurringFee (decimal), commitmentMonths (integer)
- Device: deviceIdentifier (string), deviceType (string), deviceModel (string), eligibilityDate (date)
- AcquisitionJourney: journeyStatus (string), startedAt (dateTime), completedAt (dateTime), acquisitionChannel (string)
- UpgradeJourney: journeyStatus (string), upgradeReason (string), completedAt (dateTime)
- PortabilityJourney: journeyStatus (string), direction (string), requestedAt (dateTime), completedAt (dateTime)
- ServiceOrderHandoff: handedOffAt (dateTime), handoffStatus (string), externalReference (string)
- RetentionJourney: journeyStatus (string), retentionReason (string), saveOutcome (string), completedAt (dateTime)
- InteractionOutcome: outcomeType (string), outcomeAt (dateTime), outcomeValue (decimal)
- ServiceSite: siteName (string), siteReference (string)

## Lifecycle

- SubscriberRelationship: prospect → onboarding → active → suspended → ended
- Subscription: pending → active → suspended → terminated
- Subscriber: reserved → pending_activation → active → suspended → ceased
- AcquisitionJourney: initiated → verified → ordered → provisioning → activated | failed | cancelled
- UpgradeJourney: identified → offered → accepted → provisioned | declined | cancelled
- PortabilityJourney: requested → validated → scheduled → completed | rejected | cancelled
- RetentionJourney: triggered → assessed → contacted → offered → retained | churned | suppressed
- ServiceOrderHandoff: prepared → submitted → acknowledged → completed | failed
- Case: new → in_progress → waiting_on_customer → resolved → closed

## Roles

- **RetailSalesAgentRole** (bearer: person) — acquires customers, captures consent, selects products, and hands accepted sales to fulfilment; permissions: CustomerParty:read, CustomerParty:write, SubscriberRelationship:read, SubscriberRelationship:write, AcquisitionJourney:write, Opportunity:write
- **CustomerCareAgentRole** (bearer: person) — resolves billing, balance, subscription, provisioning, and service enquiries using linked operational references; permissions: SubscriberRelationship:read, Subscription:read, BillingEnquiry:write, BalanceEnquiry:write, ServiceEnquiry:write, ProvisioningEnquiry:write, NetworkExperienceCase:write
- **RetentionAgentRole** (bearer: person) — works consent-eligible churn and renewal journeys using next-best-action recommendations; permissions: RetentionJourney:read, RetentionJourney:write, ChurnRisk:read, Opportunity:read, Opportunity:write, ConsentRecord:read
- **EnterpriseAccountManagerRole** (bearer: person) — manages organisational relationships, contacts, sites, contracts, opportunities, and multi-service estates; permissions: EnterpriseRelationship:read, EnterpriseRelationship:write, ServiceSite:read, ServiceSite:write, Opportunity:read, Opportunity:write, Contract:read
- **DealerChannelAgentRole** (bearer: person) — captures partner-attributed leads and acquisition journeys within delegated authority; permissions: DealerReferral:read, DealerReferral:write, Lead:write, AcquisitionJourney:write, PartnerRelationship:read
- **PortabilityCoordinatorRole** (bearer: person) — tracks customer-facing portability milestones and exceptions; permissions: PortabilityJourney:read, PortabilityJourney:write, SubscriberRelationship:read
- **ServiceRecoveryAgentRole** (bearer: person) — manages proactive and reactive customer communication for service impact and provisioning fallout; permissions: NetworkExperienceCase:read, NetworkExperienceCase:write, ProvisioningEnquiry:read, ProvisioningEnquiry:write, Activity:write

## Primary workflow

Capture party and consent → establish subscriber relationship → verify identity → select product and plan → create opportunity and quote → submit service order → provision and activate subscription and service line → monitor experience → resolve enquiries → decide next best action → retain, renew, upgrade, or terminate

Supporting workflows:

- Acquisition: campaign or dealer response → qualify → verify identity → order → provision → activate
- Upgrade: identify eligibility → recommend plan or device → quote → accept → provision change
- Portability: capture port request → validate identifiers → track events → activate or retain
- Care: identify relationship and service → classify enquiry → retrieve operational reference → resolve or hand off → communicate outcome
- Service recovery: receive customer-impact signal → identify affected relationships → open cases or proactive activities → restore and close
- Retention: consume churn risk and contract dates → apply consent and eligibility → select treatment → contact → record outcome
- Enterprise: manage organisation → authorised contacts → sites → contracts → opportunities → service estate
- Partner: attribute lead → validate partner authority → transact → preserve commission and audit references

## Industry and regulatory notes

- Preserve the distinction between CustomerParty, CustomerAccount, Subscription, Subscriber/ServiceLine, BillingAccount, ChargingAccount, and financial account.
- Number and SIM assignments are time-bounded; CRM displays current identifiers but portability history remains in number management.
- Identity and SIM-registration verification must gate activation where required.
- Marketing consent and communication preferences are channel- and purpose-specific; suppression applies before campaign membership or treatment.
- Customer care should see billing, charging, service, and assurance summaries through references, not duplicate their operational ledgers.
- Fraud and risk details follow least privilege; CRM holds a permitted referral status rather than investigation evidence.
- Enterprise and wholesale relationships may contain many accounts, sites, contracts, subscriptions, contacts, and service instances.
