export type ToolDef = {
  agent: 'catalog' | 'data';
  name: string;
  description: string;
  method: 'GET' | 'POST';
  path: string;
  example?: Record<string, unknown>;
};

export const CATALOG_TOOLS: ToolDef[] = [
  { agent: 'catalog', name: 'search_catalog', description: 'Search ontologies, overlays, and mappings', method: 'POST', path: '/v1/search', example: { query: 'deal', limit: 12, useLlm: false } },
  { agent: 'catalog', name: 'list_domains', description: 'List catalog domains', method: 'GET', path: '/v1/domains' },
  { agent: 'catalog', name: 'list_industries', description: 'List industries', method: 'GET', path: '/v1/industries' },
  { agent: 'catalog', name: 'get_concept', description: 'Get one concept by IRI', method: 'GET', path: '/v1/concepts', example: { iri: 'https://ecosystemcode.com/ontology/cvm#Customer' } },
  { agent: 'catalog', name: 'get_ontology', description: 'Ontology Turtle for a domain', method: 'GET', path: '/v1/ontology', example: { domainId: 'cvm' } },
  { agent: 'catalog', name: 'expand_graph', description: 'Expand graph neighbors', method: 'POST', path: '/v1/graph/expand', example: { iri: 'https://ecosystemcode.com/ontology/cvm#Customer', depth: 1 } },
  { agent: 'catalog', name: 'preview_ontology', description: 'Parse Turtle in memory for this browser session', method: 'POST', path: '/v1/ontologies/preview', example: { turtle: '@prefix : <https://example.com/ontology/mine#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:Thing a owl:Class .' } },
  { agent: 'catalog', name: 'get_mappings_for_concept', description: 'Mappings for a concept', method: 'GET', path: '/v1/mappings', example: { iri: 'https://ecosystemcode.com/ontology/cvm#Customer' } },
  { agent: 'catalog', name: 'get_alignments', description: 'Core alignment or false-friend', method: 'GET', path: '/v1/alignments', example: { iri: 'https://ecosystemcode.com/ontology/crm#Account' } },
  { agent: 'catalog', name: 'validate_text', description: 'Validate tokens against the catalog', method: 'POST', path: '/v1/validate', example: { text: 'Account' } },
  { agent: 'catalog', name: 'validate_iris', description: 'Keep only IRIs in the graph', method: 'POST', path: '/v1/iris/validate', example: { iris: ['https://ecosystemcode.com/ontology/cvm#Customer'] } },
  { agent: 'catalog', name: 'index_health', description: 'Index health', method: 'GET', path: '/v1/index/health' },
  { agent: 'catalog', name: 'rebuild_index', description: 'Rebuild the catalog index', method: 'POST', path: '/v1/index/rebuild', example: { incremental: false } },
  { agent: 'catalog', name: 'heal_index', description: 'Repair stale index files', method: 'POST', path: '/v1/index/heal', example: {} },
  { agent: 'catalog', name: 'diagnose_failure', description: 'Suggest a heal after failure', method: 'POST', path: '/v1/diagnose', example: { error: 'empty search' } },
];

export const DATA_TOOLS: ToolDef[] = [
  { agent: 'data', name: 'connect_source', description: 'Connect to MongoDB, PostgreSQL, DDL, or memory', method: 'POST', path: '/v1/sources/connect', example: { kind: 'mongodb', uri: 'mongodb://localhost:27017', database: 'mydb' } },
  { agent: 'data', name: 'introspect_schema', description: 'Introspect collections', method: 'POST', path: '/v1/sources/{id}/introspect', example: { sampleSize: 20 } },
  { agent: 'data', name: 'sample_records', description: 'Sample documents', method: 'POST', path: '/v1/sources/{id}/sample', example: { collection: 'customer', limit: 5 } },
  { agent: 'data', name: 'generate_source_ontology', description: 'Generate OWL from schema', method: 'POST', path: '/v1/sources/{id}/generate-ontology', example: {} },
  { agent: 'data', name: 'validate_source_ontology', description: 'Validate generated ontology', method: 'POST', path: '/v1/sources/{id}/validate-ontology', example: {} },
  { agent: 'data', name: 'map_to_catalog', description: 'Map onto catalog IRIs', method: 'POST', path: '/v1/sources/{id}/map', example: { preferDomain: '' } },
  { agent: 'data', name: 'mapping_coverage', description: 'Coverage after mapping', method: 'GET', path: '/v1/sources/{id}/coverage' },
  { agent: 'data', name: 'heal_mapping', description: 'Repair unmapped collections', method: 'POST', path: '/v1/sources/{id}/heal-mapping', example: {} },
  { agent: 'data', name: 'query_mapped_data', description: 'Natural-language query', method: 'POST', path: '/v1/sources/{id}/query', example: { query: 'how many customers do i have', useLlm: false } },
  { agent: 'data', name: 'compile_query_plan', description: 'Compile NL to a plan', method: 'POST', path: '/v1/sources/{id}/compile', example: { query: 'how many customers do i have' } },
  { agent: 'data', name: 'execute_query_plan', description: 'Execute a compiled plan', method: 'POST', path: '/v1/sources/{id}/execute', example: { plan: {} } },
  { agent: 'data', name: 'assess_complexity', description: 'Five-level complexity', method: 'GET', path: '/v1/sources/{id}/complexity' },
  { agent: 'data', name: 'export_rerun_suite', description: 'Export rerun suite', method: 'POST', path: '/v1/sources/{id}/tests/export', example: { includeUnsupported: true } },
  { agent: 'data', name: 'diagnose_failure', description: 'Suggest a heal after failure', method: 'POST', path: '/v1/diagnose', example: { error: 'unmapped' } },
  { agent: 'data', name: 'validate_iris', description: 'Keep only catalog IRIs', method: 'POST', path: '/v1/iris/validate', example: { iris: [] } },
];
