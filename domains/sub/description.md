# SUB — Subscriber and Subscription Management

Manages customer accounts, mobile subscriptions, service lines, plan assignments, changes, suspensions, and terminations.

## Concepts

- **CustomerAccount** — A commercial account that owns and pays for one or more subscriptions.
- **Subscription** — A contracted service relationship governed by a plan and lifecycle.
- **ServiceLine** — An operational mobile service identity activated by a subscription.
- **SubscriptionPlan** — The commercial plan governing recurring service terms and entitlements.
- **SubscriptionChange** — A requested or completed modification to a subscription.
- **Suspension** — A temporary restriction of an active subscription or service line.
- **Termination** — The permanent closure of a subscription and its active services.

## Taxonomy

- ServiceLine is a kind of Subscription service.
- Suspension is a kind of Subscription change.
- Termination is a kind of Subscription change.

## Relationships

- CustomerAccount holdsSubscription Subscription (one-to-many)
- Subscription activatesServiceLine ServiceLine (one-to-many)
- Subscription usesSubscriptionPlan SubscriptionPlan (many-to-one)
- Subscription recordsSubscriptionChange SubscriptionChange (one-to-many)
- Suspension affectsSubscription Subscription (many-to-one)
- Termination closesSubscription Subscription (one-to-one)

## Attributes

- CustomerAccount: customerAccountId (string)
- Subscription: subscriptionId (string)
- ServiceLine: serviceLineId (string)
- SubscriptionPlan: subscriptionPlanId (string)
- SubscriptionChange: subscriptionChangeId (string)
- Suspension: suspensionId (string)
- Termination: terminationId (string)

## Lifecycle

- Subscription: pending → active → suspended → terminated

## Roles

- **Subscription Manager** (bearer: person) — manages subscription lifecycles and service-line changes; permissions: CustomerAccount:read, Subscription:read, Subscription:write, ServiceLine:read, ServiceLine:write.

## Primary workflow

Capture customer account → create subscription → assign plan → activate service line → manage changes → terminate