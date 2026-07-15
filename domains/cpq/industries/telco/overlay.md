# Telco addendum — CPQ

## Additional concepts

- **PlanConfiguration** — A configured rate plan or bundle selected during quoting.
- **DeviceSubsidyQuote** — A quote line for a device with subsidy or instalment terms.
- **CreditVettedQuote** — A quote that may only convert after credit vetting for postpaid.

## Additional relationships

- PlanConfiguration relatesToContext within the CPQ base model (many-to-one).
- DeviceSubsidyQuote is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Telco Quote Specialist** — Configures plans and device subsidies and routes quotes for credit vetting.

## Regulatory notes

- Postpaid quotes must not convert to orders until credit vetting passes.
- Subsidy terms must be disclosed on the quote before acceptance.
