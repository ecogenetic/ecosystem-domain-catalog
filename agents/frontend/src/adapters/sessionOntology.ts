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
