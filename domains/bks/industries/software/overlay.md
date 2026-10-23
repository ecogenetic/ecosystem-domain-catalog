# Software addendum — BKS

## Additional concepts

- **ProductBackendService** — A backend service that implements one product edition.

## Additional relationships

- ProductBackendService implementsProductEdition ProductEdition (many-to-one)

## Additional roles

- **Product Backend Lead** — Owns the backend service for a product edition. Bearer: person. Permissions: BackendService:read, BackendService:write, ApiContract:read, ApiContract:write.

## Regulatory notes

- A published API contract should name the product edition it implements and stay immutable after publication.
