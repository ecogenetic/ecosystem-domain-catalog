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

## Modeling rules

- Keep player identity, wallet, wager, wager leg, market, outcome and settlement separate.
- Evaluate age verification, jurisdiction, self-exclusion and applicable limits before acceptance.
- Treat wallet movements as immutable ledger entries and distinguish cash from restricted bonus funds.
- Version market prices and rules so every accepted wager retains its decision context.
- Suppress marketing and incentives when consent or responsible-play eligibility is absent.
