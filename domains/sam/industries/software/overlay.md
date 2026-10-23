# Software addendum — SAM

## Additional concepts

- **ApplicationAlarm** — A service alarm raised for a software application.
- **TenantImpact** — Customer impact expressed as affected software tenants.

## Additional relationships

- TenantImpact assessesApplicationAlarm ApplicationAlarm (many-to-one)
- TenantImpact affectsSoftwareTenant SoftwareTenant (many-to-one)

## Additional roles

- **Application Assurance Analyst** — Correlates application alarms to tenant impact. Bearer: person. Permissions: ServiceAlarm:read, CustomerImpact:read, CustomerImpact:write, AssuranceCase:write.

## Regulatory notes

- Tenant impact should retain the application identifier and the alarm that caused it. An alarm is not itself an incident.
