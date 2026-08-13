# Banking addendum — EAM

## Additional concepts
- **ATMAsset** — an Asset representing an automated teller machine or self-service banking device.
- **BranchTechnologyAsset** — an Asset supporting branch operations such as teller, queue, security, or cash-handling equipment.
- **CriticalBankingAsset** — an Asset whose loss can materially disrupt a critical banking service.

## Additional relationships
- ATMAsset installedAtBankLocation Location (many-to-one)
- CriticalBankingAsset supportsCriticalService ServiceReference (many-to-many)

## Additional roles
- **Bank Asset Manager** — governs ATM, branch, and other critical physical banking assets and maintenance plans.

## Regulatory notes
- Critical assets should retain ownership, location, maintenance, outage, and recovery evidence.
- ATM and branch technology maintenance should correlate with service-impact and incident records.
