# Banking addendum — SAM

## Additional concepts
- **DigitalBankingServiceAlarm** — a ServiceAlarm raised for mobile, web, payments, cards, or another digital banking service.
- **CustomerTransactionImpact** — a CustomerImpact describing failed, delayed, duplicated, or degraded customer transactions.
- **CriticalServiceSLOViolation** — an SLAViolation against a critical banking service objective.

## Additional relationships
- DigitalBankingServiceAlarm causesCustomerImpact CustomerTransactionImpact (one-to-many)
- CriticalServiceSLOViolation relatesToAlarm DigitalBankingServiceAlarm (many-to-one)

## Additional roles
- **Digital Banking Assurance Role** — monitors service health, customer transaction impact, and escalation into ITSM.

## Regulatory notes
- Assurance events should preserve service, channel, customer-impact, and transaction correlation identifiers.
- Material outages should feed ITSM and resilience reporting without duplicating the incident record.
