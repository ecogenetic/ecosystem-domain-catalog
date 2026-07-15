# Gaming & Gambling addendum — CMS

## Additional concepts

- **PromotionContent** — Marketing or bonus content subject to responsible-gambling and license rules.
- **JurisdictionContentFlag** — A flag restricting content publish to allowed license jurisdictions.
- **SelfExclusionSuppression** — A suppression rule preventing marketing content to self-excluded players.

## Additional relationships

- PromotionContent relatesToContext within the CMS base model (many-to-one).
- JurisdictionContentFlag is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Compliance Content Editor** — Publishes promotion content only after RG and jurisdiction checks.

## Regulatory notes

- Marketing to self-excluded players is prohibited — suppression must be enforced before publish.
- Jurisdiction flags gate which markets may see a content item.
