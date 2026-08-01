# Telco addendum — CRM

## Additional concepts

- **Subscriber** — a Person holding one or more active service subscriptions; the primary customer term.
- **SubscriberRelationship** — a CustomerRelationship linking a subscriber to the operator across one or more subscriptions.
- **Subscription** — an active service identified by an MSISDN, billed on exactly one RatePlan.
- **RatePlan** — the tariff (charges, allowances, contract term) a subscription is billed on.

## Additional relationships

- SubscriberRelationship relates to one Subscriber (1..1) and covers Subscriptions (1..*); each Subscription is on exactly one RatePlan (1..1).
- Upsell/upgrade Opportunities link to the Subscription they would change.
- Contract end dates on subscriptions drive retention and renewal opportunity timing.

## Additional roles

- **Retention Agent** — works churn-risk subscribers with save offers; reads subscribers and subscriptions, writes opportunities.

## Industry notes

- MSISDN (mobile number) is the operational identifier customers recognise; keep it visible on subscriber views.
- Number portability (port-in/port-out) events are common workflow triggers for both acquisition and churn.
