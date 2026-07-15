# Healthcare addendum — MES

## Additional concepts

- **ValidatedBatch** — A production batch under validated process control for a regulated product.
- **ElectronicBatchRecord** — The electronic record of process steps, deviations, and releases for a batch.
- **InProcessQualityCheck** — A quality check performed during manufacturing before batch release.

## Additional relationships

- ValidatedBatch relatesToContext within the MES base model (many-to-one).
- ElectronicBatchRecord is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Batch Release Officer** — Reviews electronic batch records and releases or rejects batches.

## Regulatory notes

- Batch release is gated on completed in-process checks and deviation closure.
- Electronic batch records are append-only in spirit — corrections are amendments.
