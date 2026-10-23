# Software addendum — MOB

## Additional concepts

- **ProductMobileApplication** — A mobile application that presents one product edition.

## Additional relationships

- ProductMobileApplication presentsMobileEdition ProductEdition (many-to-one)

## Additional roles

- **Product Mobile Lead** — Owns the mobile application for a product edition. Bearer: person. Permissions: MobileApplication:read, MobileApplication:write, MobileRelease:read, MobileRelease:write.

## Regulatory notes

- Store submission should retain the review outcome, device platform, and product edition of the mobile release.
