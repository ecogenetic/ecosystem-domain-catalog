# Software addendum — DBS

## Additional concepts

- **ProductDataStore** — A data store that holds data for one product edition.

## Additional relationships

- ProductDataStore storesProductEdition ProductEdition (many-to-one)

## Additional roles

- **Product Data Owner** — Owns the data store for a product edition. Bearer: person. Permissions: DataStore:read, DataStore:write, AccessGrant:read.

## Regulatory notes

- Access grants to customer data should record the purpose and the product edition whose data is stored.
