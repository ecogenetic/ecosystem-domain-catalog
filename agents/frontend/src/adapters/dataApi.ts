import type { MappedEntity, MappingHomonym, MappingReadiness, QueryResult } from '../contracts/data';
import { dataPath, request } from './http';

function sourceUrl(sourceId: string, suffix: string): string {
  return dataPath(`/v1/sources/${encodeURIComponent(sourceId)}${suffix}`);
}

export const dataApi = {
  health: () => request<{ ok: boolean }>(dataPath('/v1/health')),
  connect: (body: { kind?: string; uri?: string; database?: string; sourceId?: string; ddl?: string }) =>
    request<{ ok: boolean; sourceId: string; collections: string[]; schemaOnly?: boolean; error?: string }>(dataPath('/v1/sources/connect'), {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  introspect: (id: string, sampleSize = 20) =>
    request<{ ok?: boolean; collections: { name: string; entity?: string; count?: number; infrastructure?: boolean }[] }>(
      sourceUrl(id, '/introspect'),
      { method: 'POST', body: JSON.stringify({ sampleSize }) },
    ),
  sample: (id: string, collection: string, limit = 5) =>
    request<{ documents: unknown[] }>(sourceUrl(id, '/sample'), {
      method: 'POST',
      body: JSON.stringify({ collection, limit }),
    }),
  generateOntology: (id: string) => request(sourceUrl(id, '/generate-ontology'), { method: 'POST', body: '{}' }),
  validateOntology: (id: string) => request<{ ok: boolean; errors?: unknown[] }>(sourceUrl(id, '/validate-ontology'), { method: 'POST', body: '{}' }),
  map: (id: string, preferDomain = '', selections: Record<string, string> = {}) =>
    request<{
      mapped: MappedEntity[];
      unmapped?: { entity: string; collection?: string; reason?: string }[];
      homonyms?: MappingHomonym[];
      readiness?: MappingReadiness;
    }>(sourceUrl(id, '/map'), { method: 'POST', body: JSON.stringify({ preferDomain, selections }) }),
  coverage: (id: string) =>
    request<{
      coveragePct: number;
      propertyCoveragePct?: number;
      gaps?: unknown[];
      mappedCount?: number;
      readiness?: MappingReadiness;
    }>(sourceUrl(id, '/coverage')),
  heal: (id: string) => request(sourceUrl(id, '/heal-mapping'), { method: 'POST', body: '{}' }),
  query: (id: string, query: string, useLlm = false) =>
    request<QueryResult>(sourceUrl(id, '/query'), { method: 'POST', body: JSON.stringify({ query, useLlm }) }),
  compile: (id: string, query: string) =>
    request(sourceUrl(id, '/compile'), { method: 'POST', body: JSON.stringify({ query }) }),
  execute: (id: string, plan: unknown) =>
    request(sourceUrl(id, '/execute'), { method: 'POST', body: JSON.stringify({ plan }) }),
  complexity: (id: string) => request(sourceUrl(id, '/complexity')),
  exportSuite: (id: string) =>
    request(sourceUrl(id, '/tests/export'), { method: 'POST', body: JSON.stringify({ includeUnsupported: true }) }),
  compilePhysical: (body: { domainId?: string; industry?: string; turtle?: string }) =>
    request(dataPath('/v1/physical/compile'), { method: 'POST', body: JSON.stringify(body) }),
  generateDdl: (body: { domainId?: string; industry?: string; turtle?: string }) =>
    request<{ ok?: boolean; ddl?: string; tableCount?: number; model?: import('../contracts/data').PhysicalModel }>(
      dataPath('/v1/physical/ddl'),
      { method: 'POST', body: JSON.stringify(body) },
    ),
  generateMongoSchema: (body: { domainId?: string; industry?: string; turtle?: string }) =>
    request(dataPath('/v1/physical/mongo-schema'), { method: 'POST', body: JSON.stringify(body) }),
  materialize: (body: {
    sourceId?: string;
    domainId?: string;
    industry?: string;
    turtle?: string;
    autoMap?: boolean;
    preferDomain?: string;
  }) =>
    request<{
      ok?: boolean;
      sourceId?: string;
      ddl?: string;
      tableCount?: number;
      collections?: string[];
      mapping?: { mapped?: unknown[]; readiness?: MappingReadiness; homonyms?: MappingHomonym[] };
    }>(dataPath('/v1/physical/materialize'), { method: 'POST', body: JSON.stringify(body) }),
  setOverride: (id: string, overrides: { classes?: Record<string, string>; properties?: Record<string, string> }) =>
    request(sourceUrl(id, '/overrides'), { method: 'POST', body: JSON.stringify({ overrides }) }),
  diagnose: (error: string) =>
    request(dataPath('/v1/diagnose'), { method: 'POST', body: JSON.stringify({ error }) }),
  mcpInfo: () => request(dataPath('/mcp/info')),
  mcpList: () => request(dataPath('/mcp/tools/list'), { method: 'POST', body: '{}' }),
  mcpCall: (name: string, args: Record<string, unknown>) =>
    request(dataPath('/mcp/tools/call'), { method: 'POST', body: JSON.stringify({ name, arguments: args }) }),
};
