# Telco addendum — CVM

CVM is the revenue engine of a telco: base management campaigns drive ARPU growth, bundle
uptake, and churn prevention across a high-volume, event-driven subscriber base. Value is
managed per subscriber (SIM/line), not just per paying customer, and usage events are the
primary scoring signal.

## Additional concepts

- **Subscriber** — the service identity (per SIM/line, identified by MSISDN) whose usage, spend, and churn risk are managed; a Customer may hold several.
- **RatePlan** — the telco tariff a subscriber is on; the central pricing construct that CVM migrations and save offers act upon.
- **Bundle** — a packaged allowance (data, voice, SMS) sold on top of or within a rate plan; the most common CVM offer payload.
- **UsageRecord** — an aggregated usage event (data session, call, recharge, top-up) that feeds value and churn scoring.
- **ARPUBand** — the average-revenue-per-user band a subscriber falls into, used for segmentation and campaign targeting.

## Additional relationships

- Subscriber belongsToCustomer Customer (many-to-one); a customer can hold multiple SIMs/lines.
- Subscriber currentlyOnRatePlan RatePlan (many-to-one); plan migrations are a core CVM treatment.
- Bundle soldWithRatePlan RatePlan (many-to-many); bundle uptake offers target subscribers, not customers.
- UsageRecord usageOfSubscriber Subscriber (many-to-one); usage decay is the leading churn signal.
- Subscriber classifiedInArpuBand ARPUBand (many-to-one); band transitions trigger up-sell or save campaigns.
- Offers promote Bundles or RatePlan migrations; next best action ranks recharge, bundle, migration, and retention offers per subscriber.

## Additional roles

- **BaseManagerRole** (bearer: person) — owns the subscriber base plan: monitors ARPU bands, usage decay, and churn cohorts, and commissions campaigns; permissions: Subscriber:read, ARPUBand:read, UsageRecord:read, Campaign:read, Campaign:write, Segment:read

## Industry notes

- Prepaid vs postpaid drives different value logic: prepaid value is recharge-frequency based (days-since-last-recharge is the key churn signal); postpaid value is contract and bill based.
- Consent rules are per channel (opt-in/opt-out for SMS vs voice vs app push) — treatments must check channel consent, not just global marketing consent.
- Campaign volumes are large (millions of treatments); control groups and suppression rules (recently contacted, complaint open, collections status) are mandatory practice.
- Number portability makes churn observable and hard to reverse — save offers are triggered on port-out request events where regulation permits.
