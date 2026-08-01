# Insurance

Life and non-life insurance: policy administration, underwriting, claims handling, broker and
agent distribution, and solvency-driven regulatory reporting. Insurance systems revolve around
long-lived contracts (policies) and event-driven liabilities (claims).

## Terminology

- Policyholder — the party who owns the policy; the insured may be a different person.
- Underwriting — risk assessment that decides acceptance and pricing of cover.
- Premium — the recurring or single payment for cover; claims draw against it.
- Claim — a demand for payment following an insured event; adjusted, then settled or repudiated.
- Broker / Agent — licensed intermediaries who distribute policies.
- Cover / Benefit — what the policy pays out, with limits and exclusions.

## Regulatory notes

- Solvency and reserving rules (e.g. Solvency II) require auditable exposure and claims data.
- Treating Customers Fairly / conduct rules apply to sales and claims workflows.
- Claims handling has statutory timelines; generated workflows should track SLA deadlines.
- Personal and health data in underwriting/claims is sensitive — consent and minimization apply.

## Business value chain

1. Design products, covers, benefits, exclusions and pricing rules.
2. Quote, assess risk, underwrite and issue a policy.
3. Collect premiums and administer endorsements, renewals and cancellations.
4. Receive loss notifications, validate cover, assess and settle claims.
5. Manage brokers, commissions, reinsurance, reserves and recoveries.
6. Monitor conduct, fraud, solvency and regulatory obligations.

## Cross-domain capability map

| Capability | Typical owning domain |
|---|---|
| Party, broker and customer relationship | CRM / PRM |
| Product, cover and quote configuration | PIM / CPQ |
| Policy and claim financial movements | FIN |
| Underwriting, claim and approval workflows | BPM |
| Fraud, compliance and investigation | RAF / GRC |
| Documents and evidence | CMS |
| Customer value and retention | CVM |

## Modeling rules

- Distinguish policyholder, insured, beneficiary, payer and claimant roles.
- Version policy terms and retain the exact version effective at the loss date.
- Model claim, claim item, reserve, payment and recovery separately.
- Record underwriting and claim decisions with inputs, rules/models, reason codes and approvers.
- Treat broker appointments, commissions and delegated authorities as dated relationships.
