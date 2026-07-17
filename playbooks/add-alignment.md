# Playbook: add a cross-domain entity alignment

Alignments link an existing **domain class IRI** to a class in the **core shared-entity
vocabulary** (`core/ontology.ttl`) so that multi-domain composition can resolve shared
real-world things (Customer, Product, Order, ...) to **one canonical entity** instead of
duplicating them per domain. Alignments live in `core/alignments.ttl` and are loaded
**only** when a consumer combines more than one domain; single-domain generation never
reads them.

## The similarity taxonomy (pick exactly one bucket)

Every cross-domain candidate pair is classified into one of four buckets, and the bucket
decides what (if anything) you write:

| Bucket | Meaning | Triple to add | Downstream effect |
|--------|---------|---------------|-------------------|
| **Equivalent** | Same real-world thing (e.g. `crm:Account` and `cvm:Customer` are both "the customer") | `dom:X owl:equivalentClass core:Y .` | Classes **collapse** into one canonical entity (core label wins); attributes union; relationships rebind |
| **Specialization** | Domain class is a subtype (e.g. `cvm:Subscriber` is a kind of customer) | `dom:X rdfs:subClassOf core:Y .` | Class **stays distinct**, linked to the canonical parent |
| **Homonym / false friend** | Same or similar name, different meaning | **NO triple** — document it in the false-friends comment block in `alignments.ttl` | Classes stay separate |
| **Merely related** | Associated but not the same identity (e.g. `Contact` vs `Customer`) | **NO triple** | Model as an association, not identity |

## The false-friend guard (non-negotiable)

Alignment is by **curated semantic mapping**, never by name similarity. The canonical trap
is `Account`: a customer organisation in `crm`, a financial product in `fin`/banking
(`industries/banking/industry.md` warns about exactly this). Identical strings must never
be collapsed on that basis alone. When in doubt, do **not** align — an unaligned duplicate
is recoverable; a wrong collapse silently corrupts every generated model.

## Procedure (assisted, propose → confirm)

1. **Propose.** Run the assisted suggester (EcosystemCode MCP tool
   `propose_ontology_entity_alignments`, optionally scoped with `domain_id`). It scans
   domain ontologies for candidates against each `core:*` entity using names, SKOS
   prefLabels/altLabels, and definition similarity, and classifies each candidate into the
   taxonomy above with a confidence and rationale. False friends default to
   `suggestedAlignment: none`.
2. **Review.** A human checks each proposal against the domain `description.md` and the
   core class definition. Never auto-confirm; never confirm a low-confidence equivalence
   without reading both definitions.
3. **Confirm.** Approved entries go through `confirm_ontology_entity_alignments`
   (`{domainId, className, coreEntity, alignment}` where alignment is `equivalent` or
   `specialization`). The tool emits curated triples and, when a catalog checkout is
   available, appends them to `core/alignments.ttl`. Entries classified false-friend or
   related are rejected by the tool.
4. **Validate and commit** (in this repo — the source of truth):

   ```bash
   ./tools/validate-catalog.sh   # checks every triple references a real domain class and core class
   git add core/alignments.ttl && git commit
   ```

5. **Rebuild ecosystem-server** so its classpath snapshot refreshes (the build syncs
   automatically).

## Manual authoring (without the suggester)

You can also add triples by hand. Rules:

- Reference only existing IRIs: the domain class must exist in
  `domains/{id}/ontology.ttl` and the target in `core/ontology.ttl`. Never modify the
  domain ontology itself — alignments are statements *about* IRIs defined elsewhere.
- Add the domain's `@prefix` at the top of `alignments.ttl` if it is not already declared.
- Keep the file organised by core-entity cluster (Customer/Party, Product, Order, ...) and
  keep the false-friends comment block up to date.
- If the concept you need has no core class, extend `core/ontology.ttl` first (same SKOS
  bar as any domain class: `skos:prefLabel` + `skos:definition`, `skos:altLabel`
  encouraged; stable IRIs, add-only).

## Review bar

- The two definitions describe the same real-world thing (equivalent) or a genuine
  subtype (specialization) — not just similar words.
- Many-to-one is fine (several domain classes may align to one core class); one domain
  class must not align to two core classes.
- Every skipped homonym worth noting is recorded in the false-friends block.
- `./tools/validate-catalog.sh` passes.

PR title: `feat(core): align {dom}:{Class} -> core:{Entity}` (or `docs: ...` for
false-friend documentation only).
