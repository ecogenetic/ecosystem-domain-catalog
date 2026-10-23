# CLD — Cloud Architecture

Governs cloud accounts, landing zones, regions, network segments, cloud environments, and the shared services those environments use.

## Concepts

- **CloudAccount** — A provider administrative and billing boundary. Distinct from a customer account and from a financial account.
- **LandingZone** — A governed cloud foundation of accounts, networks, and guardrails for a product or platform.
- **CloudRegion** — A provider region in which a landing zone is placed.
- **NetworkSegment** — A network boundary inside a landing zone, such as a virtual network or subnet group.
- **CloudEnvironment** — An environment inside a landing zone, such as development, test, or production. Distinct from a release target.
- **SharedCloudService** — A platform service, such as identity or logging, offered to cloud environments.

## Taxonomy

- CloudEnvironment is a kind of Landing zone environment.
- NetworkSegment is a kind of Cloud network.
- SharedCloudService is a kind of Platform service.

## Relationships

- LandingZone hostedInCloudAccount CloudAccount (many-to-one)
- LandingZone placedInCloudRegion CloudRegion (many-to-one)
- NetworkSegment segmentsLandingZone LandingZone (many-to-one)
- CloudEnvironment usesLandingZone LandingZone (many-to-one)
- SharedCloudService servesCloudEnvironment CloudEnvironment (many-to-many)

## Attributes

- CloudAccount: cloudAccountId (string), accountName (string), providerName (string)
- LandingZone: landingZoneId (string), landingZoneStatus (string), zoneName (string)
- CloudRegion: cloudRegionId (string), regionCode (string)
- NetworkSegment: networkSegmentId (string), segmentName (string)
- CloudEnvironment: cloudEnvironmentId (string), environmentName (string), environmentCode (string)
- SharedCloudService: sharedCloudServiceId (string), serviceName (string)

## Lifecycle

- LandingZone: designed → provisioned → active → retired

## Roles

- **Cloud Architect** (bearer: person) — designs landing zones, cloud environments, and network guardrails; permissions: LandingZone:read, LandingZone:write, CloudEnvironment:read, CloudEnvironment:write, NetworkSegment:read

## Primary workflow

Open cloud account → design landing zone → place region and network → provision environment → activate shared services → retire
