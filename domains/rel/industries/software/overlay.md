# Software addendum — REL

## Additional concepts

- **ProductRelease** — A release of one product edition.

## Additional relationships

- ProductRelease releasesProductEdition ProductEdition (many-to-one)

## Additional roles

- **Product Release Manager** — Owns releases of a product edition. Bearer: person. Permissions: Release:read, Release:write, Deployment:read, Deployment:write.

## Regulatory notes

- A production deployment should retain the product edition, release identifier, release target, and rollback evidence.
