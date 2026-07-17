# SIV — Service Catalog and Inventory Management

Defines technical service specifications and records live service instances, components, dependencies, resources, and product mappings.

## Concepts

- **ServiceSpecification** — A reusable technical definition of how a service is realized.
- **ServiceOffering** — A service specification made available for operational fulfilment.
- **ServiceInstance** — A deployed occurrence of a service delivered to a customer or service line.
- **ServiceComponent** — A constituent functional part of a service instance.
- **ServiceDependency** — A directed dependency between service specifications or instances.
- **ResourceReference** — A reference to a logical or physical resource used by a service.
- **ProductServiceMapping** — A mapping from a commercial product to one or more technical services.
- **ServiceInventory** — The governed collection of current and historical service instances.

## Taxonomy

- ServiceInstance is a kind of Operational service.
- ServiceComponent is a kind of Operational service.
- ServiceOffering is a kind of Catalog entry.

## Relationships

- ServiceOffering basedOnSpecification ServiceSpecification (many-to-one)
- ServiceInstance realizesSpecification ServiceSpecification (many-to-one)
- ServiceInstance containsServiceComponent ServiceComponent (one-to-many)
- ServiceDependency dependsOnServiceInstance ServiceInstance (many-to-one)
- ServiceInstance usesResourceReference ResourceReference (many-to-many)
- ProductServiceMapping mapsToServiceSpecification ServiceSpecification (many-to-one)
- ServiceInventory recordsServiceInstance ServiceInstance (one-to-many)

## Attributes

- ServiceSpecification: serviceSpecificationId (string)
- ServiceOffering: serviceOfferingId (string)
- ServiceInstance: serviceInstanceId (string)
- ServiceComponent: serviceComponentId (string)
- ServiceDependency: serviceDependencyId (string)
- ResourceReference: resourceReferenceId (string)
- ProductServiceMapping: productServiceMappingId (string)
- ServiceInventory: serviceInventoryId (string)

## Lifecycle

- ServiceInstance: designed → reserved → active → suspended → retired

## Roles

- **Service Inventory Manager** (bearer: person) — curates service definitions and governs deployed service records; permissions: ServiceSpecification:read, ServiceSpecification:write, ServiceInstance:read, ServiceInstance:write, ServiceInventory:read.

## Primary workflow

Define service specification → publish service offering → map product → reserve resources → activate service instance → retire