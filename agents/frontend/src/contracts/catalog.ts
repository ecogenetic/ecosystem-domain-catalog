export type CatalogMatch = {
  iri: string;
  kind?: string;
  domainId?: string;
  industryId?: string;
  prefLabel?: string;
  altLabels?: string[];
  definition?: string;
  localName?: string;
  score?: number;
  reason?: string[];
  coreAlignment?: { iri?: string; relation?: string };
  lifecycleStates?: string[];
  shapes?: ShapeConstraint[];
  mappings?: MappingTriple[];
};

export type ShapeConstraint = {
  path?: string;
  pathIri?: string;
  minCount?: number;
  class?: string;
  classLocal?: string;
  in?: string[];
};

export type MappingTriple = {
  source_iri?: string;
  target_iri?: string;
  predicate?: string;
  source_path?: string;
  isStub?: boolean;
};

export type GraphPayload = {
  ok?: boolean;
  nodes?: CatalogMatch[];
  edges?: { from: string; to: string; rel: string }[];
};

export type SearchResult = {
  ok?: boolean;
  query?: string;
  matches?: CatalogMatch[];
  mappings?: unknown[];
  ontology?: { turtle?: string; ontologyIri?: string };
  llm?: { used?: boolean };
};

export const EXPAND_RELS = ['subClassOf', 'mapping', 'alignment', 'objectProperty'] as const;

export function ontologyKindLabel(kind?: string): string {
  if (kind === 'overlay_class') return 'overlay class';
  if (kind === 'class') return 'class';
  if (kind === 'role') return 'role';
  if (kind === 'unmapped') return 'unmapped';
  return kind || 'class';
}

export function scoreBand(score: number | undefined, all: number[]): 'High' | 'Med' | 'Low' | null {
  if (score == null || !all.length) return null;
  const sorted = [...all].sort((a, b) => a - b);
  const hi = sorted[Math.floor((sorted.length - 1) * 0.66)] ?? sorted[sorted.length - 1];
  const lo = sorted[Math.floor((sorted.length - 1) * 0.33)] ?? sorted[0];
  if (score >= hi) return 'High';
  if (score >= lo) return 'Med';
  return 'Low';
}

export function isMapped(m: CatalogMatch): boolean {
  if ((m.mappings || []).length > 0) return true;
  const rel = m.coreAlignment?.relation;
  return Boolean(rel && rel !== 'none');
}
