# Insurance addendum — CVM

In insurance, CVM concentrates on the renewal moment: lapse propensity replaces churn, renewal
pricing is optimised within conduct and fairness constraints, and cross-sell bundles cover lines
(home + motor + life) across the household. Value is managed per policyholder and household, and
claims history shapes both value and retention risk.

## Additional concepts

- **Policyholder** — the customer who owns one or more policies; the unit whose lifetime value and lapse risk are managed.
- **PolicyHolding** — one in-force policy (motor, home, life, health) held by a policyholder; the unit renewal and cross-sell act on.
- **RenewalEvent** — the approaching renewal of a policy holding: the decisive CVM moment where lapse risk peaks and pricing is decided.
- **LapseRisk** — a computed probability that the policyholder lets a policy lapse or switches insurer at renewal.
- **RenewalPriceDecision** — the premium decision for a renewal (proposed premium, prior premium, concession applied) subject to fairness rules.
- **Household** — the grouping of policyholders at one address whose combined holdings drive bundle offers and multi-policy discounts.

## Additional relationships

- Policyholder extendsCustomer (subclass of Customer); household membership links policyholders for bundle targeting.
- PolicyHolding heldByPolicyholder Policyholder (many-to-one); holdings per household drive multi-policy discount eligibility.
- RenewalEvent renewsPolicyHolding PolicyHolding (many-to-one); renewal windows trigger retention campaigns and price decisions.
- LapseRisk assessesLapseOfPolicyholder Policyholder (many-to-one); a specialisation of churn scoring computed per renewal.
- RenewalPriceDecision pricesRenewalEvent RenewalEvent (one-to-one); concessions above threshold require documented reasons.
- Policyholder memberOfHousehold Household (many-to-one); cross-sell offers promote covering uninsured lines in the household.

## Additional roles

- **RenewalPricingAnalystRole** (bearer: person) — sets renewal price decisions within fairness constraints and monitors lapse-price elasticity; permissions: RenewalPriceDecision:read, RenewalPriceDecision:write, RenewalEvent:read, LapseRisk:read, PolicyHolding:read, Policyholder:read

## Industry notes

- Renewal is the retention event: most lapse happens at renewal, so campaigns, price decisions, and save treatments are scheduled around the renewal window, not spread across the year.
- Price-walking rules (e.g. FCA fairness reforms) prohibit charging renewing customers more than equivalent new customers — renewal price decisions must be justifiable and auditable.
- Claims history cuts both ways: a well-handled claim increases loyalty; a repudiated or slow claim is the strongest lapse predictor after price.
- Cross-sell is household-shaped: multi-policy discounts (home + motor) are the dominant bundle mechanic, so household composition matters more than individual propensity alone.
- Health and claims data used in targeting is sensitive; consent and data-minimisation rules constrain which signals models may use.
