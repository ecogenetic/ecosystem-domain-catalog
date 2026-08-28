export type CollectionInfo = {
  name: string;
  entity?: string;
  count?: number;
  infrastructure?: boolean;
};

export type MappedEntity = {
  entity: string;
  collection?: string;
  catalogIri?: string;
  catalogDomain?: string;
  prefLabel?: string;
  alignmentStatus?: 'catalog_aligned';
  mappingRelation?: 'rdfs:subClassOf';
  joins?: { field: string; targetEntity: string; targetCollection?: string }[];
};

export type MappingReadiness = {
  status: 'ready' | 'needs_review';
  readyForQuery: boolean;
  catalogAligned: number;
  unresolved: number;
  ambiguous: number;
};

export type MappingHomonym = {
  entity: string;
  collection?: string;
  reason?: string;
  candidates: string[];
  options?: { iri: string; domainId?: string; prefLabel?: string }[];
};

export type QueryResult = {
  ok?: boolean;
  result?: number;
  query?: string;
  plan?: {
    targetClass?: string;
    collection?: string;
    filters?: { entity: string; field: string; op: string; value: unknown }[];
    joins?: { from: string; to: string; field: string }[];
  };
  error?: string;
  reason?: string;
  readiness?: MappingReadiness;
  unmapped?: (string | { entity?: string; reason?: string })[];
  homonyms?: MappingHomonym[];
  targetCandidates?: string[];
  unmappedRelationships?: { from: string; to: string }[];
  operator?: string;
  maxRowsPerEntity?: number;
  rowCounts?: Record<string, number>;
  llm?: { used?: boolean };
};

export const DATA_EXAMPLES = [
  'how many customers do i have',
  'how many active customers',
  'how many orders in the last month',
  'how many orders have customers',
  'how many orders have customers that are active that ordered in the last month',
];
