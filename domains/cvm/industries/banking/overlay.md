# Banking addendum — CVM

In banking, CVM manages relationship value across a client's whole product portfolio: next-best-product
decisioning (card upgrades, loan pre-approvals, deposit retention), attrition prevention on primary
accounts, and value-based pricing concessions — always inside conduct, affordability, and consent
constraints.

## Additional concepts

- **ClientRelationship** — the value-managed view of a client (Customer) spanning every product they hold with the bank.
- **ProductHolding** — one banking product (current account, savings, card, loan, mortgage) held by a client; the unit cross-sell and retention act on.
- **PreApprovedOffer** — an offer backed by a prior credit decision (limit, rate) that the client can accept without a new application.
- **AffordabilityCheck** — an assessment that a credit-bearing offer is affordable and suitable for the client before it may be presented.
- **AttritionSignal** — a behavioural indicator of relationship run-off (salary deposit stopped, balances migrating out, dormancy) that triggers retention action.

## Additional relationships

- ClientRelationship aggregatesCustomer Customer (one-to-one); relationship value = sum of holding values minus cost to serve.
- ProductHolding heldByClient ClientRelationship (many-to-one); propensity scores estimate the next product per relationship.
- PreApprovedOffer extendsOffer (subclass of Offer); backed by a credit decision with limit and rate; requires AffordabilityCheck before treatment.
- AffordabilityCheck validatesPreApprovedOffer PreApprovedOffer (one-to-one); failed checks suppress the treatment.
- AttritionSignal detectedOnRelationship ClientRelationship (many-to-one); high-severity signals feed churn risk and trigger save campaigns.

## Additional roles

- **RelationshipManagerRole** (bearer: person) — owns high-value client relationships; reviews next-best-action recommendations and delivers advice-led treatments; permissions: ClientRelationship:read, ProductHolding:read, NextBestAction:read, Treatment:read, Treatment:write, Customer:read

## Industry notes

- Product holdings, not transactions, are the value unit: primary-bank status (salary account + 3 or more products) is the strongest retention predictor.
- Credit-bearing offers (cards, loans, overdraft increases) must pass affordability and suitability checks before delivery — a compliance gate between next best action and treatment.
- Conduct rules (Treating Customers Fairly) prohibit value-based discrimination in essential services; pricing concessions need documented decision reasons.
- Consent and marketing preferences are per channel and per product line; suppression lists include collections status, complaints in progress, vulnerability flags, and recent bereavement.
- Four-eyes approval applies to pricing concessions above threshold; every offer decision needs an auditable trail (who, when, what, why).
