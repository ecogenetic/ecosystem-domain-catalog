# Playbook: Add a new data source mapping

1. Check if your source already exists in `mappings/common/index.yaml`.
2. Copy a template under `mappings/{domainId}/` or create a new file (e.g., `crm-salesforce.ttl`).
3. Add your data source’s class/property mappings using `owl:equivalentClass`, `rdfs:subPropertyOf`.
4. Register the mapping in `mappings/common/index.yaml` if adding a new source.
5. Run `./tools/validate-catalog.sh`.
6. Commit and open a PR.

## Validation

Currently, mappings are validated manually against the canonical ontology. Future versions may include automated validation.
