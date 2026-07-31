# Playbook: Add or update a generic data source mapping

1. Check if your source format already exists in `mappings/common/index.yaml`.
2. Copy the baseline template under `mappings/{domainId}/generic-mapping.ttl`.
3. Align your data columns/fields to the canonical domain ontology using `owl:equivalentClass` and `rdfs:subPropertyOf`.
4. Update `mappings/common/index.yaml` if you are adding a new generic source type.
5. Run `./tools/validate-catalog.sh` to ensure structural compliance.
6. Commit and open a PR.

## Validation

Mappings are validated against the canonical domain ontology. Ensure that all `legacy:` prefixes resolve correctly and that aligned properties exist in the target domain's `ontology.ttl`.

## Tips

- Keep the `legacy:` namespace generic (e.g., `https://example.com/legacy/data#`) unless documenting a specific vendor schema.
- Use `rdfs:subPropertyOf` to map multiple legacy column names to a single canonical property.
- Never modify the canonical `domains/{id}/ontology.ttl` files; mappings are strictly additive.
