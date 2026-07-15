# Healthcare addendum — HEALTH

## Additional concepts

- **EncounterRecord** — A clinical encounter (visit, admission, telehealth) in the EHR.
- **ConsentDirective** — Patient consent for treatment or data sharing, scoped and revocable.
- **ProblemListEntry** — An active or historical problem on the patient problem list.

## Additional relationships

- EncounterRecord relatesToContext within the HEALTH base model (many-to-one).
- ConsentDirective is recordedAgainst operational records in this domain (many-to-one).

## Additional roles

- **Health Records Officer** — Maintains encounter documentation integrity and consent directives.

## Regulatory notes

- Consent must be checked before data sharing workflows.
- Clinical corrections are amendments — never silent overwrites of encounter content.
