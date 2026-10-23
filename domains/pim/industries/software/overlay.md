# Software addendum — PIM

## Additional concepts

- **SoftwareEditionProduct** — A catalog product that represents a sellable software edition.
- **EditionAttribute** — An attribute that describes a software edition product, such as seat model or deployment form.

## Additional relationships

- EditionAttribute describesSoftwareEdition SoftwareEditionProduct (many-to-one)

## Additional roles

- **Software Merchandiser** — Publishes software edition products in the catalog. Bearer: person. Permissions: Product:read, Product:write, Attribute:read, Publication:write.

## Regulatory notes

- A published software edition stays immutable. Later changes create a new catalog publication.
