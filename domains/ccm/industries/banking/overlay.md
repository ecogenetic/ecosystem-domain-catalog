# Banking addendum — Credit & Collections

## Additional concepts

- **CreditFacility** — a formal lending arrangement (overdraft, term loan, revolver) with limit, tenor, and covenants; specializes CreditLimit.
- **Covenant** — a condition on a facility whose breach triggers credit review.
- **ProvisionEntry** — expected-credit-loss recognised against an exposure (stage 1/2/3).

## Additional relationships

- CreditFacility is granted to one banking Party (1..1); Covenants attach to facilities (0..*).
- ProvisionEntry covers one CreditExposure (1..1) and carries an impairment stage.

## Additional roles

- **Credit Committee Member** — approves facilities above delegated limits; the approver in maker-checker flows.

## Regulatory notes

- Facility approval and limit changes require maker-checker (four-eyes); generated approval workflows must separate proposer and approver.
- Exposures must be staged for expected-credit-loss provisioning and re-staged on arrears events.
- Collections activity on regulated retail customers must respect treating-customers-fairly rules (contact frequency, hardship processes).
