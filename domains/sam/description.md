# SAM — Service Assurance Management

Monitors service alarms and performance, detects degradation and outages, assesses customer impact, and records SLA violations.

## Concepts

- **ServiceAlarm** — A notification that a monitored service condition requires attention.
- **PerformanceMetric** — A measured value describing service behavior or quality.
- **Threshold** — A boundary that determines when a metric indicates an abnormal condition.
- **ServiceDegradation** — A reduction in service quality that does not necessarily constitute a total outage.
- **Outage** — A period during which a service is unavailable.
- **CustomerImpact** — An assessment of customers or services affected by degradation or outage.
- **SLAViolation** — A failure to meet a committed service-level target.
- **AssuranceCase** — A managed operational case grouping assurance observations and actions.

## Taxonomy

- Outage is a kind of Service degradation.
- SLAViolation is a kind of Assurance exception.
- ServiceAlarm is a kind of Assurance observation.

## Relationships

- PerformanceMetric evaluatedAgainstThreshold Threshold (many-to-many)
- Threshold raisesServiceAlarm ServiceAlarm (one-to-many)
- ServiceAlarm indicatesServiceDegradation ServiceDegradation (many-to-one)
- Outage causesCustomerImpact CustomerImpact (one-to-many)
- ServiceDegradation causesCustomerImpact CustomerImpact (one-to-many)
- SLAViolation resultsFromOutage Outage (many-to-one)
- AssuranceCase groupsServiceAlarm ServiceAlarm (one-to-many)

## Attributes

- ServiceAlarm: serviceAlarmId (string)
- PerformanceMetric: performanceMetricId (string)
- Threshold: thresholdId (string)
- ServiceDegradation: serviceDegradationId (string)
- Outage: outageId (string)
- CustomerImpact: customerImpactId (string)
- SLAViolation: sLAViolationId (string)
- AssuranceCase: assuranceCaseId (string)

## Lifecycle

- ServiceAlarm: raised → acknowledged → correlated → cleared → escalated

## Roles

- **Service Assurance Analyst** (bearer: person) — monitors service quality and correlates alarms into customer impact; permissions: ServiceAlarm:read, ServiceAlarm:write, PerformanceMetric:read, CustomerImpact:read, AssuranceCase:write.

## Primary workflow

Collect metric → evaluate threshold → raise alarm → correlate degradation → assess customer impact → clear or escalate