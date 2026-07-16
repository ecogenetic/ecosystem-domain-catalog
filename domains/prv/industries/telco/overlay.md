# Telco addendum — PRV

## Additional concepts

- **NetworkActivation** — An activation executed against an MVNO or host-MNO network capability.
- **HostMNOAdapter** — A network adapter integrating with the host mobile network operator.

## Additional relationships

- NetworkActivation activatesSubscriber Subscriber (many-to-one)

## Additional roles

- **Activation Support** — Person role that resolves MVNO activation failures with the host network operator. Bearer: person. Permissions: ProvisioningRequest:read, ProvisioningTask:read, ProvisioningTask:write, FalloutCase:read, FalloutCase:write.

## Regulatory notes

- Identifier, subscriber, usage, and service associations retain effective dates and source-system provenance where required for audit.
- Personally identifiable and communications data are accessed according to applicable privacy, retention, and lawful-process controls.