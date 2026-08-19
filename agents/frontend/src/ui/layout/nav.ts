export type NavIcon = 'book' | 'database' | 'terminal' | 'activity';

export type NavNode = {
  id: string;
  label: string;
  hint?: string;
  to?: string;
  icon?: NavIcon;
  end?: boolean;
  count?: number;
  dynamic?: 'domains' | 'industries' | 'session';
  keywords?: string[];
  children?: NavNode[];
};

export const NAV: NavNode[] = [
  {
    id: 'ontology',
    label: 'Ontology building',
    icon: 'book',
    to: '/',
    children: [
      { id: 'overview', label: 'Overview', to: '/', end: true, keywords: ['home', 'lookup'] },
      {
        id: 'classes',
        label: 'Search the catalog',
        to: '/ontology/classes',
        keywords: ['search', 'prefLabel', 'skos', 'lookup', 'class'],
      },
      {
        id: 'hierarchy',
        label: 'Hierarchy',
        to: '/ontology/hierarchy',
        keywords: ['graph', 'subclass', 'taxonomy'],
      },
      {
        id: 'yours',
        label: 'Your ontology',
        to: '/ontology/yours',
        dynamic: 'session',
        keywords: ['upload', 'session', 'turtle', 'owl'],
        children: [],
      },
      {
        id: 'types',
        label: 'Domain ontologies',
        keywords: ['domain', 'owl', 'class'],
        dynamic: 'domains',
        children: [],
      },
      {
        id: 'overlays',
        label: 'Industry overlays',
        keywords: ['industry', 'banking', 'overlay'],
        dynamic: 'industries',
        children: [],
      },
    ],
  },
  {
    id: 'data',
    label: 'Your data',
    icon: 'database',
    to: '/sources/connect',
    children: [
      { id: 'connect', label: 'Data sources', to: '/sources/connect', keywords: ['mongodb', 'postgresql', 'ddl', 'connect'] },
      { id: 'understand', label: 'Schema profiler', to: '/sources/understand', keywords: ['introspect', 'schema', 'understand'] },
      { id: 'map', label: 'Field mapping', to: '/sources/map', keywords: ['coverage', 'catalog', 'map'] },
      { id: 'ask', label: 'Query', to: '/sources/ask', keywords: ['query', 'count', 'ask'] },
    ],
  },
  {
    id: 'runtime',
    label: 'Runtime',
    icon: 'activity',
    to: '/ontology/hierarchy?overlay=paths',
    children: [
      {
        id: 'agent-paths',
        label: 'Agent paths',
        to: '/ontology/hierarchy?overlay=paths',
        keywords: ['runtime', 'overlay', 'execution', 'agent'],
      },
    ],
  },
  {
    id: 'developers',
    label: 'Developer toolchain',
    icon: 'terminal',
    to: '/advanced/catalog',
    children: [
      { id: 'catalog-tools', label: 'Catalog tools', to: '/advanced/catalog', keywords: ['openapi', 'json'] },
      { id: 'data-tools', label: 'Data tools', to: '/advanced/data', keywords: ['openapi', 'json'] },
      { id: 'docs', label: 'API docs', to: '/advanced/docs', keywords: ['swagger', 'redoc'] },
      { id: 'mcp', label: 'MCP', to: '/advanced/mcp', keywords: ['json-rpc', 'stdio'] },
    ],
  },
];

export type DomainRef = { id: string; name: string; acronym?: string };
export type IndustryRef = { id: string; label: string };

export type SessionNavRef = { id: string; name: string; version: number; matchedDomainId?: string };

export function hydrateNav(
  domains: DomainRef[],
  industries: IndustryRef[],
  sessionItems: SessionNavRef[] = [],
): NavNode[] {
  return NAV.map((group) => {
    const children = group.children?.map((child) => {
      if (child.dynamic === 'domains') {
        return {
          ...child,
          count: domains.length,
          children: domains.map((d) => ({
            id: `domain-${d.id}`,
            label: d.acronym || d.id.toUpperCase(),
            hint: d.name,
            to: `/ontology/domains/${d.id}`,
            keywords: [d.id, d.name, d.acronym || ''],
          })),
        };
      }
      if (child.dynamic === 'industries') {
        return {
          ...child,
          count: industries.length,
          children: industries.map((i) => ({
            id: `industry-${i.id}`,
            label: i.label,
            hint: i.id,
            to: `/ontology/industries/${i.id}`,
            keywords: [i.id, i.label],
          })),
        };
      }
      if (child.dynamic === 'session') {
        return {
          ...child,
          count: sessionItems.length,
          children: [
            {
              id: 'yours-add',
              label: sessionItems.length ? 'Add another' : 'Add ontology',
              to: '/ontology/yours',
              end: true,
              keywords: ['upload', 'add', 'turtle', 'owl'],
            },
            ...sessionItems.map((item) => ({
              id: `yours-${item.id}`,
              label: item.name.replace(/\.(ttl|owl|rdf|txt)$/i, '') || 'Untitled ontology',
              hint: item.matchedDomainId ? `v${item.version} · ${item.matchedDomainId}` : `v${item.version}`,
              to: `/ontology/yours/${item.id}`,
              keywords: [item.name, item.matchedDomainId || '', 'session'],
            })),
          ],
        };
      }
      return child;
    });
    let count: number | undefined;
    if (group.id === 'ontology') count = domains.length;
    if (group.id === 'data') count = 4;
    return { ...group, count, children };
  });
}

