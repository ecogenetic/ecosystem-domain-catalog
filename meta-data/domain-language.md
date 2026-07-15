# Domain language (normative headings)

Every domain ships a `domains/{id}/description.md` with **exactly these seven sections**,
in this order, each non-empty. External products that parse or display domain language
MUST recognise these headings.

## Document skeleton

```markdown
# {ACRONYM} — {Full Name}

One-paragraph summary of what this system does and for whom.

## Concepts
## Taxonomy
## Relationships
## Attributes
## Lifecycle
## Roles
## Primary workflow
```

## Section rules

### Concepts

- One bullet per core business object: `- **{Concept}** — one-line definition.`
- Every seed entity listed in `index.json` `entities[]` MUST appear as a `**Concept**` bullet.

### Taxonomy

- Is-a lines: `- {Concept} is a kind of {SuperConcept}.`

### Relationships

- Lines MUST follow: `Subject verb Object (cardinality)`
- Allowed cardinalities: `one-to-many` | `many-to-one` | `one-to-one` | `many-to-many`
- Example: `- Opportunity pursuedWithAccount Account (many-to-one)`

### Attributes

- Lines: `- {Concept}: {attribute} ({type}), {attribute} ({type})`
- Common types: `string`, `integer`, `decimal`, `boolean`, `date`, `dateTime`

### Lifecycle

- Stateful entity chains: `- {StatefulConcept}: state1 → state2 → state3 | terminalAlt`
- Allowed lifecycle states are also constrained in SHACL with `sh:in`.

### Roles

- `- **{RoleName}** (bearer: person | organisation) — what they do; permissions: {Entity}:read, {Entity}:write`
- Ontology mirrors roles as `{Something}Role` classes under `bfo:0000023`.

### Primary workflow

- A single end-to-end flow: `{Step 1} → {Step 2} → {Step 3} → {Step 4}`

## Industry addenda

Industry overlays may append additional Concepts / Relationships / Roles / Regulatory notes
in `overlay.md`. They MUST NOT rewrite or delete base sections. See [industry-overlays.md](industry-overlays.md).
