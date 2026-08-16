import { ArrowUp, Loader2 } from 'lucide-react';
import { FormEvent, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { catalogApi } from '../../adapters/catalogApi';
import { CATALOG_EXAMPLES, ontologyKindLabel, type CatalogMatch } from '../../contracts/catalog';
import { useApp } from '../AppContext';
import { Card } from '../common/Card';
import { EmptyState } from '../common/EmptyState';
import { GraphCanvas } from '../common/GraphCanvas';
import { catalogDomainId, catalogIndustryId } from '../layout/nav';

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
  const domainId = catalogDomainId(pathname);
  const industryId = catalogIndustryId(pathname);
  const [query, setQuery] = useState('');
  const [domain, setDomain] = useState('');
  const [industry, setIndustry] = useState('');
  const [matches, setMatches] = useState<CatalogMatch[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

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
      if (next[0]) await explore(next[0]);
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
    // Search is driven by the URL; runSearch is stable enough for this mount/route change.
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
      const g = await catalogApi.expand(match.iri, 1, ['subClassOf', 'mapping', 'alignment']);
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

  const composer = (
    <form className="composer" onSubmit={onSubmit}>
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Class, preferred label, or definition…"
        rows={2}
      />
      <button className="send-btn" type="submit" disabled={busy} aria-label="Look up class">
        {busy ? <Loader2 className="spin" size={16} /> : <ArrowUp size={16} />}
      </button>
    </form>
  );

  const filters = (
    <div className="filter-row">
      <select value={domain} onChange={(e) => setDomain(e.target.value)}>
        <option value="">All domain ontologies</option>
        {domains.map((d) => (
          <option key={d.id} value={d.id}>
            {d.name}
          </option>
        ))}
      </select>
      <select value={industry} onChange={(e) => setIndustry(e.target.value)}>
        <option value="">All industry overlays</option>
        {industries.map((i) => (
          <option key={i.id} value={i.id}>
            {i.label}
          </option>
        ))}
      </select>
    </div>
  );

  const examples = (
    <div className="chip-row">
      {CATALOG_EXAMPLES.map((ex) => (
        <button
          key={ex.label}
          className="chip"
          type="button"
          onClick={() => {
            setQuery(ex.query);
            if (ex.domain) setDomain(ex.domain);
            if (ex.industry) setIndustry(ex.industry);
            navigate('/ontology/classes');
            void runSearch(ex.query, { domain: ex.domain, industry: ex.industry });
          }}
        >
          {ex.label}
        </button>
      ))}
    </div>
  );

  if (mode === 'overview') {
    return (
      <div className="page">
        <div className="hero">
          <h1>Look up a class</h1>
          <p>
            The catalog exposes the ontology: preferred labels, alternative labels, definitions, and
            subclass relations. Homonyms stay distinct by domain (crm:Account is not fin:Account).
            Browse domain ontologies and industry overlays in the left navigation.
          </p>
          {filters}
          {composer}
          {examples}
          {error && <p className="error">{error}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="page-fill">
      <div className="workspace">
        <div className="workspace-left">
          {composer}
          {error && <p className="error">{error}</p>}
          <div className="result-list">
            {matches.map((m) => (
              <Card key={m.iri} interactive onClick={() => void explore(m)}>
                <h3>{m.prefLabel || m.localName}</h3>
                <p className="muted">
                  {ontologyKindLabel(m.kind)}
                  {m.domainId ? ` · ${m.domainId}` : ''}
                  {m.industryId ? ` · ${m.industryId}` : ''}
                </p>
                <p>{m.definition || 'No definition on this class.'}</p>
              </Card>
            ))}
          </div>
        </div>
        <div className="workspace-right graph-shell">
          <GraphCanvas
            payload={graph}
            onSelect={(n) => void explore(n, true)}
            onGoUp={() => restoreGraphUp()}
            canGoUp={graphTrail.length > 0}
            upLabel={
              graphTrail[graphTrail.length - 1]?.selected.prefLabel ||
              graphTrail[graphTrail.length - 1]?.selected.localName
            }
          />
          <aside className="graph-inspector">
            {selected ? (
              <>
                <h3>{selected.prefLabel || selected.localName}</h3>
                <p className="muted">
                  {ontologyKindLabel(selected.kind)}
                  {selected.domainId ? ` · ontology ${selected.domainId}` : ''}
                </p>
                <p>{selected.definition || 'No definition on this class.'}</p>
                {(selected.altLabels || []).length > 0 && (
                  <p className="muted">skos:altLabel — {(selected.altLabels || []).join(', ')}</p>
                )}
                <details>
                  <summary className="muted">IRI and local name</summary>
                  <p className="muted">{selected.iri}</p>
                  {selected.localName ? <p className="muted">{selected.localName}</p> : null}
                </details>
              </>
            ) : (
              <p className="muted">Select a class to see preferred label, definition, and IRI.</p>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}
