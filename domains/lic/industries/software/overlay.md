# Software addendum — LIC

## Additional concepts

- **SaaSLicenseAgreement** — A license agreement for a software tenant on a product edition.

## Additional relationships

- SaaSLicenseAgreement coversSoftwareTenant SoftwareTenant (many-to-one)
- SaaSLicenseAgreement licensesProductEdition ProductEdition (many-to-one)

## Additional roles

- **SaaS License Administrator** — Issues tenant license agreements. Bearer: person. Permissions: LicenseAgreement:read, LicenseAgreement:write, Entitlement:read, Entitlement:write.

## Regulatory notes

- Entitlement changes should retain the product edition and license agreement version used at decision time.
