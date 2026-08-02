# Gaming & Gambling addendum — CRM

In a licensed gambling operator, CRM is player relationship management: acquiring players through
affiliates and campaigns, verifying age and identity before any real-money relationship, managing
VIP relationships through hosts, and resolving player complaints — with responsible-gambling status
gating every piece of outreach.

## Additional concepts

- **Player** — a Person who is a registered, age-verified account holder; the primary relationship unit.
- **AffiliatePartner** — an Organisation representing an affiliate or media partner that refers new players for commission.
- **PlayerRelationship** — a CustomerRelationship connecting an age-verified player to the licensed operator and governing outreach eligibility.
- **VIPTier** — a named level in the VIP programme (e.g. bronze, silver, gold, host-managed) that determines relationship treatment.
- **SaferGamblingStatus** — the player's current responsible-gambling state (active limits, cool-off, self-excluded); gates all outreach and offers.
- **PlayerComplaint** — a Case raised by a player, including regulatory complaints that carry statutory response deadlines.

## Additional relationships

- PlayerRelationship relatesToPlayer Player (many-to-one).
- Player carriesSaferGamblingStatus SaferGamblingStatus (one-to-one); outreach must check status before any campaign, activity, or offer.
- Player assignedToVipTier VIPTier (many-to-one); tier changes drive host assignment and treatment level.
- Lead referredByAffiliate AffiliatePartner (many-to-one); affiliate attribution is tracked from first touch for commission and compliance.
- PlayerComplaint raisedByPlayer Player (many-to-one); regulatory complaints have statutory SLA deadlines (use the base Case slaDueAt).
- VIP opportunities (reactivation, tier upgrade) follow the base Opportunity flow, owned by a VIP host.

## Additional roles

- **VIPHostRole** (bearer: person) — owns high-value player relationships: manages tier treatment, logs interactions, and opens reactivation opportunities; permissions: Player:read, Player:write, VIPTier:read, Opportunity:read, Opportunity:write, Activity:read, Activity:write, SaferGamblingStatus:read
- **SaferGamblingOfficerRole** (bearer: person) — reviews at-risk players, applies status changes, and audits that outreach respected suppression rules; permissions: SaferGamblingStatus:read, SaferGamblingStatus:write, Player:read, Campaign:read, Activity:read

## Regulatory notes

- Age and identity verification is mandatory before real-money play: the Player record must be verified before any opportunity or campaign treatment targets it.
- Marketing to self-excluded or cooled-off players is prohibited; campaign audience selection must exclude players whose SaferGamblingStatus is not clear, and the exclusion must be auditable.
- VIP treatment is regulated: affordability and source-of-funds checks gate VIP tier upgrades in many jurisdictions.
- Regulatory complaints have statutory response deadlines — model them as Cases with slaDueAt set and escalation tracked.
