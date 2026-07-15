# Banking addendum — LSM

## Additional concepts

- **AssetFinanceLease** — A lease financing a customer asset (vehicle, equipment) on bank books.
- **ResidualValueSchedule** — The scheduled residual value used in lease pricing and end-of-term options.
- **LeaseAffordabilityCheck** — Affordability assessment gating lease approval.

## Additional relationships

- AssetFinanceLease relatesToContext within the LSM base model (many-to-one).
- ResidualValueSchedule is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Lease Credit Officer** — Reviews lease affordability and residual risk before activation.

## Regulatory notes

- Lease activation is gated on affordability and KYC.
- Residual value assumptions must be documented for audit.
