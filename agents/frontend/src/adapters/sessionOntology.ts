import type { CatalogMatch, GraphPayload } from '../contracts/catalog';

const KEY = 'ecosystem.ontology.session.library';
const LEGACY_KEY = 'ecosystem.ontology.session';

export type ClassDomainMatch = {
  classIri: string;
  catalogIri?: string;
  catalogLabel?: string;
  catalogDomain?: string;
  catalogDefinition?: string;
  alternatives?: { iri: string; prefLabel?: string; domainId?: string; definition?: string }[];
  status: 'proposed' | 'accepted' | 'none';
};

export type SessionOntology = {
  id: string;
  name: string;
  fileName?: string;
  turtle: string;
  ontologyIri?: string;
  graph: GraphPayload;
  classes: CatalogMatch[];
  version: number;
  updatedAt: number;
  matchedDomainId?: string;
  classMatches?: ClassDomainMatch[];
};

export type SessionLibrary = {
  items: SessionOntology[];
  activeId: string | null;
};

export type ParsedOntology = {
  name: string;
  fileName?: string;
  turtle: string;
  ontologyIri?: string;
  graph: GraphPayload;
  classes: CatalogMatch[];
};

function newId(): string {
  return `onto-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function emptyLibrary(): SessionLibrary {
  return { items: [], activeId: null };
}

function fromLegacy(value: SessionOntology | Record<string, unknown>): SessionOntology | null {
  const graph = (value as SessionOntology).graph;
  if (!graph) return null;
  return {
    id: typeof (value as SessionOntology).id === 'string' ? (value as SessionOntology).id : 'legacy',
    name: (value as SessionOntology).name || 'Your ontology',
    fileName: (value as SessionOntology).fileName,
    turtle: (value as SessionOntology).turtle || '',
    ontologyIri: (value as SessionOntology).ontologyIri,
    graph,
    classes: (value as SessionOntology).classes || [],
    version: typeof (value as SessionOntology).version === 'number' ? (value as SessionOntology).version : 1,
    updatedAt: typeof (value as SessionOntology).updatedAt === 'number' ? (value as SessionOntology).updatedAt : Date.now(),
    matchedDomainId: (value as SessionOntology).matchedDomainId,
    classMatches: (value as SessionOntology).classMatches,
  };
}

export function loadLibrary(): SessionLibrary {
  try {
    const raw = sessionStorage.getItem(KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as SessionLibrary;
      if (Array.isArray(parsed?.items)) {
        return {
          items: parsed.items.filter((item) => item?.graph),
          activeId: parsed.activeId || parsed.items[0]?.id || null,
        };
      }
    }
    const legacy = sessionStorage.getItem(LEGACY_KEY);
    if (legacy) {
      const one = fromLegacy(JSON.parse(legacy) as Record<string, unknown>);
      if (one) {
        const lib = { items: [one], activeId: one.id };
        saveLibrary(lib);
        sessionStorage.removeItem(LEGACY_KEY);
        return lib;
      }
    }
  } catch {
    /* ignore quota / parse errors */
  }
  return emptyLibrary();
}

export function saveLibrary(value: SessionLibrary): void {
  const payload = JSON.stringify(value);
  try {
    sessionStorage.setItem(KEY, payload);
    sessionStorage.removeItem(LEGACY_KEY);
  } catch {
    const slim: SessionLibrary = {
      ...value,
      items: value.items.map((item) =>
        item.id === value.activeId ? item : { ...item, turtle: '' },
      ),
    };
    sessionStorage.setItem(KEY, JSON.stringify(slim));
  }
}

export function findByOntologyIri(items: SessionOntology[], iri?: string): SessionOntology | undefined {
  const key = (iri || '').trim();
  if (!key) return undefined;
  return items.find((item) => (item.ontologyIri || '').trim() === key);
}

export function addOrUpdateOntology(
  library: SessionLibrary,
  parsed: ParsedOntology,
  options?: { replaceId?: string; forceAdd?: boolean },
): { library: SessionLibrary; item: SessionOntology; action: 'added' | 'updated' } {
  const now = Date.now();
  const replaceId = options?.replaceId;
  const existing =
    (replaceId && library.items.find((item) => item.id === replaceId)) ||
    (!options?.forceAdd && !replaceId ? findByOntologyIri(library.items, parsed.ontologyIri) : undefined);

  if (existing) {
    const item: SessionOntology = {
      ...existing,
      name: parsed.name || existing.name,
      fileName: parsed.fileName || existing.fileName,
      turtle: parsed.turtle,
      ontologyIri: parsed.ontologyIri || existing.ontologyIri,
      graph: parsed.graph,
      classes: parsed.classes,
      version: existing.version + 1,
      updatedAt: now,
      classMatches: [],
    };
    const items = library.items.map((row) => (row.id === existing.id ? item : row));
    return { library: { items, activeId: item.id }, item, action: 'updated' };
  }

  const item: SessionOntology = {
    id: newId(),
    name: parsed.name || 'Untitled ontology',
    fileName: parsed.fileName,
    turtle: parsed.turtle,
    ontologyIri: parsed.ontologyIri,
    graph: parsed.graph,
    classes: parsed.classes,
    version: 1,
    updatedAt: now,
  };
  return {
    library: { items: [item, ...library.items], activeId: item.id },
    item,
    action: 'added',
  };
}

export function patchOntology(
  library: SessionLibrary,
  id: string,
  patch: Partial<SessionOntology>,
): SessionLibrary {
  const items = library.items.map((item) => (item.id === id ? { ...item, ...patch } : item));
  return { ...library, items, activeId: id };
}

export function removeOntology(library: SessionLibrary, id: string): SessionLibrary {
  const items = library.items.filter((item) => item.id !== id);
  const activeId = library.activeId === id ? items[0]?.id || null : library.activeId;
  return { items, activeId };
}

export function setActiveOntology(library: SessionLibrary, id: string | null): SessionLibrary {
  return { ...library, activeId: id };
}

export function neighborhood(graph: GraphPayload, iri: string): GraphPayload {
  const nodes = graph.nodes || [];
  const edges = graph.edges || [];
  const keep = new Set<string>([iri]);
  for (const e of edges) {
    if (e.from === iri) keep.add(e.to);
    if (e.to === iri) keep.add(e.from);
  }
  return {
    nodes: nodes.filter((n) => keep.has(n.iri)),
    edges: edges.filter((e) => keep.has(e.from) && keep.has(e.to)),
  };
}

export function overlayDomainMatches(graph: GraphPayload, matches: ClassDomainMatch[] | undefined): GraphPayload {
  const accepted = (matches || []).filter((m) => m.status === 'accepted' && m.catalogIri);
  if (!accepted.length) return graph;
  const nodes = [...(graph.nodes || [])];
  const seen = new Set(nodes.map((n) => n.iri));
  const edges = [...(graph.edges || [])];
  const inView = new Set(nodes.map((n) => n.iri));
  for (const m of accepted) {
    if (!inView.has(m.classIri) || !m.catalogIri) continue;
    if (!seen.has(m.catalogIri)) {
      seen.add(m.catalogIri);
      nodes.push({
        iri: m.catalogIri,
        kind: 'class',
        prefLabel: m.catalogLabel,
        definition: m.catalogDefinition,
        domainId: m.catalogDomain,
        localName: m.catalogLabel,
      });
    }
    edges.push({ from: m.classIri, to: m.catalogIri, rel: 'mapping' });
  }
  return { nodes, edges };
}

export const SESSION_BUNDLE_KIND = 'ecosystem.ontology.session';
export const SESSION_BUNDLE_VERSION = 1;

export type SessionBundle = {
  kind: typeof SESSION_BUNDLE_KIND;
  version: number;
  exportedAt: string;
  library: SessionLibrary;
};

function isSessionOntology(value: unknown): value is SessionOntology {
  if (!value || typeof value !== 'object') return false;
  const item = value as SessionOntology;
  return Boolean(item.id && item.graph && typeof item.turtle === 'string' && Array.isArray(item.classes));
}

/** Build a downloadable JSON bundle for one ontology or the whole library. */
export function buildSessionBundle(library: SessionLibrary, onlyId?: string): SessionBundle {
  const items = onlyId ? library.items.filter((item) => item.id === onlyId) : library.items;
  const activeId =
    onlyId && items.some((item) => item.id === onlyId)
      ? onlyId
      : items.some((item) => item.id === library.activeId)
        ? library.activeId
        : items[0]?.id || null;
  return {
    kind: SESSION_BUNDLE_KIND,
    version: SESSION_BUNDLE_VERSION,
    exportedAt: new Date().toISOString(),
    library: { items, activeId },
  };
}

export function sessionBundleFileName(library: SessionLibrary, onlyId?: string): string {
  const item = onlyId ? library.items.find((row) => row.id === onlyId) : undefined;
  const base = (item?.name || 'ontology-session')
    .replace(/\.(ttl|owl|rdf|txt|json)$/i, '')
    .replace(/[^\w.-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 64);
  return `${base || 'ontology-session'}.ecosystem-session.json`;
}

/**
 * Parse a saved session file. Accepts the bundle format, a bare SessionLibrary,
 * or a single SessionOntology (legacy-friendly).
 */
export function parseSessionBundle(raw: string): { ok: true; library: SessionLibrary } | { ok: false; error: string } {
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return { ok: false, error: 'That file is not valid JSON.' };
  }
  if (!parsed || typeof parsed !== 'object') {
    return { ok: false, error: 'That file does not look like a saved session.' };
  }
  const obj = parsed as Record<string, unknown>;

  if (obj.kind === SESSION_BUNDLE_KIND && obj.library && typeof obj.library === 'object') {
    const lib = obj.library as SessionLibrary;
    const items = (lib.items || []).filter(isSessionOntology);
    if (!items.length) return { ok: false, error: 'The session file has no ontologies.' };
    return {
      ok: true,
      library: {
        items,
        activeId: items.some((item) => item.id === lib.activeId) ? lib.activeId : items[0].id,
      },
    };
  }

  if (Array.isArray((obj as SessionLibrary).items)) {
    const lib = obj as SessionLibrary;
    const items = (lib.items || []).filter(isSessionOntology);
    if (!items.length) return { ok: false, error: 'The session file has no ontologies.' };
    return {
      ok: true,
      library: {
        items,
        activeId: items.some((item) => item.id === lib.activeId) ? lib.activeId : items[0].id,
      },
    };
  }

  if (isSessionOntology(obj)) {
    return { ok: true, library: { items: [obj], activeId: obj.id } };
  }

  return {
    ok: false,
    error: 'Expected an ecosystem ontology session file (.ecosystem-session.json).',
  };
}

/** Merge an imported library into the current one (same id replaces; new ids are added). */
export function mergeSessionLibrary(
  current: SessionLibrary,
  incoming: SessionLibrary,
): { library: SessionLibrary; added: number; updated: number } {
  const byId = new Map(current.items.map((item) => [item.id, item]));
  let added = 0;
  let updated = 0;
  for (const item of incoming.items) {
    if (byId.has(item.id)) {
      updated += 1;
      byId.set(item.id, { ...item, updatedAt: Date.now() });
    } else {
      added += 1;
      byId.set(item.id, item);
    }
  }
  const items = [...byId.values()].sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));
  const activeId =
    (incoming.activeId && items.some((item) => item.id === incoming.activeId) && incoming.activeId) ||
    current.activeId ||
    items[0]?.id ||
    null;
  return { library: { items, activeId }, added, updated };
}

export function downloadSessionBundle(library: SessionLibrary, onlyId?: string): void {
  const bundle = buildSessionBundle(library, onlyId);
  const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = sessionBundleFileName(library, onlyId);
  a.click();
  URL.revokeObjectURL(url);
}
