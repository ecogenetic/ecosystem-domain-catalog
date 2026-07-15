# Telco addendum — PLM

## Additional concepts

- **DeviceSKURevision** — A revision of a handset or CPE product definition through design and launch.
- **FirmwareBaseline** — An approved firmware version associated with a device SKU revision.
- **TypeApprovalRecord** — Regulatory type-approval evidence required before commercial launch.

## Additional relationships

- DeviceSKURevision relatesToContext within the PLM base model (many-to-one).
- FirmwareBaseline is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Device Product Manager** — Owns device SKU revisions and launch readiness including type approval.

## Regulatory notes

- Commercial launch is gated on type approval for the target jurisdiction.
- Firmware baselines must be traceable to the SKU revision sold to customers.
