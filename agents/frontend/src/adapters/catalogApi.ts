import type { CatalogMatch, GraphPayload, SearchResult } from '../contracts/catalog';
import { catalogPath, request } from './http';

export const catalogApi = {
  health: () => request<{ ok: boolean }>(catalogPath('/v1/health')),
  search: (body: Record<string, unknown>) =>
    request<SearchResult>(catalogPath('/v1/search'), { method: 'POST', body: JSON.stringify(body) }),
  domains: () => request<{ domains: { id: string; name: string; acronym?: string }[] }>(catalogPath('/v1/domains')),
  industries: () => request<{ industries: { id: string; label: string }[] }>(catalogPath('/v1/industries')),
  concept: (iri: string) =>
    request<CatalogMatch & { ok?: boolean }>(`${catalogPath('/v1/concepts')}?iri=${encodeURIComponent(iri)}`),
  ontology: (domainId: string, industry?: string) => {
    const q = industry ? `?industry=${encodeURIComponent(industry)}` : '';
    return request<{ turtle?: string; classes?: CatalogMatch[] }>(
      `${catalogPath(`/v1/ontology/${encodeURIComponent(domainId)}`)}${q}`,
    );
  },
  expand: (iri: string, depth = 1, rels?: string[]) =>
    request<GraphPayload>(catalogPath('/v1/graph/expand'), {
      method: 'POST',
      body: JSON.stringify({ iri, depth, rels }),
    }),
  previewOntology: (turtle: string) =>
    request<GraphPayload & { ok?: boolean; error?: string; detail?: string; classes?: CatalogMatch[]; ontologyIri?: string; truncated?: boolean; stored?: boolean }>(
      catalogPath('/v1/ontologies/preview'),
      { method: 'POST', body: JSON.stringify({ turtle }) },
    ),
  mappings: (iri: string) => request(`${catalogPath('/v1/mappings')}?iri=${encodeURIComponent(iri)}`),
  alignments: (iri: string) => request(`${catalogPath('/v1/alignments')}?iri=${encodeURIComponent(iri)}`),
  validateText: (text: string) =>
    request(catalogPath('/v1/validate'), { method: 'POST', body: JSON.stringify({ text }) }),
  validateIris: (iris: string[]) =>
    request(catalogPath('/v1/iris/validate'), { method: 'POST', body: JSON.stringify({ iris }) }),
  indexHealth: () => request(catalogPath('/v1/index/health')),
  rebuild: (incremental = false) =>
    request(catalogPath('/v1/index/rebuild'), { method: 'POST', body: JSON.stringify({ incremental }) }),
  heal: (paths?: string[]) =>
    request(catalogPath('/v1/index/heal'), { method: 'POST', body: JSON.stringify({ paths }) }),
  diagnose: (error: string) =>
    request(catalogPath('/v1/diagnose'), { method: 'POST', body: JSON.stringify({ error }) }),
  mcpInfo: () => request(catalogPath('/mcp/info')),
  mcpList: () => request(catalogPath('/mcp/tools/list'), { method: 'POST', body: '{}' }),
  mcpCall: (name: string, args: Record<string, unknown>) =>
    request(catalogPath('/mcp/tools/call'), { method: 'POST', body: JSON.stringify({ name, arguments: args }) }),
};
