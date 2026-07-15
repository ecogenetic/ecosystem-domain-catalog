# Banking addendum — ERP

## Additional concepts

- **CostCentre** — A bank GL cost centre used to allocate ERP journal postings to business units.
- **RegulatoryReportLine** — A mapped line for prudential or statutory reporting fed from ERP ledgers.
- **IntercompanyLoan** — An internal funding arrangement between legal entities posted through ERP.

## Additional relationships

- CostCentre relatesToContext within the ERP base model (many-to-one).
- RegulatoryReportLine is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Finance Controller** — Owns chart of accounts integrity and regulatory report extracts from ERP.

## Regulatory notes

- GL postings that feed regulatory reports require maker-checker approval.
- Intercompany loans must retain an immutable audit trail of principal and interest.
