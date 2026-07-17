# Telco addendum — NUM

## Additional concepts

- **TelcoNumberAssignment** — An assignment connecting MVNO identifiers to a telco service identity.
- **DonorNetworkRecord** — A record of the network donating a number during a port-in.

## Additional relationships

- TelcoNumberAssignment assignedToSubscriber Subscriber (many-to-one)

## Additional roles

- **Porting Desk** — Person role that coordinates MVNO port-in and port-out cases with network operators. Bearer: person. Permissions: PortingRequest:read, PortingRequest:write, MobileNumber:read.

## Regulatory notes

- Identifier, subscriber, usage, and service associations retain effective dates and source-system provenance where required for audit.
- Personally identifiable and communications data are accessed according to applicable privacy, retention, and lawful-process controls.