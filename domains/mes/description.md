# MES — Manufacturing Execution System

A Manufacturing Execution System executes shop-floor work orders, batches, routings, and quality
checks so production supervisors see real-time status across work centers and can react to
downtime before it disrupts the schedule.

## Concepts

- **WorkOrder** — an authorised instruction to produce a quantity of product by a due date.
- **WorkCenter** — a machine, cell, or line on the shop floor where production steps are executed.
- **Batch** — a discrete quantity of product produced together under one work order.
- **Routing** — the ordered sequence of work centers and steps a product follows during production.
- **QualityCheck** — an in-process or final inspection performed against a batch.
- **Downtime** — a recorded period during which a work center is unavailable for production.

## Taxonomy

- WorkOrder is a kind of ProductionOrder.
- WorkCenter is a kind of Resource.
- QualityCheck is a kind of Inspection.

## Relationships

- WorkOrder executedAtWorkCenter WorkCenter (many-to-one)
- WorkOrder followsRouting Routing (many-to-one)
- Batch producedByWorkOrder WorkOrder (many-to-one)
- Routing sequencesWorkCenter WorkCenter (many-to-many)
- QualityCheck inspectsBatch Batch (many-to-one)
- Downtime recordedAtWorkCenter WorkCenter (many-to-one)

## Attributes

- WorkOrder: orderNumber (string), quantityPlanned (decimal), dueDate (date), workOrderStatus (string)
- WorkCenter: workCenterName (string), capacityPerHour (decimal)
- Batch: batchNumber (string), quantityProduced (decimal), startedAt (dateTime)
- Routing: routingName (string), stepCount (integer)
- QualityCheck: checkResult (string), checkedAt (dateTime)
- Downtime: downtimeReason (string), durationMinutes (decimal)

## Lifecycle

- WorkOrder: released → in progress → quality check → complete

## Roles

- **OperatorRole** (bearer: person) — starts batches at work centers, records production quantities, logs downtime; permissions: WorkOrder:read, Batch:read, Batch:write, Downtime:read, Downtime:write
- **ProductionSupervisorRole** (bearer: person) — releases work orders, monitors work-center status, reviews quality checks; permissions: WorkOrder:read, WorkOrder:write, WorkCenter:read, QualityCheck:read, Routing:read

## Primary workflow

Release work order → start batch at work center → record production → perform quality check → complete
