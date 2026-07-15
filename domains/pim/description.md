# PIM — Product Information Management

A Product Information Management system maintains product attributes, categories, catalogs, and
channel publications so merchandising teams publish accurate product data everywhere it is sold.

Industry overlays specialize this domain for vertical terminology and regulatory constraints without forking the base model.

## Concepts

- **Product** — a sellable item whose descriptive information is enriched and published to channels.
- **Attribute** — a named descriptive property (such as colour, size, or material) that enriches a Product.
- **Category** — a node in the merchandising classification tree that Products are assigned to.
- **Variant** — a sellable variation of a Product distinguished by option values such as size or colour.
- **Catalog** — a curated collection of Products assembled for a channel or audience.
- **Publication** — the act of releasing a Catalog to a sales channel at a point in time.

## Taxonomy

- Variant is a kind of Product.
- Category is a kind of ClassificationNode.
- Publication is a kind of ReleaseEvent.

## Relationships

- Product describedByAttribute Attribute (many-to-many)
- Product classifiedInCategory Category (many-to-many)
- Variant variantOfProduct Product (many-to-one)
- Catalog aggregatesProduct Product (many-to-many)
- Publication publishesCatalog Catalog (many-to-one)

## Attributes

- Product: productName (string), sku (string), productStatus (string)
- Attribute: attributeName (string), attributeType (string), attributeValue (string)
- Category: categoryName (string), categoryPath (string)
- Variant: variantSku (string), optionValues (string)
- Catalog: catalogName (string), channel (string)
- Publication: publishedAt (dateTime), targetChannel (string)

## Lifecycle

- Product: draft → enriched → approved → published

## Roles

- **MerchandiserRole** (bearer: person) — creates products, assigns categories, assembles catalogs, and publishes to channels; permissions: Product:read, Product:write, Catalog:read, Catalog:write, Publication:read, Publication:write
- **DataStewardRole** (bearer: person) — defines attributes, enforces data quality, and approves enriched product data; permissions: Attribute:read, Attribute:write, Product:read, Product:write, Category:read

## Primary workflow

Create product → enrich attributes → assign category → publish to catalog channel
