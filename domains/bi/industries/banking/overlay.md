# Banking addendum — BI

## Additional concepts

- **RiskMetricCube** — An analytical cube or dataset of risk metrics for regulatory or management reporting.
- **LiquidityDashboard** — A curated dashboard of liquidity and funding indicators.
- **ModelValidationReport** — A report documenting validation of a credit or risk model used in BI.

## Additional relationships

- RiskMetricCube relatesToContext within the BI base model (many-to-one).
- LiquidityDashboard is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Risk Reporting Analyst** — Publishes risk metrics and validates dashboard figures against source systems.

## Regulatory notes

- Regulatory risk metrics must be reconcilable to source ledgers.
- Model validation status should be visible wherever model outputs are published.
