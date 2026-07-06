# ITSM — IT Service Management

An IT Service Management system logs incidents, manages changes, tracks configuration items,
and meets SLAs so IT support restores service quickly with a traceable change history.

## Concepts

- **Incident** — an unplanned interruption or degradation of an IT service reported for restoration.
- **ChangeRequest** — a proposed modification to configuration items, assessed for risk and approved before execution.
- **Service** — an IT capability delivered to users, such as email or the payroll application.
- **ConfigurationItem** — a tracked infrastructure or software component that supports one or more services.
- **Problem** — the underlying root cause identified across one or more related incidents.
- **SLA** — a service level agreement defining response and resolution time commitments.

## Taxonomy

- Incident is a kind of ServiceEvent.
- ChangeRequest is a kind of ServiceRequest.
- ConfigurationItem is a kind of Asset.

## Relationships

- ConfigurationItem supportsService Service (many-to-many)
- Incident affectsService Service (many-to-one)
- Incident linkedToConfigurationItem ConfigurationItem (many-to-one)
- Problem groupsIncident Incident (one-to-many)
- ChangeRequest modifiesConfigurationItem ConfigurationItem (many-to-many)
- SLA constrainsIncident Incident (one-to-many)

## Attributes

- Incident: incidentNumber (string), priority (string), loggedAt (dateTime), incidentStatus (string)
- ChangeRequest: changeSummary (string), riskLevel (string)
- Service: serviceName (string), criticality (string)
- ConfigurationItem: ciName (string), ciType (string)
- Problem: rootCause (string), identifiedAt (dateTime)
- SLA: responseTimeMinutes (integer), resolutionTimeMinutes (integer)

## Lifecycle

- Incident: logged → in progress → resolved → closed

## Roles

- **ServiceDeskAgentRole** (bearer: person) — logs incidents, diagnoses issues, links configuration items, resolves and closes tickets; permissions: Incident:read, Incident:write, Service:read, ConfigurationItem:read, SLA:read
- **ChangeManagerRole** (bearer: person) — assesses change risk, approves change requests, tracks problem root causes; permissions: ChangeRequest:read, ChangeRequest:write, ConfigurationItem:read, ConfigurationItem:write, Problem:read, Problem:write

## Primary workflow

Log incident → diagnose → link configuration item → resolve → close with SLA met
