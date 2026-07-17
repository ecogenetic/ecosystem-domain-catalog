# PRV — Provisioning and Activation Management

Converts approved service orders into validated activation, configuration, modification, and deactivation tasks across delivery systems.

## Concepts

- **ServiceOrder** — An approved instruction to create, modify, suspend, or cease a service.
- **ProvisioningRequest** — A request to execute a defined service configuration change.
- **ProvisioningTask** — An atomic unit of provisioning work assigned to a system or operator.
- **Activation** — The successful enablement of a requested service capability.
- **ConfigurationChange** — A controlled modification to an existing service configuration.
- **NetworkAdapter** — An integration endpoint that translates provisioning tasks for a target platform.
- **ProvisioningError** — A recorded technical or business failure during provisioning.
- **FalloutCase** — A managed case grouping failed tasks requiring recovery or manual intervention.

## Taxonomy

- Activation is a kind of Provisioning outcome.
- ConfigurationChange is a kind of Provisioning outcome.
- ProvisioningError is a kind of Provisioning outcome.

## Relationships

- ServiceOrder containsProvisioningRequest ProvisioningRequest (one-to-many)
- ProvisioningRequest createsProvisioningTask ProvisioningTask (one-to-many)
- ProvisioningTask usesNetworkAdapter NetworkAdapter (many-to-one)
- Activation completesProvisioningRequest ProvisioningRequest (one-to-one)
- ConfigurationChange implementsProvisioningRequest ProvisioningRequest (many-to-one)
- ProvisioningError failsProvisioningTask ProvisioningTask (many-to-one)
- FalloutCase groupsProvisioningError ProvisioningError (one-to-many)

## Attributes

- ServiceOrder: serviceOrderId (string)
- ProvisioningRequest: provisioningRequestId (string)
- ProvisioningTask: provisioningTaskId (string)
- Activation: activationId (string)
- ConfigurationChange: configurationChangeId (string)
- NetworkAdapter: networkAdapterId (string)
- ProvisioningError: provisioningErrorId (string)
- FalloutCase: falloutCaseId (string)

## Lifecycle

- ProvisioningRequest: received → validated → in_progress → completed → failed → cancelled

## Roles

- **Provisioning Operator** (bearer: person) — monitors provisioning tasks and recovers failed requests; permissions: ServiceOrder:read, ProvisioningRequest:read, ProvisioningRequest:write, ProvisioningTask:read, FalloutCase:write.

## Primary workflow

Receive service order → validate request → create tasks → execute adapters → confirm activation → resolve fallout