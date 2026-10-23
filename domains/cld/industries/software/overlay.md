# Software addendum — CLD

## Additional concepts

- **ProductLandingZone** — A landing zone dedicated to one product edition.

## Additional relationships

- ProductLandingZone landsProductEdition ProductEdition (many-to-one)

## Additional roles

- **Product Cloud Architect** — Owns the landing zone for a product edition. Bearer: person. Permissions: LandingZone:read, LandingZone:write, CloudEnvironment:read.

## Regulatory notes

- Landing-zone changes that affect production should preserve the account, region, and guardrail version in effect.
