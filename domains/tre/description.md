# TRE — Treasury and Asset/Liability Management

Treasury and Asset/Liability Management manages funding, liquidity, treasury deals, maturity structure, interest-rate risk, transfer pricing, limits, and treasury positions.

## Concepts
- **TreasuryPosition** — an aggregated treasury exposure or balance position at a point in time.
- **FundingSource** — a source of wholesale, deposit, secured, or central-bank funding.
- **LiquidityBuffer** — a portfolio or reserve maintained to meet liquidity needs.
- **MaturityBucket** — a time bucket used to aggregate expected inflows, outflows, or repricing.
- **InterestRateRiskPosition** — a measured exposure to changes in interest rates.
- **FundsTransferPrice** — an internal transfer-pricing rate applied to products or balances.
- **TreasuryLimit** — a risk or dealing limit constraining treasury activity.
- **TreasuryDeal** — a treasury transaction executed to fund, hedge, invest, or manage liquidity.

## Taxonomy
- InterestRateRiskPosition is a kind of TreasuryPosition.
- LiquidityBuffer is a kind of TreasuryPosition.

## Relationships
- TreasuryPosition fundedBy FundingSource (many-to-many)
- TreasuryPosition assignedMaturityBucket MaturityBucket (many-to-one)
- InterestRateRiskPosition pricedBy FundsTransferPrice (many-to-one)
- TreasuryLimit constrainsDeal TreasuryDeal (one-to-many)
- TreasuryDeal changesPosition TreasuryPosition (many-to-many)

## Attributes
- TreasuryPosition: positionReference (string), asOfDate (date), amount (decimal), currencyCode (string)
- FundingSource: fundingReference (string), fundingType (string), maturityDate (date)
- LiquidityBuffer: bufferReference (string), eligibleAmount (decimal)
- MaturityBucket: bucketName (string), startDays (integer), endDays (integer)
- InterestRateRiskPosition: riskMeasure (string), riskValue (decimal)
- FundsTransferPrice: rateReference (string), transferRate (decimal), effectiveDate (date)
- TreasuryLimit: limitReference (string), limitAmount (decimal)
- TreasuryDeal: dealReference (string), dealStatus (string), tradeDate (date), settlementDate (date)

## Lifecycle
- TreasuryDeal: proposed → approved → executed → settled → matured | cancelled

## Roles
- **Treasury Dealer Role** (bearer: person) — proposes and executes treasury deals within approved limits; permissions: TreasuryDeal:read, TreasuryDeal:write, TreasuryPosition:read
- **Treasury Risk Approver Role** (bearer: person) — approves limits and deals requiring escalation; permissions: TreasuryLimit:read, TreasuryLimit:write, TreasuryDeal:read

## Primary workflow
Forecast liquidity → assess positions and maturity gaps → source funding or hedge → check limits → approve deal → execute → settle → update positions and transfer pricing
