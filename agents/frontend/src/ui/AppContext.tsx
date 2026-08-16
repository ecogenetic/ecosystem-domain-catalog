import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { catalogApi } from '../adapters/catalogApi';
import { dataApi } from '../adapters/dataApi';
import { loadLibrary, saveLibrary, type SessionLibrary } from '../adapters/sessionOntology';
import { gatewayHealth } from '../adapters/toolsApi';
import type { CatalogMatch, GraphPayload } from '../contracts/catalog';
import type { DomainRef, IndustryRef } from './layout/nav';

export type GraphFrame = {
  selected: CatalogMatch;
  graph: GraphPayload;
};

type Ctx = {
  useLlm: boolean;
  setUseLlm: (v: boolean) => void;
  theme: 'dark' | 'light';
  toggleTheme: () => void;
  catalogOk: boolean | null;
  dataOk: boolean | null;
  sourceId: string;
  setSourceId: (id: string) => void;
  selected: CatalogMatch | null;
  setSelected: (m: CatalogMatch | null) => void;
  graph: GraphPayload | null;
  setGraph: (g: GraphPayload | null) => void;
  catalogKey: number;
  resetCatalog: () => void;
  domains: DomainRef[];
  industries: IndustryRef[];
  graphTrail: GraphFrame[];
  recordGraphDrill: () => void;
  restoreGraphUp: () => boolean;
  clearGraphTrail: () => void;
  sessionLibrary: SessionLibrary;
  setSessionLibrary: (next: SessionLibrary) => void;
};

const AppCtx = createContext<Ctx | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [useLlm, setUseLlm] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>(() =>
    document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark',
  );
  const [catalogOk, setCatalogOk] = useState<boolean | null>(null);
  const [dataOk, setDataOk] = useState<boolean | null>(null);
  const [sourceId, setSourceId] = useState('');
  const [selected, setSelected] = useState<CatalogMatch | null>(null);
  const [graph, setGraph] = useState<GraphPayload | null>(null);
  const [catalogKey, setCatalogKey] = useState(0);
  const [domains, setDomains] = useState<DomainRef[]>([]);
  const [industries, setIndustries] = useState<IndustryRef[]>([]);
  const [graphTrail, setGraphTrail] = useState<GraphFrame[]>([]);
  const [sessionLibrary, setSessionLibraryState] = useState<SessionLibrary>(() => loadLibrary());

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    gatewayHealth()
      .then(() => {
        catalogApi.health().then(() => setCatalogOk(true)).catch(() => setCatalogOk(false));
        dataApi.health().then(() => setDataOk(true)).catch(() => setDataOk(false));
        catalogApi.domains().then((d) => setDomains(d.domains || [])).catch(() => undefined);
        catalogApi.industries().then((d) => setIndustries(d.industries || [])).catch(() => undefined);
      })
      .catch(() => {
        setCatalogOk(false);
        setDataOk(false);
      });
  }, []);

  const value = useMemo(
    () => ({
      useLlm,
      setUseLlm,
      theme,
      toggleTheme: () => setTheme((t) => (t === 'dark' ? 'light' : 'dark')),
      catalogOk,
      dataOk,
      sourceId,
      setSourceId,
      selected,
      setSelected,
      graph,
      setGraph,
      catalogKey,
      resetCatalog: () => {
        setSelected(null);
        setGraph(null);
        setGraphTrail([]);
        setCatalogKey((k) => k + 1);
      },
      domains,
      industries,
      graphTrail,
      recordGraphDrill: () => {
        if (!selected || !graph) return;
        setGraphTrail((t) => [...t, { selected, graph }]);
      },
      restoreGraphUp: () => {
        const prev = graphTrail[graphTrail.length - 1];
        if (!prev) return false;
        setGraphTrail((t) => t.slice(0, -1));
        setSelected(prev.selected);
        setGraph(prev.graph);
        return true;
      },
      clearGraphTrail: () => setGraphTrail([]),
      sessionLibrary,
      setSessionLibrary: (next: SessionLibrary) => {
        saveLibrary(next);
        setSessionLibraryState(next);
      },
    }),
    [useLlm, theme, catalogOk, dataOk, sourceId, selected, graph, catalogKey, domains, industries, graphTrail, sessionLibrary],
  );

  return <AppCtx.Provider value={value}>{children}</AppCtx.Provider>;
}

export function useApp() {
  const ctx = useContext(AppCtx);
  if (!ctx) throw new Error('useApp outside provider');
  return ctx;
}
