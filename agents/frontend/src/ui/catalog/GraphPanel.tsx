import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { catalogApi } from '../../adapters/catalogApi';
import { EXPAND_RELS, type CatalogMatch, type GraphPayload } from '../../contracts/catalog';
import { useApp } from '../AppContext';
import { Button } from '../common/Button';
import { EmptyState } from '../common/EmptyState';
import { GraphCanvas } from '../common/GraphCanvas';
import { TurtleView } from '../common/TurtleView';
import { ConceptInspector } from './ConceptInspector';

const RELS = [
  { id: 'subClassOf', label: 'rdfs:subClassOf' },
  { id: 'equivalentClass', label: 'owl:equivalentClass' },
  { id: 'mapping', label: 'mapped to' },
  { id: 'alignment', label: 'aligned with' },
  { id: 'objectProperty', label: 'object property' },
];
const NODE_CAP = 150;

function capGraph(g: GraphPayload): { graph: GraphPayload; truncated: boolean } {
  const nodes = (g.nodes || []).slice(0, NODE_CAP);
  const keep = new Set(nodes.map((n) => n.iri));
  const edges = (g.edges || []).filter((e) => keep.has(e.from) && keep.has(e.to));
  return { graph: { ...g, nodes, edges }, truncated: (g.nodes || []).length > NODE_CAP };
}

function classLabel(c: CatalogMatch): string {
  return c.prefLabel || c.localName || c.iri;
}

