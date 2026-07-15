# Banking addendum — OMS

## Additional concepts

- **ChannelOrder** — An order placed via a banking digital or branch channel for a product or VAS.
- **FulfilmentHold** — A hold preventing fulfilment until KYC or risk checks clear.
- **AccountCreditFulfilment** — Fulfilment that credits a customer account rather than shipping goods.

## Additional relationships

- ChannelOrder relatesToContext within the OMS base model (many-to-one).
- FulfilmentHold is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Channel Order Operations** — Clears fulfilment holds and monitors channel order SLAs.

## Regulatory notes

- Orders involving credit products must not fulfil until KYC/affordability gates pass.
- Account credit fulfilment requires an immutable payment/disbursement reference.
