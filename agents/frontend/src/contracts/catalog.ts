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

export const CATALOG_EXAMPLES: { label: string; query: string; domain?: string; industry?: string }[] = [
  { label: 'RetailCreditCard overlay', query: 'ontology for banking credit card', domain: 'card', industry: 'banking' },
  { label: 'Deal class', query: 'deal' },
  { label: 'Customer class', query: 'my customer buys mobile phones' },
  { label: 'Account homonym', query: 'Account' },
];

export function ontologyKindLabel(kind?: string): string {
  if (kind === 'overlay_class') return 'overlay class';
  if (kind === 'class') return 'class';
  if (kind === 'role') return 'role';
  if (kind === 'unmapped') return 'unmapped';
  return kind || 'class';
}
