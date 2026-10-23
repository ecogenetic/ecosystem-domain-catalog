# Software addendum — PRM

## Additional concepts

- **MarketplacePartner** — A partner that lists or integrates a software product.
- **IntegrationAgreement** — An agreement that allows a partner to call or embed a product.

## Additional relationships

- IntegrationAgreement governsMarketplacePartner MarketplacePartner (many-to-one)

## Additional roles

- **Technology Partner Manager** — Onboards marketplace partners and integration agreements. Bearer: person. Permissions: Partner:read, Partner:write, PartnerAgreement:read, PartnerAgreement:write.

## Regulatory notes

- An integration agreement should name the API contract or product edition the partner may use.
