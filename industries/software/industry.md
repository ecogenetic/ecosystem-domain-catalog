# Software

Product and platform companies that design, build, license, and operate software:
customer relationships, product editions, user-interface and mobile applications,
backend services, architecture, cloud platforms, servers, databases, and releases.
The running application is not the customer, and a cloud account is not a commercial account.

## Terminology

- Tenant — the customer organisation or isolated usage context that consumes a software product.
- Product edition — a sellable version of a software product, distinct from a deployed release.
- Entitlement — the right to use a feature, seat, or metered capacity under a license agreement.
- Application — a user-interface, mobile, or backend software product that is built and released.
- Architecture component — a structural part of a system, distinct from a user-interface widget.
- Cloud environment — a landing-zone environment in a cloud account, distinct from a release target.
- Release target — the environment a deployment is aimed at.
- Service instance — a deployed occurrence recorded in the service inventory, distinct from a backend service definition and from an IT service catalog entry.

## Regulatory notes

- Security and privacy programs (SOC 2, ISO 27001, GDPR, POPIA) require evidence of control operation, access, and customer-data purpose.
- Accessibility expectations apply to user-interface and mobile applications that customers use.
- App-store distribution rules apply to mobile releases, review outcomes, and store listings.
- License and entitlement decisions should retain the product edition and agreement version used at the time of the decision.
- Production changes should preserve approval, deployment, and rollback evidence.

## Business value chain

1. Identify the customer party and the software tenant that will consume the product.
2. Define the product edition, price it, and quote seats, features, or metered use.
3. Agree a license and issue entitlements.
4. Describe the architecture, cloud landing zone, compute, and data stores the product needs.
5. Build the user interface, mobile application, and backend services.
6. Release and deploy them onto a named target.
7. Record the live service instance, assure it, and handle incidents and change.
8. Recognise subscription revenue, enable users, and expand or renew the relationship.

## Cross-domain capability map

| Capability | Typical owning domain |
|---|---|
| Customer party, subscription opportunity, and commercial contract | CRM |
| Adoption, churn, and expansion decisions | CVM |
| Seat, edition, and usage pricing | CPQ |
| Sellable product and edition catalog | PIM |
| Product revision and engineering change | PLM |
| Digital storefront and checkout | ECOM |
| License and entitlement fulfilment orders | OMS |
| License agreements, seats, feature access, and usage meters | LIC |
| User-interface applications | UIA |
| Mobile applications and store distribution | MOB |
| Backend services and API contracts | BKS |
| Architecture decisions, components, and interface contracts | ARC |
| Cloud accounts, landing zones, and cloud environments | CLD |
| Servers, clusters, and compute capacity | SRV |
| Databases, schemas, and data stores | DBS |
| Repositories, releases, and deployments | REL |
| Live service inventory | SIV |
| Service alarms and customer impact | SAM |
| Incidents, changes, and configuration items | ITSM |
| Subscription invoicing and the general ledger | FMS / ERP |
| Security controls, policies, and audit evidence | GRC |
| Release quality and defect control | QMS |
| Engineering organisation and product enablement | HCM / LMS |
| Release approval workflow | BPM |
| Product documentation | CMS |
| Adoption and reliability analytics | BI |
| Customer and product mastering | MDM |
| Marketplace and technology partners | PRM |

## Domain integration model

| Canonical detail | Software specialization | Owning domain | Shared identifiers |
|---|---|---|---|
| Party and customer | Software customer account and tenant | CRM / MDM | partyId, customerRelationshipId |
| Product | Product edition and revision | PIM / PLM | productId, productVersionId |
| Offer and quote | Seat, edition, or usage quote | CPQ | offerId, quoteId, productVersionId |
| Agreement | License agreement | LIC / CRM | licenseAgreementId, agreementId |
| Entitlement | Seat, feature access, or usage meter | LIC | entitlementId, licenseAgreementId |
| Application | User interface, mobile app, or backend service | UIA / MOB / BKS | applicationId |
| Architecture | Decision, component, and interface contract | ARC | architectureDecisionId, componentId |
| Cloud platform | Cloud account, landing zone, and cloud environment | CLD | cloudAccountId, landingZoneId |
| Compute | Host, cluster, and runtime | SRV | computeHostId |
| Data | Data store and database instance | DBS | dataStoreId |
| Release | Repository, release, deployment, and release target | REL | releaseId, deploymentId, environmentId |
| Service | Deployed service instance | SIV | serviceInstanceId, applicationId |
| Assurance | Application alarm and tenant impact | SAM | alarmId, customerRelationshipId |
| Case | Incident, change, or release-approval case | ITSM / BPM | incidentId, changeId, caseId |
| Consent | Product-data and communication permission | CRM / GRC | consentId, partyId, purposeCode |
| Finance | Subscription invoice and revenue journal | FMS / ERP | invoiceId, journalEntryId |
| Partner | Marketplace or integration partner | PRM | partnerId, agreementId |

### Integration rules

- A party is the legal person or organisation. A software tenant is the usage context for that customer, not a second customer.
- A product edition is immutable input to quotes, license agreements, architecture decisions, and releases.
- A license agreement is a contract specialization. It is not the CRM opportunity and not the entitlement.
- A user-interface component is a screen widget. An architecture component is a structural part of the system.
- A cloud environment belongs to a landing zone. A release target is where a deployment is directed. They are correlated by identifier, not treated as one object.
- A backend service defines behavior and an API contract. A service instance is the deployed occurrence. An IT service is the operational service people support.
- A cloud account is a provider billing and administrative boundary, not a CRM account and not a financial account.
- A source repository is not a supply-chain shipment, and product documentation is not a configuration item.
- Service assurance alarms are monitoring signals. They may lead to an incident; they are not the incident.
- Each object keeps its own identifier and the correlation identifiers of upstream objects.
- Lifecycle events carry eventId, eventType, occurredAt, sourceDomain, entityId, entityVersion, and correlationId.
- Domains exchange references and events instead of copying another domain's authoritative state.

## Modeling rules

- Keep the customer party, software tenant, license agreement, and entitlement as separate objects.
- Keep user-interface, mobile, and backend applications as specializations of one software application, with their own lifecycles.
- Do not collapse architecture components with user-interface components.
- Do not collapse cloud accounts with CRM accounts or financial accounts.
- Do not collapse cloud environments with release targets.
- Do not collapse backend services, service instances, and IT services.
- Attach pricing, entitlement, and architecture decisions to the product edition used at decision time.
- Keep deployment evidence on the release, including the release target and the resulting service instance.
- Industry mappings align a source record to the owning domain first, then add software relationships.
