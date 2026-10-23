# Software addendum — BI

## Additional concepts

- **ProductUsageMetric** — A metric of product adoption, usage, or reliability.
- **AdoptionDashboard** — A dashboard that displays product usage metrics.

## Additional relationships

- AdoptionDashboard displaysProductUsageMetric ProductUsageMetric (one-to-many)

## Additional roles

- **Product Analyst** — Defines product usage metrics and adoption dashboards. Bearer: person. Permissions: Metric:read, Metric:write, Dashboard:read, Dashboard:write.

## Regulatory notes

- Product metrics should name the product edition and the time window they measure.
