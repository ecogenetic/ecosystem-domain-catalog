# Software addendum — ITSM

## Additional concepts

- **ProductionIncident** — An incident affecting a production software service.
- **SoftwareConfigurationItem** — A configuration item that represents a deployed software component.

## Additional relationships

- ProductionIncident affectsSoftwareConfigurationItem SoftwareConfigurationItem (many-to-many)

## Additional roles

- **Software Change Manager** — Approves changes to production software configuration items. Bearer: person. Permissions: Incident:read, ChangeRequest:read, ChangeRequest:write, ConfigurationItem:read.

## Regulatory notes

- A production incident should correlate to the service instance and the deployment that was current, without copying their state.
