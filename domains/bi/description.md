# BI — Business Intelligence & Analytics

A Business Intelligence & Analytics system defines datasets, metrics, dashboards, and reports
for decision-makers so leaders monitor KPIs continuously instead of waiting for ad hoc analysis.

## Concepts

- **Dashboard** — an interactive collection of visualizations that presents metrics at a glance.
- **Report** — a scheduled or on-demand document that presents metrics for a defined audience.
- **Metric** — a computed measure derived from a dataset, such as revenue or conversion rate.
- **Dataset** — a modeled collection of records that feeds metrics and can be sliced by dimensions.
- **Dimension** — a categorical attribute, such as region or product line, used to slice datasets.
- **KPI** — a key performance indicator that sets a target value against a metric.

## Taxonomy

- KPI is a kind of Metric.
- Dashboard is a kind of AnalyticalView.
- Report is a kind of AnalyticalDocument.

## Relationships

- Dataset slicedByDimension Dimension (many-to-many)
- Dataset feedsMetric Metric (one-to-many)
- Dashboard visualizesMetric Metric (many-to-many)
- Report presentsMetric Metric (many-to-many)
- KPI targetsMetric Metric (many-to-one)

## Attributes

- Dashboard: dashboardName (string), refreshIntervalMinutes (integer)
- Report: reportName (string), schedule (string), reportStatus (string)
- Metric: metricName (string), aggregationType (string)
- Dataset: datasetName (string), rowCount (integer), lastRefreshedAt (dateTime)
- Dimension: dimensionName (string), hierarchyLevel (integer)
- KPI: targetValue (decimal), thresholdDirection (string)

## Lifecycle

- Report: defined → scheduled → refreshed → archived

## Roles

- **AnalystRole** (bearer: person) — models datasets, defines metrics and KPIs, builds dashboards and reports; permissions: Dataset:read, Dataset:write, Metric:read, Metric:write, Dashboard:read, Dashboard:write, Report:read, Report:write
- **ViewerRole** (bearer: person) — consumes shared dashboards and reports to monitor KPIs; permissions: Dashboard:read, Report:read, KPI:read, Metric:read

## Primary workflow

Model dataset → define metric → build dashboard → share report → refresh on schedule
