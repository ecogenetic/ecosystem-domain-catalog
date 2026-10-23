# Software addendum — MDM

## Additional concepts

- **CustomerTenantMaster** — The mastered record for a software customer tenant.
- **ProductMasterRecord** — The mastered record for a software product edition.

## Additional relationships

- CustomerTenantMaster linksProductMaster ProductMasterRecord (many-to-many)

## Additional roles

- **Software Data Steward** — Stewards customer-tenant and product-edition master records. Bearer: person. Permissions: MasterRecord:read, MasterRecord:write, MatchRule:read.

## Regulatory notes

- A mastered tenant keeps the party identifier and does not copy license or deployment state.
