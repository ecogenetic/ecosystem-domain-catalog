import { ArrowUp, Loader2 } from 'lucide-react';
import { FormEvent, KeyboardEvent, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { catalogApi } from '../../adapters/catalogApi';
import {
  EXPAND_RELS,
  isMapped,
  ontologyKindLabel,
  scoreBand,
  type CatalogMatch,
} from '../../contracts/catalog';
import { useApp } from '../AppContext';
import { Card } from '../common/Card';
import { EmptyState } from '../common/EmptyState';
import { GraphCanvas } from '../common/GraphCanvas';
import { SearchableSelect } from '../common/SearchableSelect';
import { catalogDomainId, catalogIndustryId } from '../layout/nav';
import { ConceptInspector } from './ConceptInspector';

export function CatalogHome({ mode }: { mode: 'overview' | 'workspace' }) {
  const {
    useLlm,
    catalogOk,
    selected,
    setSelected,
    graph,
    setGraph,
    domains,
    industries,
    graphTrail,
    recordGraphDrill,
    restoreGraphUp,
    clearGraphTrail,
  } = useApp();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const domainId = catalogDomainId(pathname);
  const industryId = catalogIndustryId(pathname);
  const [query, setQuery] = useState('');
  const [domain, setDomain] = useState('');
  const [industry, setIndustry] = useState('');
  const [matches, setMatches] = useState<CatalogMatch[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const agentPaths = searchParams.get('overlay') === 'paths';
  const setAgentPaths = (on: boolean) => {
    const next = new URLSearchParams(searchParams);
    if (on) next.set('overlay', 'paths');
    else next.delete('overlay');
    setSearchParams(next, { replace: true });
  };

  const visibleMatches = useMemo(() => {
    if (!industry) return matches;
    return matches.filter((m) => m.industryId === industry);
  }, [matches, industry]);

  const filteredGraph = useMemo(() => {
    if (!graph || !industry) return graph;
    return {
      ...graph,
      nodes: (graph.nodes || []).map((n) => {
        const inIndustry = !n.industryId || n.industryId === industry || n.iri === selected?.iri;
        return inIndustry ? n : { ...n, kind: 'unmapped' };
      }),
    };
  }, [graph, industry, selected?.iri]);

  const scores = visibleMatches.map((m) => m.score || 0);

  async function runSearch(text: string, extra?: { domain?: string; industry?: string }) {
    const q = text.trim();
    if (!q) return;
    setBusy(true);
    setError('');
    try {
      const result = await catalogApi.search({
        query: q,
        domain: extra?.domain || domain || undefined,
        industry: extra?.industry || industry || undefined,
        includeOntology: true,
        useLlm,
        limit: 16,
      });
      const next = result.matches || [];
      setMatches(next);
      // Domain/industry routes open three-pane with the top hit; class search stays two-pane until select.
      const autoSelect = Boolean(extra?.domain || extra?.industry || domain || industry);
      if (next[0] && autoSelect) {
        setSelected(next[0]);
        const g = await catalogApi.expand(next[0].iri, 1, [...EXPAND_RELS]);
        setGraph(g);
      } else {
        setSelected(null);
        if (next[0]) {
          const g = await catalogApi.expand(next[0].iri, 1, [...EXPAND_RELS]);
          setGraph(g);
        } else {
          setGraph(null);
        }
      }
    } catch {
      setError('Could not reach the catalog. Check that the agents gateway is running, then try again.');
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (domainId) {
      const name = domains.find((d) => d.id === domainId)?.name || domainId;
      setDomain(domainId);
      setIndustry('');
      setQuery(name);
      void runSearch(name, { domain: domainId, industry: undefined });
      return;
    }
    if (industryId) {
      const label = industries.find((i) => i.id === industryId)?.label || industryId;
      setIndustry(industryId);
      setDomain('');
      setQuery(label);
      void runSearch(label, { industry: industryId, domain: undefined });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [domainId, industryId, domains, industries]);

  async function explore(match: CatalogMatch, fromGraph = false) {
    if (fromGraph && selected && selected.iri !== match.iri) {
      recordGraphDrill();
    } else if (!fromGraph) {
      clearGraphTrail();
    }
    setSelected(match);
    try {
      const g = await catalogApi.expand(match.iri, 1, [...EXPAND_RELS]);
      setGraph(g);
    } catch {
      setGraph({ nodes: [match], edges: [] });
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (mode === 'overview') navigate('/ontology/classes');
    void runSearch(query);
  }

  function onComposerKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key !== 'Enter' || e.shiftKey || e.nativeEvent.isComposing) return;
    e.preventDefault();
    e.currentTarget.form?.requestSubmit();
  }

  function toggleIndustry(id: string) {
    const next = industry === id ? '' : id;
    setIndustry(next);
    if (query.trim()) {
      void runSearch(query, { industry: next || undefined, domain: domain || undefined });
    }
  }

  if (catalogOk === false) {
    return (
      <div className="page">
        <EmptyState
          title="Ontology is offline"
          body="The catalog agent is offline. Start the gateway and reload this page."
        />
      </div>
    );
  }

  const industryChips = (
    <div className="chip-row industry-chips">
      {industries.map((i) => (
        <button
          key={i.id}
          type="button"
          className={`chip${industry === i.id ? ' active' : ''}`}
          title={i.label}
          onClick={() => toggleIndustry(i.id)}
        >
          {i.label}
        </button>
      ))}
    </div>
  );

  const composer = (
    <form className="composer" onSubmit={onSubmit}>
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={onComposerKeyDown}
        placeholder="Class, preferred label, or definition…"
        rows={2}
      />
      <button className="send-btn" type="submit" disabled={busy} aria-label="Search the catalog">
        {busy ? <Loader2 className="spin" size={16} /> : <ArrowUp size={16} />}
      </button>
    </form>
  );

  const filters = (
    <div className="filter-row">
      <SearchableSelect
        value={domain}
        allLabel="All domain ontologies"
        placeholder="Search domain ontologies…"
        ariaLabel="Domain ontology"
        options={domains.map((d) => ({
          id: d.id,
          label: d.acronym ? `${d.acronym} — ${d.name}` : d.name,
          hint: d.id,
        }))}
        onChange={(next) => {
          setDomain(next);
          if (query.trim()) {
            void runSearch(query, { domain: next || undefined, industry: industry || undefined });
          }
        }}
      />
    </div>
  );

  if (mode === 'overview') {
    return (
      <div className="page">
        <div className="hero">
          <h1>Search the catalog</h1>
          <p>
            Match a preferred label, synonym, or definition to a catalog IRI. Homonyms stay distinct
            by domain (crm:Account is not fin:Account). Optionally scope by domain ontology and
            industry overlay, then search.
          </p>
          {filters}
          {industryChips}
          {composer}
          {error && <p className="error">{error}</p>}
        </div>
      </div>
    );
  }

  const threePane = Boolean(selected);

  return (
    <div className="page-fill">
      <div className={`workspace${threePane ? ' three-pane' : ' two-pane'}`}>
        <div className="workspace-left">
          {filters}
          {industryChips}
          {composer}
          {error && <p className="error">{error}</p>}
          <div className="result-list">
            {visibleMatches.map((m) => {
              const band = scoreBand(m.score, scores);
              return (
                <Card key={m.iri} interactive onClick={() => void explore(m)}>
                  <div className="card-badges">
                    {band && <span className={`badge usage-${band.toLowerCase()}`}>Usage: {band}</span>}
                    {isMapped(m) && <span className="badge mapped">Mapped</span>}
                  </div>
                  <h3>{m.prefLabel || m.localName}</h3>
                  <p className="muted">
                    {ontologyKindLabel(m.kind)}
                    {m.domainId ? ` · ${m.domainId}` : ''}
                    {m.industryId ? ` · ${m.industryId}` : ''}
                  </p>
                  <p>{m.definition || 'No definition on this class.'}</p>
                </Card>
              );
            })}
          </div>
        </div>
        <div className={`workspace-right${threePane ? ' graph-shell' : ' graph-only'}`}>
          <GraphCanvas
            payload={filteredGraph}
            agentPaths={agentPaths}
            onAgentPathsChange={setAgentPaths}
            showMetricsChip={!threePane}
            onSelect={(n) => void explore(n, true)}
            onGoUp={() => {
              if (!restoreGraphUp() && selected) setSelected(null);
            }}
            canGoUp={graphTrail.length > 0 || Boolean(selected)}
            upLabel={
              graphTrail[graphTrail.length - 1]?.selected.prefLabel ||
              graphTrail[graphTrail.length - 1]?.selected.localName ||
              (selected ? 'Results' : undefined)
            }
          />
          {threePane && selected ? (
            <ConceptInspector
              selected={selected}
              graph={filteredGraph}
              agentPaths={agentPaths}
              onClose={() => setSelected(null)}
            />
          ) : null}
        </div>
      </div>
    </div>
  );
}