export function pathIsActive(to: string | undefined, pathname: string, end?: boolean): boolean {
  if (!to) return false;
  const pathOnly = to.split('?')[0];
  if (pathOnly === '/') return pathname === '/' || pathname === '/ontology';
  if (end) return pathname === pathOnly;
  return pathname === pathOnly || pathname.startsWith(`${pathOnly}/`);
}

export function nodeMatches(node: NavNode, q: string): boolean {
  if (!q) return true;
  const hay = [node.label, node.hint, node.to, ...(node.keywords || [])]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();
  return hay.includes(q);
}

export function filterTree(nodes: NavNode[], q: string): NavNode[] {
  const needle = q.trim().toLowerCase();
  if (!needle) return nodes;
  const keep: NavNode[] = [];
  for (const node of nodes) {
    const children = node.children ? filterTree(node.children, needle) : [];
    if (nodeMatches(node, needle) || children.length) {
      keep.push(children.length ? { ...node, children } : node);
    }
  }
  return keep;
}

export function groupIdsForPath(nodes: NavNode[], pathname: string, acc: string[] = []): string[] {
  for (const node of nodes) {
    if (node.children?.length) {
      const nested = groupIdsForPath(node.children, pathname, [...acc, node.id]);
      if (nested.length) return nested;
      if (pathIsActive(node.to, pathname, node.end)) return [...acc, node.id];
    } else if (pathIsActive(node.to, pathname, node.end)) {
      return acc;
    }
  }
  return [];
}

export type CatalogSection = 'overview' | 'workspace' | 'hierarchy' | 'session';

export function catalogSection(pathname: string): CatalogSection {
  if (pathname.includes('/hierarchy')) return 'hierarchy';
  if (pathname.includes('/ontology/yours')) return 'session';
  if (
    pathname.includes('/ontology/classes') ||
    pathname.includes('/ontology/domains/') ||
    pathname.includes('/ontology/industries/')
  ) {
    return 'workspace';
  }
  return 'overview';
}

export function catalogDomainId(pathname: string): string {
  const m = pathname.match(/\/ontology\/domains\/([^/]+)/);
  return m?.[1] || '';
}

export function catalogIndustryId(pathname: string): string {
  const m = pathname.match(/\/ontology\/industries\/([^/]+)/);
  return m?.[1] || '';
}

export function catalogSessionId(pathname: string): string {
  const m = pathname.match(/\/ontology\/yours\/([^/]+)/);
  return m?.[1] || '';
}

export const DATA_STEPS = ['connect', 'understand', 'map', 'ask'] as const;
export type DataStep = (typeof DATA_STEPS)[number];

export function dataStepFromPath(pathname: string): DataStep {
  const part = pathname.split('/')[2];
  return (DATA_STEPS as readonly string[]).includes(part) ? (part as DataStep) : 'connect';
}

export function advancedSection(pathname: string): 'catalog' | 'data' | 'docs' | 'mcp' {
  const part = pathname.split('/')[2];
  if (part === 'data' || part === 'docs' || part === 'mcp') return part;
  return 'catalog';
}

export function headerCopy(
  pathname: string,
  domains: DomainRef[],
  industries: IndustryRef[],
  sessionItems: SessionNavRef[] = [],
): { title: string; sub: string } {
  const domainId = catalogDomainId(pathname);
  if (domainId) {
    const d = domains.find((x) => x.id === domainId);
    return {
      title: d?.name || domainId,
      sub: `Object type · ontology ${domainId}`,
    };
  }
  const industryId = catalogIndustryId(pathname);
  if (industryId) {
    const i = industries.find((x) => x.id === industryId);
    return {
      title: i?.label || industryId,
      sub: `Industry overlay · ${industryId}`,
    };
  }
  if (pathname.startsWith('/sources')) {
    const step = dataStepFromPath(pathname);
    const copy: Record<DataStep, { title: string; sub: string }> = {
      connect: { title: 'Data sources', sub: 'MongoDB, PostgreSQL, DDL, or sample data' },
      understand: { title: 'Schema profiler', sub: 'Business collections found in the source' },
      map: { title: 'Field mapping', sub: 'Match collections to catalog classes' },
      ask: { title: 'Query', sub: 'Count through mapped fields only' },
    };
    return copy[step];
  }
  if (pathname.startsWith('/advanced')) {
    const section = advancedSection(pathname);
    const copy = {
      catalog: { title: 'Catalog tools', sub: 'Call every catalog endpoint with a JSON body' },
      data: { title: 'Data tools', sub: 'Connect, map, and query from the raw API' },
      docs: { title: 'API docs', sub: 'Swagger for catalog and data on this origin' },
      mcp: { title: 'MCP', sub: 'JSON-RPC tools/list and tools/call' },
    } as const;
    return copy[section];
  }
  if (pathname.includes('/ontology/yours')) {
    const sessionId = catalogSessionId(pathname);
    const item = sessionItems.find((row) => row.id === sessionId);
    if (item) {
      return {
        title: item.name.replace(/\.(ttl|owl|rdf|txt)$/i, '') || 'Your ontology',
        sub: `v${item.version} · this tab only — never written to the catalog`,
      };
    }
    return {
      title: 'Your ontology',
      sub: 'Add or update files in this tab — never written to the catalog',
    };
  }
  if (pathname.includes('/hierarchy')) {
    return { title: 'Hierarchy', sub: 'Subclass, mapping, and alignment relations' };
  }
  if (pathname.includes('/classes')) {
    return { title: 'Search the catalog', sub: 'Match a label, synonym, or definition to an IRI' };
  }
  return { title: 'Search the catalog', sub: 'Match a label, synonym, or definition to an IRI' };
}
