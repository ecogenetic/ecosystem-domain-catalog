# DBS — Database and Data Store Management

Governs data stores, schemas, database instances, backup policies, access grants, and the data products those stores serve.

## Concepts

- **DataStore** — A logical store of software data, such as a database, cache, or object collection.
- **DatabaseSchema** — The versioned structure that defines a data store.
- **DatabaseInstance** — A running database that hosts a schema. Distinct from a physical asset and from a product.
- **BackupPolicy** — The rule for how a database instance is backed up and restored.
- **AccessGrant** — A permission for a subject to use a data store.
- **DataProduct** — A governed data set served from a data store for other teams or products to consume.

## Taxonomy

- DatabaseInstance is a kind of Running store.
- DatabaseSchema is a kind of Store definition.
- DataProduct is a kind of Governed data.

## Relationships

- DatabaseSchema definesDataStore DataStore (many-to-one)
- DatabaseInstance hostsDatabaseSchema DatabaseSchema (many-to-one)
- BackupPolicy protectsDatabaseInstance DatabaseInstance (many-to-one)
- AccessGrant grantsDataStore DataStore (many-to-one)
- DataProduct servedByDataStore DataStore (many-to-one)

## Attributes

- DataStore: dataStoreId (string), storeName (string), environmentCode (string)
- DatabaseSchema: databaseSchemaId (string), schemaName (string)
- DatabaseInstance: databaseInstanceId (string), databaseInstanceStatus (string), instanceName (string), hostReference (string)
- BackupPolicy: backupPolicyId (string), retentionDays (integer)
- AccessGrant: accessGrantId (string), subjectReference (string), accessPurpose (string)
- DataProduct: dataProductId (string), dataProductName (string)

## Lifecycle

- DatabaseInstance: provisioned → online → maintenance → retired

## Roles

- **Data Platform Owner** (bearer: person) — owns data stores, schemas, backup policy, and access grants; permissions: DataStore:read, DataStore:write, DatabaseInstance:read, DatabaseInstance:write, AccessGrant:read, AccessGrant:write

## Primary workflow

Define data store → publish schema → provision instance → apply backup policy → grant access → retire
