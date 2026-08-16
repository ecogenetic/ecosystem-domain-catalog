import { Loader2, Plus, Trash2, Upload } from 'lucide-react';
import { DragEvent, FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { catalogApi } from '../../adapters/catalogApi';
import { proposeClassMatches } from '../../adapters/matchDomain';
import {
  addOrUpdateOntology,
  neighborhood,
  overlayDomainMatches,
  patchOntology,
  removeOntology,
  type ClassDomainMatch,
  type SessionLibrary,
  type SessionOntology,
} from '../../adapters/sessionOntology';
import { ontologyKindLabel, type CatalogMatch, type GraphPayload } from '../../contracts/catalog';
import { useApp } from '../AppContext';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { EmptyState } from '../common/EmptyState';
import { GraphCanvas } from '../common/GraphCanvas';
import { TurtleView } from '../common/TurtleView';
import { catalogSessionId } from '../layout/nav';

const SAMPLE = `@prefix : <https://example.com/ontology/demo#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

<https://example.com/ontology/demo> a owl:Ontology ;
    rdfs:label "Demo" .

:Party a owl:Class ;
    skos:prefLabel "Party" ;
    skos:definition "A person or organisation." .

:Customer a owl:Class ;
    rdfs:subClassOf :Party ;
    skos:prefLabel "Customer" ;
    skos:definition "A party the business sells to." .
`;

function displayName(item: SessionOntology): string {
  return item.name.replace(/\.(ttl|owl|rdf|txt)$/i, '') || 'Untitled ontology';
}

function matchFor(matches: ClassDomainMatch[] | undefined, iri: string): ClassDomainMatch | undefined {
  return (matches || []).find((m) => m.classIri === iri);
}

export function SessionOntologyPage() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { sessionLibrary, setSessionLibrary, domains } = useApp();
  const sessionId = catalogSessionId(pathname);
  const adding = !sessionId;
  const active = useMemo(
    () => sessionLibrary.items.find((item) => item.id === sessionId) || null,
    [sessionLibrary.items, sessionId],
  );

  const [turtle, setTurtle] = useState('');
  const [busy, setBusy] = useState(false);
  const [matching, setMatching] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [dragging, setDragging] = useState(false);
  const [showPaste, setShowPaste] = useState(false);
  const [replaceId, setReplaceId] = useState<string | null>(null);
  const [domainId, setDomainId] = useState(active?.matchedDomainId || '');
  const [selected, setSelected] = useState<CatalogMatch | null>(active?.classes[0] || null);
  const [focused, setFocused] = useState<GraphPayload | null>(active?.graph || null);
  const [trail, setTrail] = useState<CatalogMatch[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);
  const uploadTargetRef = useRef<string | null>(null);

  useEffect(() => {
    setSelected(active?.classes[0] || null);
    setFocused(active?.graph || null);
    setTrail([]);
    setReplaceId(null);
    setError('');
    setDomainId(active?.matchedDomainId || '');
  }, [active?.id, active?.version]);

  const graphView = overlayDomainMatches(focused || { nodes: [], edges: [] }, active?.classMatches);
  const sessionIris = new Set((active?.classes || []).map((c) => c.iri));
  const selectedMatch = selected ? matchFor(active?.classMatches, selected.iri) : undefined;
  const acceptedCount = (active?.classMatches || []).filter((m) => m.status === 'accepted').length;

  function persist(next: SessionLibrary) {
    setSessionLibrary(next);
  }

  function saveActive(patch: Partial<SessionOntology>) {
    if (!active) return;
    persist(patchOntology(sessionLibrary, active.id, patch));
  }

  function applyLibrary(next: SessionLibrary, item?: SessionOntology) {
    persist(next);
    const current = item || next.items.find((row) => row.id === next.activeId) || null;
    if (current) navigate(`/ontology/yours/${current.id}`);
    else navigate('/ontology/yours');
  }

  async function ingest(text: string, fileName: string, targetId?: string | null) {
    const body = text.trim();
    if (!body) {
      setError('Drop a .ttl or .owl file, or paste Turtle.');
      return;
    }
    setBusy(true);
    setError('');
    setNotice('');
    try {
      const parsed = await catalogApi.previewOntology(body);
      if (parsed.ok === false) {
        setError(parsed.detail || parsed.error || 'That file could not be parsed as Turtle or RDF/XML.');
        return;
      }
      const result = addOrUpdateOntology(
        sessionLibrary,
        {
          name: fileName.replace(/\.(ttl|owl|rdf|txt)$/i, '') || 'Untitled ontology',
          fileName,
          turtle: body,
          ontologyIri: parsed.ontologyIri,
          graph: { nodes: parsed.nodes || parsed.classes || [], edges: parsed.edges || [] },
          classes: parsed.classes || parsed.nodes || [],
        },
        targetId ? { replaceId: targetId } : { forceAdd: true },
      );
      applyLibrary(result.library, result.item);
      setTurtle('');
      setShowPaste(false);
      setReplaceId(null);
      uploadTargetRef.current = null;
      setNotice(
        result.action === 'updated'
          ? `Updated ${displayName(result.item)} to version ${result.item.version}.`
          : `Added ${displayName(result.item)}. Match it to a catalog domain when you are ready.`,
      );
    } catch {
      setError('Could not reach the catalog agent to parse the file. Restart the gateway on port 8080.');
    } finally {
      setBusy(false);
    }
  }

  function onFile(file: File, targetId?: string | null) {
    const reader = new FileReader();
    reader.onload = () => void ingest(String(reader.result || ''), file.name, targetId);
    reader.readAsText(file);
  }

  function onDrop(e: DragEvent, targetId?: string | null) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) onFile(file, targetId);
  }

  function onPasteSubmit(e: FormEvent) {
    e.preventDefault();
    void ingest(turtle, 'pasted-ontology', replaceId);
  }

  function removeItem(id: string) {
    applyLibrary(removeOntology(sessionLibrary, id));
    setReplaceId(null);
    uploadTargetRef.current = null;
  }

  function openClass(match: CatalogMatch, fromGraph = false) {
    if (!active) return;
    if (fromGraph && selected && selected.iri !== match.iri && sessionIris.has(selected.iri)) {
      setTrail((t) => [...t, selected]);
    } else if (!fromGraph) {
      setTrail([]);
    }
    setSelected(match);
    if (sessionIris.has(match.iri)) {
      setFocused(neighborhood(active.graph, match.iri));
    }
  }

  function goUp() {
    const prev = trail[trail.length - 1];
    if (!prev || !active) return;
    setTrail((t) => t.slice(0, -1));
    setSelected(prev);
    setFocused(neighborhood(active.graph, prev.iri));
  }

  function pickFile(targetId?: string | null) {
    uploadTargetRef.current = targetId || null;
    setReplaceId(targetId || null);
    fileRef.current?.click();
  }

  async function proposeMatches() {
    if (!active || !domainId) {
      setError('Choose a catalog domain first.');
      return;
    }
    setMatching(true);
    setError('');
    try {
      const proposed = await proposeClassMatches(active.classes, domainId);
      saveActive({ matchedDomainId: domainId, classMatches: proposed });
      const n = proposed.filter((m) => m.status === 'proposed').length;
      setNotice(
        n
          ? `Proposed ${n} match${n === 1 ? '' : 'es'} against ${domainId}. Accept in the inspector. Nothing is written to the catalog.`
          : `No catalog classes in ${domainId} looked like this file. Try another domain.`,
      );
    } catch {
      setError('Could not search the catalog to propose matches.');
    } finally {
      setMatching(false);
    }
  }

  function setMatchChoice(classIri: string, catalogIri: string) {
    if (!active) return;
    const rows = (active.classMatches || []).map((m) => {
      if (m.classIri !== classIri) return m;
      const alt = (m.alternatives || []).find((a) => a.iri === catalogIri);
      if (!alt) return m;
      return {
        ...m,
        catalogIri: alt.iri,
        catalogLabel: alt.prefLabel,
        catalogDomain: alt.domainId || domainId,
        catalogDefinition: alt.definition,
      };
    });
    saveActive({ classMatches: rows });
  }

  function acceptMatch(classIri: string) {
    if (!active) return;
    const rows = (active.classMatches || []).map((m) => {
      if (m.classIri !== classIri || !m.catalogIri) return m;
      return { ...m, status: 'accepted' as const };
    });
    saveActive({ classMatches: rows });
  }

  function rejectMatch(classIri: string) {
    if (!active) return;
    saveActive({
      classMatches: (active.classMatches || []).map((m) =>
        m.classIri === classIri ? { ...m, status: 'none' as const } : m,
      ),
    });
  }

  function dropzone(targetId?: string | null) {
    const updating = Boolean(targetId);
    return (
      <button
        type="button"
        className={`dropzone${dragging ? ' active' : ''}${updating ? ' compact' : ''}`}
        disabled={busy}
        onClick={() => pickFile(targetId)}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => onDrop(e, targetId)}
      >
        {busy ? <Loader2 className="spin" size={updating ? 20 : 28} /> : <Upload size={updating ? 20 : 28} />}
        <strong>
          {busy
            ? 'Parsing…'
            : updating
              ? 'Drop a new version of this ontology'
              : sessionLibrary.items.length
                ? 'Drop another .ttl or .owl file'
                : 'Drop a .ttl or .owl file here'}
        </strong>
        <span>
          {updating
            ? 'Replaces this entry and bumps the version'
            : 'Adds a new item under Your ontology in the left panel'}
        </span>
      </button>
    );
  }

  const addForm = (
    <div className="session-intro">
      <h2>{sessionLibrary.items.length ? 'Add another ontology' : 'Upload an ontology to view'}</h2>
      <p>
        {sessionLibrary.items.length
          ? 'This adds a separate file under Your ontology. It does not replace ones already in the list.'
          : 'Load Turtle or OWL, then browse its classes. You can match them to a catalog domain after it opens.'}
        {' '}Closing the tab clears the list. The catalog is not changed.
      </p>
      {error && <p className="error">{error}</p>}
      {dropzone()}
      <div className="session-alt">
        <Button onClick={() => void ingest(SAMPLE, 'demo')}>Try a 2-class sample</Button>
        <Button onClick={() => setShowPaste((v) => !v)}>
          {showPaste ? 'Hide paste box' : 'Paste Turtle instead'}
        </Button>
      </div>
      {showPaste && (
        <form className="session-paste" onSubmit={onPasteSubmit}>
          <textarea
            value={turtle}
            onChange={(e) => setTurtle(e.target.value)}
            rows={10}
            placeholder="@prefix : <https://example.com/ontology/mine#> ."
          />
          <Button variant="cta" disabled={busy} type="submit">
            Add pasted Turtle
          </Button>
        </form>
      )}
    </div>
  );

  return (
    <div className={adding || !active ? 'page session-empty' : 'page-fill'}>
      <input
        ref={fileRef}
        type="file"
        accept=".ttl,.owl,.rdf,.txt,text/turtle,application/rdf+xml"
        hidden
        onChange={(e) => {
          const file = e.target.files?.[0];
          e.target.value = '';
          if (file) onFile(file, uploadTargetRef.current);
        }}
      />
      {adding || !active ? (
        addForm
      ) : (
        <>
          <div className="session-toolbar">
            <span className="name">{displayName(active)}</span>
            <span className="chip">v{active.version}</span>
            <span className="muted">
              {active.classes.length} class{active.classes.length === 1 ? '' : 'es'}
            </span>
            <span className="grow" />
            {notice && <span className="session-notice">{notice}</span>}
            <Button onClick={() => navigate('/ontology/yours')}>
              <Plus size={14} /> Add another
            </Button>
            <Button onClick={() => { setFocused(active.graph); setTrail([]); }}>Show all</Button>
            <Button onClick={() => pickFile(active.id)} disabled={busy}>
              Upload update
            </Button>
            <Button variant="danger" onClick={() => removeItem(active.id)}>
              <Trash2 size={14} /> Remove
            </Button>
          </div>
          <div className="session-toolbar">
            <label className="session-match-label">
              Match to domain
              <select value={domainId} onChange={(e) => setDomainId(e.target.value)}>
                <option value="">Choose a catalog domain…</option>
                {domains.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.acronym || d.id.toUpperCase()} — {d.name}
                  </option>
                ))}
              </select>
            </label>
            <Button variant="primary" onClick={() => void proposeMatches()} disabled={matching || !domainId}>
              {matching ? <Loader2 className="spin" size={14} /> : null}
              {matching ? 'Proposing…' : 'Propose matches'}
            </Button>
            <span className="muted">
              {acceptedCount} accepted · this tab only
            </span>
          </div>
          {error && <p className="error" style={{ padding: '0 16px' }}>{error}</p>}
          {replaceId === active.id && <div className="session-update-banner">{dropzone(active.id)}</div>}
          <div className="workspace">
            <div className="workspace-left">
              <div className="result-list">
                {active.classes.map((m) => {
                  const hit = matchFor(active.classMatches, m.iri);
                  return (
                    <Card key={m.iri} interactive onClick={() => openClass(m)}>
                      <h3>{m.prefLabel || m.localName}</h3>
                      <p className="muted">{ontologyKindLabel(m.kind)}</p>
                      <p>{m.definition || 'No definition on this class.'}</p>
                      {hit?.status === 'accepted' && hit.catalogLabel && (
                        <p className="session-match-ok">Matched to {hit.catalogLabel} ({hit.catalogDomain})</p>
                      )}
                      {hit?.status === 'proposed' && hit.catalogLabel && (
                        <p className="muted">Proposed: {hit.catalogLabel}</p>
                      )}
                    </Card>
                  );
                })}
              </div>
            </div>
            <div className="workspace-right graph-shell">
              {graphView.nodes?.length ? (
                <GraphCanvas
                  payload={graphView}
                  onSelect={(n) => openClass(n, true)}
                  onGoUp={goUp}
                  canGoUp={trail.length > 0}
                  upLabel={trail[trail.length - 1]?.prefLabel || trail[trail.length - 1]?.localName}
                />
              ) : (
                <div className="page">
                  <EmptyState title="No classes" body="This file parsed, but it has no owl:Class or rdfs:Class terms to draw." />
                </div>
              )}
              <aside className="graph-inspector">
                {selected ? (
                  <>
                    <h3>{selected.prefLabel || selected.localName}</h3>
                    <p className="muted">
                      {sessionIris.has(selected.iri) ? ontologyKindLabel(selected.kind) : 'catalog class'}
                      {selected.domainId ? ` · ${selected.domainId}` : ''}
                    </p>
                    <p>{selected.definition || 'No definition on this class.'}</p>
                    {(selected.altLabels || []).length > 0 && (
                      <p className="muted">skos:altLabel — {(selected.altLabels || []).join(', ')}</p>
                    )}
                    <details>
                      <summary className="muted">IRI</summary>
                      <p className="muted">{selected.iri}</p>
                    </details>
                    {sessionIris.has(selected.iri) && selectedMatch && (
                      <div className="match-block">
                        <h3>Match to {domainId || 'a domain'}</h3>
                        {selectedMatch.status === 'none' || !(selectedMatch.alternatives || []).length ? (
                          <p className="muted">No catalog class was proposed. Choose a domain and run Propose matches.</p>
                        ) : (
                          <>
                            <label className="session-match-label">
                              Catalog class
                              <select
                                value={selectedMatch.catalogIri || ''}
                                onChange={(e) => setMatchChoice(selected.iri, e.target.value)}
                              >
                                {(selectedMatch.alternatives || []).map((alt) => (
                                  <option key={alt.iri} value={alt.iri}>
                                    {alt.prefLabel || alt.iri} {alt.domainId ? `(${alt.domainId})` : ''}
                                  </option>
                                ))}
                              </select>
                            </label>
                            {selectedMatch.catalogDefinition && (
                              <p className="muted">{selectedMatch.catalogDefinition}</p>
                            )}
                            <div className="session-alt">
                              {selectedMatch.status !== 'accepted' && (
                                <Button variant="primary" onClick={() => acceptMatch(selected.iri)}>
                                  Accept match
                                </Button>
                              )}
                              <Button onClick={() => rejectMatch(selected.iri)}>Not this</Button>
                              {selectedMatch.catalogDomain && (
                                <Button onClick={() => navigate(`/ontology/domains/${selectedMatch.catalogDomain}`)}>
                                  Open domain
                                </Button>
                              )}
                            </div>
                            {selectedMatch.status === 'accepted' && (
                              <p className="session-match-ok">Accepted for this tab only.</p>
                            )}
                          </>
                        )}
                      </div>
                    )}
                    {!sessionIris.has(selected.iri) && selected.domainId && (
                      <div className="match-block">
                        <p className="muted">This node is a catalog class from a match you accepted.</p>
                        <Button onClick={() => navigate(`/ontology/domains/${selected.domainId}`)}>
                          Open {selected.domainId}
                        </Button>
                      </div>
                    )}
                    {active.turtle ? (
                      <details>
                        <summary className="muted">Turtle in this tab</summary>
                        <TurtleView turtle={active.turtle} />
                      </details>
                    ) : null}
                  </>
                ) : (
                  <p className="muted">Select a class from the list or the graph.</p>
                )}
              </aside>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