export function GraphPanel({ advanced }: { advanced?: boolean }) {
  const {
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
  const [searchParams, setSearchParams] = useSearchParams();
  const agentPaths = searchParams.get('overlay') === 'paths';
  const setAgentPaths = (on: boolean) => {
    const next = new URLSearchParams(searchParams);
    if (on) next.set('overlay', 'paths');
    else next.delete('overlay');
    setSearchParams(next, { replace: true });
  };
  const [depth, setDepth] = useState(2);
  const [rels, setRels] = useState<string[]>([...EXPAND_RELS]);
  const [turtle, setTurtle] = useState('');
  const [truncated, setTruncated] = useState(false);
  const [busy, setBusy] = useState(false);
  const [domainId, setDomainId] = useState(selected?.domainId || '');
  const [industryId, setIndustryId] = useState(selected?.industryId || '');
  const [classes, setClasses] = useState<CatalogMatch[]>([]);

  async function loadClasses(nextDomain: string, nextIndustry?: string) {
    if (!nextDomain) {
      setClasses([]);
      return [];
    }
    const ont = await catalogApi.ontology(nextDomain, nextIndustry || undefined);
    const next = [...(ont.classes || [])].sort((a, b) => classLabel(a).localeCompare(classLabel(b)));
    setClasses(next);
    setTurtle(ont.turtle || '');
    return next;
  }

  async function expand(match: CatalogMatch, nextDepth = depth) {
    setSelected(match);
    setBusy(true);
    try {
      const raw = await catalogApi.expand(match.iri, nextDepth, rels);
      const { graph: next, truncated: tooBig } = capGraph(raw);
      setGraph(next);
      setTruncated(tooBig);
      if (match.domainId) {
        const ont = await catalogApi.ontology(match.domainId, match.industryId);
        setTurtle(ont.turtle || '');
      }
    } catch {
      setGraph({ nodes: [match], edges: [] });
    } finally {
      setBusy(false);
    }
  }

  async function pickDomain(nextDomain: string) {
    setDomainId(nextDomain);
    setIndustryId('');
    clearGraphTrail();
    if (!nextDomain) {
      setClasses([]);
      setGraph(null);
      setSelected(null);
      return;
    }
    const next = await loadClasses(nextDomain);
    if (next[0]) await expand(next[0], depth);
  }

  async function pickIndustry(nextIndustry: string) {
    setIndustryId(nextIndustry);
    clearGraphTrail();
    if (!domainId) return;
    const next = await loadClasses(domainId, nextIndustry || undefined);
    if (next[0]) await expand(next[0], depth);
  }

  async function pickClass(iri: string) {
    const match = classes.find((c) => c.iri === iri);
    if (!match) return;
    clearGraphTrail();
    await expand(match, depth);
  }

  useEffect(() => {
    if (!selected?.domainId || domainId) return;
    setDomainId(selected.domainId);
    setIndustryId(selected.industryId || '');
    void loadClasses(selected.domainId, selected.industryId);
    // Sync dropdowns when arriving from a class lookup; do not replace the open graph.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected]);

  const hasGraph = Boolean(graph?.nodes?.length);
  const threePane = Boolean(selected);

  return (
    <div className="page-fill">
      <div className={threePane ? 'graph-shell' : 'graph-shell two-pane'}>
        <div className="graph-col">
          <div className="filter-row" style={{ justifyContent: 'flex-start', padding: 12 }}>
            <select
              value={domainId}
              onChange={(e) => void pickDomain(e.target.value)}
              aria-label="Domain ontology"
            >
              <option value="">Choose a domain ontology…</option>
              {domains.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.acronym || d.id.toUpperCase()} — {d.name}
                </option>
              ))}
            </select>
            <select
              value={industryId}
              onChange={(e) => void pickIndustry(e.target.value)}
              aria-label="Industry overlay"
              disabled={!domainId}
            >
              <option value="">Base ontology</option>
              {industries.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.label}
                </option>
              ))}
            </select>
            <select
              value={selected?.iri || ''}
              onChange={(e) => void pickClass(e.target.value)}
              aria-label="Starting class"
              disabled={!classes.length}
              style={{ minWidth: 220 }}
            >
              <option value="">{classes.length ? 'Choose a class…' : 'Classes appear after a domain'}</option>
              {classes.map((c) => (
                <option key={c.iri} value={c.iri}>
                  {classLabel(c)}
                </option>
              ))}
            </select>
            {advanced && (
              <>
                <label className="toggle">
                  Depth
                  <input
                    type="number"
                    min={1}
                    max={4}
                    value={depth}
                    onChange={(e) => setDepth(Number(e.target.value) || 1)}
                    style={{ width: 64 }}
                  />
                </label>
                {RELS.map((r) => (
                  <label key={r.id} className="toggle">
                    <input
                      type="checkbox"
                      checked={rels.includes(r.id)}
                      onChange={(e) =>
                        setRels((cur) => (e.target.checked ? [...cur, r.id] : cur.filter((x) => x !== r.id)))
                      }
                    />
                    {r.label}
                  </label>
                ))}
                <Button disabled={!selected || busy} onClick={() => selected && void expand(selected, depth)}>
                  Expand
                </Button>
              </>
            )}
          </div>
          {truncated && (
            <p className="muted" style={{ padding: '0 12px' }}>
              Too large — constrain the class expansion (showing {NODE_CAP} classes).
            </p>
          )}
          {hasGraph ? (
            <GraphCanvas
              payload={graph}
              agentPaths={agentPaths}
              onAgentPathsChange={setAgentPaths}
              showMetricsChip={!threePane}
              onSelect={(n) => {
                if (selected && n.iri !== selected.iri) recordGraphDrill();
                void expand(n, 1);
              }}
              onGoUp={() => {
                if (!restoreGraphUp()) setSelected(null);
              }}
              canGoUp={graphTrail.length > 0 || Boolean(selected)}
              upLabel={
                graphTrail[graphTrail.length - 1]?.selected.prefLabel ||
                graphTrail[graphTrail.length - 1]?.selected.localName ||
                (selected ? 'Results' : undefined)
              }
            />
          ) : (
            <div className="page">
              <EmptyState
                title="Choose a hierarchy"
                body="Pick a domain ontology above to open its class tree. Click a node to go deeper; use Up to return to the previous class."
              />
            </div>
          )}
        </div>
        {threePane && selected ? (
          <ConceptInspector
            selected={selected}
            graph={graph}
            agentPaths={agentPaths}
            onClose={() => setSelected(null)}
            footer={
              turtle ? (
                <details>
                  <summary className="muted">Domain Turtle</summary>
                  <TurtleView turtle={turtle} />
                </details>
              ) : null
            }
          />
        ) : null}
      </div>
    </div>
  );
}
