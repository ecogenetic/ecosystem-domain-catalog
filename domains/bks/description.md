# BKS — Backend Services

Defines backend services, API contracts, endpoints, service bindings, and the consumers that call them.

## Concepts

- **BackendService** — A server-side software application that exposes behavior through an API. Distinct from a deployed service instance and from an IT service.
- **ApiContract** — The versioned contract a backend service publishes.
- **ApiEndpoint** — One operation exposed by an API contract.
- **ServiceBinding** — A binding that connects a backend service to the runtime it is offered on.
- **ApiConsumer** — A system or application permitted to call an API endpoint.

## Taxonomy

- ApiEndpoint is a kind of API operation.
- ApiContract is a kind of Service definition.
- ApiConsumer is a kind of Calling application.

## Relationships

- ApiContract specifiesBackendService BackendService (many-to-one)
- ApiEndpoint exposesApiContract ApiContract (many-to-one)
- ServiceBinding bindsBackendService BackendService (many-to-one)
- ApiConsumer consumesApiEndpoint ApiEndpoint (many-to-many)

## Attributes

- BackendService: backendServiceId (string), serviceName (string), productEditionCode (string)
- ApiContract: apiContractId (string), apiContractStatus (string), contractName (string), interfaceContractReference (string)
- ApiEndpoint: apiEndpointId (string), httpMethod (string), endpointPath (string)
- ServiceBinding: serviceBindingId (string), environmentCode (string)
- ApiConsumer: apiConsumerId (string), consumerName (string)

## Lifecycle

- ApiContract: draft → published → deprecated

## Roles

- **Backend Lead** (bearer: person) — owns backend services, API contracts, and consumer bindings; permissions: BackendService:read, BackendService:write, ApiContract:read, ApiContract:write, ApiEndpoint:read

## Primary workflow

Define backend service → draft API contract → publish endpoints → bind consumers → deprecate the contract
