# Telecommunications

Mobile, fixed-line, and broadband operators: subscriber management, rate plans and bundles,
usage and charging, provisioning, and churn management. Telco systems are high-volume and
event-driven, with the subscriber (not just the person) as the central entity.

## Terminology

- Subscriber — the service identity (often per SIM/line), distinct from the paying customer.
- MSISDN — the mobile number identifying a subscriber.
- Rate Plan / Tariff — the pricing construct governing charges for usage and subscriptions.
- Bundle — packaged allowances (data, voice, SMS) purchased on top of or within a plan.
- Provisioning — activating services on network elements after a commercial order.
- ARPU — average revenue per user; churn — subscriber loss rate.

## Regulatory notes

- Number portability requires traceable subscriber-to-number history.
- Lawful intercept and data retention obligations affect what usage data is stored and for how long.
- Consent rules govern marketing contact (opt-in/opt-out per channel) — relevant to CVM campaigns.
- RICA/SIM-registration style rules require verified identity before activation in many markets.

## Business value chain

1. Acquire and verify a customer or organisation.
2. Configure an offer, rate plan, contract, number, SIM/eSIM and device.
3. Capture an order and provision services across network and IT resources.
4. Record usage, apply online/offline charging and produce a bill or balance update.
5. Assure service quality, resolve faults and communicate customer impact.
6. Manage upgrades, renewals, portability, collections, retention and termination.
7. Settle partner, roaming and wholesale obligations.

## Cross-domain capability map

| Capability | Authoritative domain |
|---|---|
| Customer relationship, sales and care journeys | CRM |
| Subscription, account and service-line lifecycle | SUB |
| Number, SIM/eSIM and portability | NUM |
| Service inventory and activation state | SIV |
| Order orchestration and provisioning | PRV |
| Usage mediation | MED |
| Real-time balance and rating | CHG |
| Billing, invoice and payment allocation | BIL |
| Service assurance and customer impact | SAM |
| Revenue assurance and fraud investigation | RAF |
| Partner and wholesale relationships | PRM / WSP |

## Domain integration model

| Canonical detail | Telecommunications specialization | Owning domain | Shared identifiers |
|---|---|---|---|
| Party and customer | Customer party, account owner or authorised contact | CRM / MDM | partyId, customerRelationshipId |
| Product | Tariff, bundle, device or service specification | PIM | productId, productVersionId |
| Offer and quote | Acquisition, upgrade or retention proposition | CPQ | offerId, quoteId |
| Agreement and account | Customer account, subscription and billing relationship | CRM / SUB / BIL | agreementId, customerAccountId, subscriptionId |
| Interaction | Retail, app, contact-centre, dealer or care contact | CRM | interactionId, channelId |
| Order and process | Activation, change, port or cease request | OMS / PRV | orderId, serviceOrderId |
| Service | Service line and provisioned service instance | SUB / SIV | serviceLineId, serviceInstanceId |
| Transaction | Usage, charge, invoice, payment or adjustment | MED / CHG / BIL | usageRecordId, chargeId, transactionId |
| Case | Care, assurance, fallout, complaint or retention case | CRM / BPM / SAM | caseId |
| Consent | Marketing, channel and data-use permission | CRM / GRC | consentId, partyId, purposeCode |
| Decision | Fraud, credit, eligibility, churn or next-action result | RAF / CVM / GRC | decisionId, policyVersionId |
| Partner | Dealer, roaming, network or wholesale partner | PRM / WSP | partnerId |

### Integration rules

- Party, account, subscription, service line, service instance, number and SIM identifiers are not interchangeable.
- Product versions are immutable inputs to offers, subscriptions, orders, charging and billing.
- Each object keeps its own identifier and the correlation identifiers of upstream objects.
- Lifecycle events carry eventId, eventType, occurredAt, sourceDomain, entityId, entityVersion and correlationId.
- Domains exchange references and events; operational state stays in its owning telco domain.
- Telecommunications terminology and states map to canonical concepts through overlays and mappings.

## Modeling rules

- Keep customer, subscriber, subscription, service line, number, SIM and device as distinct identities.
- Reference operational records from CRM; do not duplicate their balances, invoices, orders or service state.
- Treat all assignments as time-bound, especially subscriber-number, SIM, device, plan and service relationships.
- Record correlation identifiers from commercial order through provisioning, activation, charging and billing.
- Distinguish prepaid, postpaid and hybrid charging without creating separate customer classes.
- Industry mappings should align source records to the owning domain first, then expose additive telco relationships.
