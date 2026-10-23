# Software addendum — UIA

## Additional concepts

- **ProductClientApplication** — A client application that presents one product edition.

## Additional relationships

- ProductClientApplication presentsProductEdition ProductEdition (many-to-one)

## Additional roles

- **Product UI Lead** — Owns the client application for a product edition. Bearer: person. Permissions: ClientApplication:read, ClientApplication:write, Screen:read, Screen:write.

## Regulatory notes

- Customer-facing screens should record the accessibility requirement they satisfy and the product edition they present.
