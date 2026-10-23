# Software addendum — ARC

## Additional concepts

- **ProductArchitectureDecision** — An architecture decision made for a named product edition.

## Additional relationships

- ProductArchitectureDecision governsProductEdition ProductEdition (many-to-one)

## Additional roles

- **Product Architect** — Owns architecture decisions for a product edition. Bearer: person. Permissions: ArchitectureDecision:read, ArchitectureDecision:write, SystemContext:read.

## Regulatory notes

- Product architecture decisions should retain the product edition identifier used when the decision was accepted.
