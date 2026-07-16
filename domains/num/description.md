# NUM — Number, SIM and Portability Management

Manages mobile-number pools, SIM and eSIM profiles, identifier assignments, and number-portability history.

## Concepts

- **NumberPool** — A governed collection of mobile numbers available for allocation.
- **MobileNumber** — A mobile service number that can be allocated and ported.
- **SIMProfile** — The logical subscriber identity profile carried by a physical SIM or eSIM.
- **PhysicalSIM** — A removable physical card capable of carrying a SIM profile.
- **ESIMProfile** — A downloadable embedded-SIM profile provisioned to compatible equipment.
- **IdentifierAssignment** — A time-bounded association between mobile identifiers and a service.
- **PortingRequest** — A request to transfer a mobile number between providers.
- **PortingEvent** — An auditable event occurring during a number-portability process.

## Taxonomy

- PhysicalSIM is a kind of SIM carrier.
- ESIMProfile is a kind of SIM profile.
- PortingEvent is a kind of Identifier event.

## Relationships

- NumberPool containsMobileNumber MobileNumber (one-to-many)
- IdentifierAssignment assignsMobileNumber MobileNumber (many-to-one)
- IdentifierAssignment assignsSIMProfile SIMProfile (many-to-one)
- PhysicalSIM carriesSIMProfile SIMProfile (one-to-one)
- PortingRequest transfersMobileNumber MobileNumber (many-to-one)
- PortingRequest producesPortingEvent PortingEvent (one-to-many)

## Attributes

- NumberPool: numberPoolId (string)
- MobileNumber: mobileNumberId (string)
- SIMProfile: sIMProfileId (string)
- PhysicalSIM: physicalSIMId (string)
- ESIMProfile: eSIMProfileId (string)
- IdentifierAssignment: identifierAssignmentId (string)
- PortingRequest: portingRequestId (string)
- PortingEvent: portingEventId (string)

## Lifecycle

- PortingRequest: requested → validated → scheduled → completed → rejected → cancelled

## Roles

- **Number Portability Operator** (bearer: person) — validates identifier assignments and coordinates number transfers; permissions: NumberPool:read, MobileNumber:read, IdentifierAssignment:write, PortingRequest:read, PortingRequest:write.

## Primary workflow

Load number pool → register SIM profile → assign identifiers → validate port request → schedule transfer → complete port