# Banking addendum — TRE

## Additional concepts
- **RegulatoryLiquidityBuffer** — a LiquidityBuffer classified for regulatory liquidity reporting.
- **DepositFundingSource** — a FundingSource derived from customer deposit balances.
- **LiquidityStressScenario** — a named scenario used to assess liquidity resilience.

## Additional relationships
- DepositFundingSource derivedFromAccount FinancialAccount (many-to-many)
- RegulatoryLiquidityBuffer reportedUnderScenario LiquidityStressScenario (many-to-many)

## Additional roles
- **Asset Liability Committee Role** — organisation role that reviews liquidity, funding, interest-rate risk, and transfer-pricing policy.

## Regulatory notes
- Liquidity and interest-rate positions must retain as-of date, currency, source lineage, and model or policy version.
- Treasury limits and high-value deal approvals should use maker-checker controls.
- Regulatory calculations should remain reproducible from immutable input snapshots.
