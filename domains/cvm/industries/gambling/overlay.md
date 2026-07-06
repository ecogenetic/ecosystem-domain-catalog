# Gambling addendum — CVM

## Additional concepts

- **Player** — the customer term in gambling; a Customer who wagers on games or bets.
- **PlayerSegment** — a Segment of players by wagering behaviour, value, and risk (casual, VIP, at-risk).
- **ResponsibleGamblingLimit** — deposit/loss/wager/session-time limits that all offers and campaigns must respect.
- **SaferGamblingFlag** — at-risk or self-exclusion marker that excludes a player from value campaigns.

## Additional relationships

- Player sets ResponsibleGamblingLimits (0..*); every Offer must be checked against active limits before send.
- SaferGamblingFlag on a Player excludes them from Campaign targeting regardless of segment or value score.

## Additional roles

- **Responsible Gambling Officer** — reviews at-risk players, applies flags, and enforces limits and exclusions.

## Regulatory notes

- Self-excluded and flagged players must be excluded from all marketing; generated campaign flows must include an exclusion check step.
- Limit changes that loosen a limit typically require a cooling-off period; tightening applies immediately.
- Wagering and bonus offers must record that limits were respected (auditable offer-limit check).
