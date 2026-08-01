# Gaming & Gambling

Licensed betting and gaming operators: player accounts, wagers, wallets and payments,
bonusing and promotions, responsible gambling controls, and licensing compliance. The player
account with its wallet and protection limits is the central construct.

## Terminology

- Player — the registered, age-verified account holder who places wagers.
- Wallet — the player's balance, split between cash and bonus funds.
- Wager / Bet — a stake placed on an outcome; settled as won, lost, or void.
- Bonus — promotional funds or free bets with wagering requirements before withdrawal.
- Responsible gambling (RG) — deposit/loss/session limits, cool-off, and self-exclusion.
- Segmentation — grouping players by value and risk for CVM offers, constrained by RG status.

## Regulatory notes

- Age and identity verification is mandatory before real-money play (and often before deposit).
- Responsible gambling limits and self-exclusion are legal obligations: any campaign, offer, or
  wager acceptance flow must check RG status first — generated workflows should include a gate.
- AML applies to deposits and withdrawals; source-of-funds checks trigger at thresholds.
- Marketing to self-excluded or vulnerable players is prohibited; consent and suppression lists
  must be enforced in CVM/campaign logic.
- License jurisdictions require segregated reporting of stakes, winnings, and player funds.

## Business value chain

1. Register, age-verify and risk-screen a player.
2. Fund a segregated wallet and apply deposit, loss, wager and session limits.
3. Publish events/markets or game rounds and accept eligible wagers.
4. Price exposure, suspend markets where required and settle outcomes.
5. Allocate winnings, bonuses, taxes, commissions and withdrawals.
6. Monitor player protection, fraud, AML, disputes and regulatory reporting.

## Cross-domain capability map

| Capability | Typical owning domain |
|---|---|
| Player relationship, service and campaigns | CRM / CVM |
| Wallet, ledger and payment movements | FIN |
| Offers, bonuses and rewards | CPQ / LSM |
| Responsible-play and compliance controls | GRC |
| Fraud monitoring and investigation | RAF |
| Content, event and market publication | CMS |
| Partner and affiliate relationships | PRM |

## Domain integration model

| Canonical detail | Industry specialization | Owning domain | Shared identifiers |
|---|---|---|---|
| Party and customer | Verified account holder | CRM / MDM | partyId, playerId, customerRelationshipId |
| Product | Game, event, market or promotion definition | PIM / CMS | productId, productVersionId |
| Offer and quote | Published price or eligible promotion | CPQ | offerId, quoteId |
| Agreement and account | Terms acceptance and wallet account | CRM / FIN | agreementId, walletId, accountId |
| Interaction | Digital, retail or service contact | CRM | interactionId, channelId |
| Order and process | Registration or account transaction request | OMS / BPM | orderId, processInstanceId |
| Service | Enabled account or platform service | SIV | serviceInstanceId |
| Transaction | Wallet or settlement movement | FIN | transactionId, walletId |
| Case | Verification, protection, dispute or investigation case | BPM / CCM | caseId |
| Consent | Marketing and data-use permission | CRM / GRC | consentId, playerId, purposeCode |
| Decision | Eligibility, protection, AML or fraud result | RAF / GRC | decisionId, policyVersionId |
| Partner | Affiliate, content or payment provider | PRM | partnerId |

### Integration rules

- A party identifies the person while the regulated account relationship has its own identifier.
- Product, market and price versions referenced by accepted transactions must be retained.
- Each object keeps its own identifier and the correlation identifiers of upstream objects.
- Lifecycle events carry eventId, eventType, occurredAt, sourceDomain, entityId, entityVersion and correlationId.
- Domains exchange references and events; identity, ledger and protection state remain authoritative.
- Industry terminology and states map to canonical concepts through overlays and mappings.

## Modeling rules

- Keep player identity, wallet, wager, wager leg, market, outcome and settlement separate.
- Evaluate age verification, jurisdiction, self-exclusion and applicable limits before acceptance.
- Treat wallet movements as immutable ledger entries and distinguish cash from restricted bonus funds.
- Version market prices and rules so every accepted wager retains its decision context.
- Suppress marketing and incentives when consent or responsible-play eligibility is absent.
