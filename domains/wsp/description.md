# WSP — Wholesale Partner and Settlement Management

Manages wholesale partners, host-MNO agreements, service rate cards, settlement periods, statements, reconciliation, and disputes.

## Concepts

- **WholesalePartner** — An organization supplying or consuming services under a wholesale arrangement.
- **HostMNO** — The mobile network operator providing network access to an MVNO.
- **WholesaleAgreement** — A contract defining wholesale services, commercial terms, and obligations.
- **WholesaleService** — A network or platform service supplied under a wholesale agreement.
- **WholesaleRate** — A price applicable to a measured unit of wholesale service.
- **SettlementPeriod** — The time interval covered by a wholesale reconciliation and settlement.
- **SettlementStatement** — A partner statement of wholesale usage, charges, credits, and amounts due.
- **SettlementDispute** — A documented disagreement over a settlement statement or its underlying records.

## Taxonomy

- HostMNO is a kind of Wholesale partner.
- SettlementStatement is a kind of Wholesale document.
- SettlementDispute is a kind of Wholesale case.

## Relationships

- HostMNO actsAsWholesalePartner WholesalePartner (one-to-one)
- WholesaleAgreement governsWholesalePartner WholesalePartner (many-to-one)
- WholesaleAgreement includesWholesaleService WholesaleService (one-to-many)
- WholesaleRate pricesWholesaleService WholesaleService (many-to-one)
- SettlementStatement coversSettlementPeriod SettlementPeriod (many-to-one)
- SettlementStatement settlesWholesaleAgreement WholesaleAgreement (many-to-one)
- SettlementDispute disputesSettlementStatement SettlementStatement (many-to-one)

## Attributes

- WholesalePartner: wholesalePartnerId (string)
- HostMNO: hostMNOId (string)
- WholesaleAgreement: wholesaleAgreementId (string)
- WholesaleService: wholesaleServiceId (string)
- WholesaleRate: wholesaleRateId (string)
- SettlementPeriod: settlementPeriodId (date)
- SettlementStatement: settlementStatementId (string)
- SettlementDispute: settlementDisputeId (string)

## Lifecycle

- SettlementStatement: received → reconciled → disputed → approved → settled

## Roles

- **Wholesale Settlement Analyst** (bearer: person) — reconciles partner statements and manages settlement disputes; permissions: WholesaleAgreement:read, WholesaleRate:read, SettlementStatement:read, SettlementStatement:write, SettlementDispute:write.

## Primary workflow

Contract partner → publish wholesale rates → receive statement → reconcile usage → raise dispute or approve → settle