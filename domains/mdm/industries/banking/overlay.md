# Banking addendum — MDM

## Additional concepts

- **PartyMaster** — The golden party record for a banking customer or counterparty.
- **KYCAttributeSet** — Master-data attributes required for KYC classification of a party.
- **GoldenRecordMerge** — A controlled merge of duplicate party records with audit of survivors.

## Additional relationships

- PartyMaster relatesToContext within the MDM base model (many-to-one).
- KYCAttributeSet is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Party Data Steward** — Approves golden-record merges and KYC attribute quality.

## Regulatory notes

- Party merges are never silent — survivors and losers must be audited.
- KYC attribute changes may require re-verification before product eligibility updates.
