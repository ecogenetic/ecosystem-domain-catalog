# Telco addendum — E-Commerce

A telco online store sells a mix that plain retail does not: physical devices (phones, routers),
SIM cards that must be registered before activation, and instantly provisioned digital products —
data bundles, airtime, and contract plans. One order often combines all three (device + SIM + plan),
so order lines fulfil differently: the device ships, the SIM activates after registration, and the
bundle or plan provisions to an MSISDN on the network within seconds.

## Additional concepts

- **Device** — a Product that is a physical handset, router, or accessory, tracked by IMEI and shipped like retail goods.
- **SIMCard** — a Product (physical or eSIM) that carries an ICCID and must pass subscriber registration (e.g. RICA/KYC) before activation.
- **DataBundle** — a digital Product of a data allowance with a validity period, provisioned to an MSISDN immediately after payment.
- **AirtimeTopUp** — a digital Product crediting prepaid airtime to an MSISDN immediately after payment.
- **ContractPlan** — a subscription Product committing the customer to a monthly tariff over a term; requires a credit check before activation.
- **ProvisioningRequest** — a Fulfilment that activates a digital product (bundle, airtime, plan, SIM) on the network against an MSISDN.
- **CreditCheck** — the credit assessment gating contract-plan and device-financing orders.

## Additional relationships

- ProvisioningRequest provisionsToMsisdn (the target mobile number) — digital order lines fulfil by provisioning, not shipping.
- CreditCheck assessesOrder Order (one-to-one); a contract-plan order must not activate until the credit check passes.
- SIMCard activation is gated on subscriber registration; the SIM ships (or eSIM delivers digitally) but stays inactive until registered.
- Mixed carts split fulfilment: Device lines ship with tracking, SIMCard lines await registration, DataBundle/AirtimeTopUp/ContractPlan lines raise ProvisioningRequests.

## Additional roles

- **ProvisioningOperatorRole** (bearer: person) — monitors and retries failed network provisioning requests; permissions: ProvisioningRequest:read, ProvisioningRequest:write, Order:read, Product:read
- **TelcoStoreManagerRole** (bearer: person) — manages the device/SIM/bundle catalog, pricing, and promotions; permissions: Product:read, Product:write, Promotion:read, Promotion:write, Order:read, CreditCheck:read

## Regulatory notes

- Subscriber registration (RICA, KYC, or equivalent) is a legal precondition for SIM activation: generated workflows must include a registration gate between SIM purchase and activation.
- Credit checks are mandatory before contract-plan activation and device financing; declined checks must cancel or downgrade the order line, never silently activate.
- Provisioning is transactional: a paid bundle that fails to provision must auto-retry and refund on final failure — never leave the customer paid but unprovisioned.
- Prepaid airtime and data purchases are usually irrevocable once provisioned; refund policies must distinguish provisioned digital goods from shipped goods.
