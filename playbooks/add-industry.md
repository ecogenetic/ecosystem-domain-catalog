# Playbook: Add a new industry

Prompt-style procedure for registering a new industry vertical (e.g. utilities, logistics).
Industries provide cross-domain context and shared concepts; per-domain specialization is
done separately via [add-industry-overlay.md](add-industry-overlay.md).

## Steps

1. Add the registry entry to `industries.json` (AGENTS.md section 7):
   `{ "id": "...", "label": "...", "description": "..." }` — id lowercase.
2. Create `industries/{id}/industry.md` containing:
   - one-paragraph description of the vertical;
   - **Terminology** section: industry-specific terms and synonyms;
   - **Regulatory notes** section: compliance concerns generation should respect
     (e.g. KYC/AML for banking, HIPAA for healthcare, responsible-gambling for gambling).
3. Create `industries/{id}/common.ttl` with shared concepts reused across domain overlays,
   namespace `https://ecosystemcode.com/ontology/industry/{id}#`, following the class/property
   templates of AGENTS.md section 4 (SKOS labels + definitions mandatory).
   Only include concepts genuinely shared by multiple domains (e.g. banking `KYCProfile`);
   domain-specific specializations belong in overlays.
4. Run `./tools/validate-catalog.sh` until it exits 0.
5. PR titled `Add industry: {Label}`. After merge, sync into ecosystem-server per the README.
6. The wizard's optional Industry selector picks the new industry up automatically from the
   synced registry — no frontend change needed.
