# Software addendum — CVM

## Additional concepts

- **ProductLedSegment** — A customer segment defined by product adoption or expansion potential.
- **SeatExpansionOffer** — An offer to expand seats or features for a software tenant.

## Additional relationships

- SeatExpansionOffer targetsProductLedSegment ProductLedSegment (many-to-one)

## Additional roles

- **Product Growth Analyst** — Scores expansion and churn for software tenants. Bearer: person. Permissions: Segment:read, Offer:read, Offer:write, ChurnRisk:read.

## Regulatory notes

- Expansion offers should record the product edition and the evidence used to choose the treatment.
