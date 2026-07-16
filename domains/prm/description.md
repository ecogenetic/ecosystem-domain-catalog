# PRM — Partner and Dealer Management

Manages partners, dealers, agreements, channel roles, territories, commission plans, statements, and credentials.

## Concepts

- **Partner** — An organization participating in sales, distribution, service, or fulfilment on behalf of the enterprise.
- **Dealer** — A partner authorized to sell or service offerings through an approved channel.
- **PartnerAgreement** — A contract defining partner rights, obligations, commercial terms, and duration.
- **PartnerRole** — A formally assigned function performed by a partner organization.
- **Territory** — A geographic or market area assigned to a partner or dealer.
- **CommissionPlan** — A rule set determining partner remuneration for eligible outcomes.
- **CommissionStatement** — A periodic statement of calculated commissions, adjustments, and amounts due.
- **PartnerCredential** — A credential authorizing a partner user or system to access channel capabilities.

## Taxonomy

- Dealer is a kind of Partner.
- PartnerRole is a kind of Role.
- CommissionStatement is a kind of Partner document.

## Relationships

- Dealer operatesAsPartner Partner (one-to-one)
- PartnerAgreement governsPartner Partner (many-to-one)
- Partner holdsPartnerRole PartnerRole (one-to-many)
- Partner assignedTerritory Territory (many-to-many)
- CommissionPlan appliesToPartner Partner (many-to-many)
- CommissionStatement calculatedUnderPlan CommissionPlan (many-to-one)
- PartnerCredential authorizesPartner Partner (many-to-one)

## Attributes

- Partner: partnerId (string)
- Dealer: dealerId (string)
- PartnerAgreement: partnerAgreementId (string)
- PartnerRole: partnerRoleId (string)
- Territory: territoryId (string)
- CommissionPlan: commissionPlanId (string)
- CommissionStatement: commissionStatementId (string)
- PartnerCredential: partnerCredentialId (string)

## Lifecycle

- Partner: prospective → onboarding → active → suspended → terminated

## Roles

- **Channel Manager** (bearer: person) — onboards partners and governs agreements, territories, and commission plans; permissions: Partner:read, Partner:write, Dealer:read, PartnerAgreement:write, Territory:write, CommissionPlan:write.

## Primary workflow

Register partner → complete onboarding → sign agreement → assign role and territory → transact → calculate commission