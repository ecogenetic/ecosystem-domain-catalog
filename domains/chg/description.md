# CHG — Charging and Balance Management

Rates service usage, applies charges, consumes allowances, and maintains real-time and periodic balances.

## Concepts

- **ChargingAccount** — An account that holds monetary and non-monetary balances for charging.
- **Balance** — A quantity of value available to or owed by a charging account.
- **Allowance** — A non-cash entitlement to consume a defined quantity of service.
- **RatingRule** — A tariff rule converting measured usage into a rated amount.
- **RatedUsage** — The result of applying a rating rule to a usage record.
- **Charge** — A monetary or entitlement impact applied to a charging account.
- **BalanceReservation** — A temporary hold on balance while a service session is in progress.

## Taxonomy

- Allowance is a kind of Balance.
- BalanceReservation is a kind of Balance control.
- Charge is a kind of Charging result.

## Relationships

- ChargingAccount holdsBalance Balance (one-to-many)
- ChargingAccount grantsAllowance Allowance (one-to-many)
- RatingRule producesRatedUsage RatedUsage (one-to-many)
- RatedUsage producesCharge Charge (one-to-many)
- Charge appliesToChargingAccount ChargingAccount (many-to-one)
- BalanceReservation reservesBalance Balance (many-to-one)

## Attributes

- ChargingAccount: chargingAccountId (string)
- Balance: balanceId (string)
- Allowance: allowanceId (string)
- RatingRule: ratingRuleId (string)
- RatedUsage: ratedUsageId (string)
- Charge: chargeId (string)
- BalanceReservation: balanceReservationId (string)

## Lifecycle

- Charge: received → rated → applied → rejected → reversed

## Roles

- **Charging Operations** (bearer: person) — maintains rating rules and resolves charging exceptions; permissions: ChargingAccount:read, Balance:read, RatingRule:read, RatingRule:write, Charge:read, Charge:write.

## Primary workflow

Receive mediated usage → select rating rule → calculate rated usage → reserve balance → apply charge → update allowance