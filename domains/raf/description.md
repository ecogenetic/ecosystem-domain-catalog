# RAF — Revenue Assurance and Fraud Management

Defines assurance controls, reconciliations, leakage and anomaly detection, fraud alerts, investigations, and recovery actions.

## Concepts

- **AssuranceControl** — A preventive or detective control applied to a revenue-bearing process.
- **ReconciliationRule** — A rule comparing records, quantities, or monetary values across sources.
- **RevenueLeakage** — A confirmed loss or unbilled amount caused by a process or system failure.
- **UsageAnomaly** — A usage pattern that differs materially from expected behavior.
- **FraudAlert** — A risk signal indicating suspected deliberate abuse or deception.
- **Investigation** — A managed assessment of assurance exceptions or fraud alerts.
- **RecoveryAction** — An action taken to recover value or prevent further loss.
- **ControlResult** — The recorded outcome and evidence produced by an assurance control.

## Taxonomy

- FraudAlert is a kind of Risk alert.
- UsageAnomaly is a kind of Assurance exception.
- RevenueLeakage is a kind of Assurance exception.

## Relationships

- AssuranceControl usesReconciliationRule ReconciliationRule (one-to-many)
- AssuranceControl producesControlResult ControlResult (one-to-many)
- ControlResult identifiesRevenueLeakage RevenueLeakage (one-to-many)
- UsageAnomaly raisesFraudAlert FraudAlert (one-to-many)
- Investigation examinesFraudAlert FraudAlert (many-to-many)
- Investigation examinesRevenueLeakage RevenueLeakage (many-to-many)
- RecoveryAction resolvesInvestigation Investigation (many-to-one)

## Attributes

- AssuranceControl: assuranceControlId (string)
- ReconciliationRule: reconciliationRuleId (string)
- RevenueLeakage: revenueLeakageId (string)
- UsageAnomaly: usageAnomalyId (string)
- FraudAlert: fraudAlertId (string)
- Investigation: investigationId (string)
- RecoveryAction: recoveryActionId (string)
- ControlResult: controlResultId (string)

## Lifecycle

- Investigation: opened → triaged → investigating → confirmed → dismissed → closed

## Roles

- **Revenue Assurance Analyst** (bearer: person) — runs reconciliations and investigates revenue loss and fraud; permissions: AssuranceControl:read, ControlResult:read, RevenueLeakage:read, Investigation:read, Investigation:write, RecoveryAction:write.

## Primary workflow

Execute assurance control → detect exception → raise alert → triage investigation → confirm or dismiss → recover and close