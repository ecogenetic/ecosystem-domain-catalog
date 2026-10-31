import { Download, Loader2, Pencil, Plus, ShieldCheck, Trash2, Upload } from 'lucide-react';
import { DragEvent, FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { catalogApi } from '../../adapters/catalogApi';
import { proposeClassMatches } from '../../adapters/matchDomain';
import {
  addOrUpdateOntology,
  downloadSessionBundle,
  mergeSessionLibrary,
  neighborhood,
  overlayDomainMatches,
  parseSessionBundle,
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
import { ConceptInspector } from './ConceptInspector';
import {
  OntologyValidationModal,
  type ValidationRecommendation,
  type ValidationReportPayload,
} from './OntologyValidationModal';

function downloadTextFile(filename: string, text: string, mime = 'text/plain') {
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

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
  const [copyDomainId, setCopyDomainId] = useState('');
  const [editing, setEditing] = useState(false);
  const [draftTurtle, setDraftTurtle] = useState('');
  const [selected, setSelected] = useState<CatalogMatch | null>(active?.classes[0] || null);
  const [focused, setFocused] = useState<GraphPayload | null>(active?.graph || null);
  const [trail, setTrail] = useState<CatalogMatch[]>([]);
  const [agentPaths, setAgentPaths] = useState(false);
  const [validating, setValidating] = useState(false);
  const [validationOpen, setValidationOpen] = useState(false);
  const [validationReport, setValidationReport] = useState<ValidationReportPayload | null>(null);
  const [selectedRecIds, setSelectedRecIds] = useState<string[]>([]);
  const [lastApplyFeedback, setLastApplyFeedback] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const sessionFileRef = useRef<HTMLInputElement>(null);
  const uploadTargetRef = useRef<string | null>(null);

  useEffect(() => {
    setSelected(active?.classes[0] || null);
    setFocused(active?.graph || null);
    setTrail([]);
    setReplaceId(null);
    setError('');
    setDomainId(active?.matchedDomainId || '');
    setEditing(false);
    setDraftTurtle(active?.turtle || '');
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

  async function runValidation() {
    if (!active?.turtle) return;
    setValidating(true);
    setError('');
    try {
      const report = await catalogApi.validateOntology({
        turtle: active.turtle,
        includeRecommendations: true,
      });
      setValidationReport(report);
      setSelectedRecIds((report.recommendations || []).filter((r) => r.suggestedTtl).map((r) => r.id));
      setValidationOpen(true);
      const errs = report.summary?.errors ?? 0;
      const warns = report.summary?.warnings ?? 0;
      setNotice(
        report.summary?.passed
          ? `RDF 1.2 · OWL · SHACL · SKOS Validated${warns ? ` (${warns} warning${warns === 1 ? '' : 's'})` : ''}`
          : `Validation found ${errs} error${errs === 1 ? '' : 's'}, ${warns} warning${warns === 1 ? '' : 's'}`,
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Validation failed');
    } finally {
      setValidating(false);
    }
  }

  async function applyRecommendationsToActive(
    recsToApply: ValidationRecommendation[],
    customTtl?: string,
  ) {
    if (!active?.turtle) return;
    if (!recsToApply.length && !customTtl?.trim()) return;
    setValidating(true);
    setError('');
    try {
      const result = await catalogApi.applyOntologyRecommendations({
        turtle: active.turtle,
        recommendations: recsToApply,
        customTtl,
      });
      const nextTurtle = result.content || active.turtle;
      let nextClasses = active.classes;
      let nextGraph = active.graph;
      let nextIri = active.ontologyIri;
      try {
        const preview = await catalogApi.previewOntology(nextTurtle);
        if (preview && preview.ok !== false) {
          nextClasses = preview.classes || preview.nodes || active.classes;
          nextGraph = {
            nodes: preview.nodes || preview.classes || [],
            edges: preview.edges || [],
          };
          nextIri = preview.ontologyIri || active.ontologyIri;
        }
      } catch {
        /* keep existing graph if preview fails on partial syntax */
      }
      const nextVersion = (active.version || 1) + 1;
      saveActive({
        turtle: nextTurtle,
        version: nextVersion,
        classes: nextClasses,
        graph: nextGraph,
        ontologyIri: nextIri,
      });
      setFocused(nextGraph);
      setDraftTurtle(nextTurtle);
      const count = result.applied?.length || recsToApply.length || 1;
      const msg = `Applied ${count} recommendation${count === 1 ? '' : 's'} to ${displayName(active)} (now v${nextVersion}).`;
      setNotice(msg);
      setLastApplyFeedback(msg);
      const refreshed =
        (result.validation as ValidationReportPayload | undefined) ||
        (await catalogApi.validateOntology({
          turtle: nextTurtle,
          includeRecommendations: true,
        }));
      setValidationReport(refreshed);
      setSelectedRecIds(
        (refreshed.recommendations || []).filter((r) => r.suggestedTtl).map((r) => r.id),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Apply recommendations failed');
    } finally {
      setValidating(false);
    }
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

  function importSessionText(text: string) {
    const parsed = parseSessionBundle(text);
    if (!parsed.ok) {
      setError(parsed.error);
      return;
    }
    const merged = mergeSessionLibrary(sessionLibrary, parsed.library);
    persist(merged.library);
    const active = merged.library.items.find((item) => item.id === merged.library.activeId);
    setNotice(
      `Loaded saved session (${merged.added} added, ${merged.updated} updated). Matches and actions are restored.`,
    );
    setError('');
    if (active) navigate(`/ontology/yours/${active.id}`);
    else navigate('/ontology/yours');
  }

  function onFile(file: File, targetId?: string | null) {
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result || '');
      const looksLikeSession =
        /\.ecosystem-session\.json$/i.test(file.name) ||
        (/\.json$/i.test(file.name) && text.includes('ecosystem.ontology.session'));
      if (looksLikeSession) {
        importSessionText(text);
        return;
      }
      void ingest(text, file.name, targetId);
    };
    reader.readAsText(file);
  }

  function onSessionFile(file: File) {
    const reader = new FileReader();
    reader.onload = () => importSessionText(String(reader.result || ''));
    reader.readAsText(file);
  }

  function onDrop(e: DragEvent, targetId?: string | null) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) onFile(file, targetId);
  }

  function downloadActiveOrLibrary() {
    if (!sessionLibrary.items.length) {
      setError('Nothing to download yet. Add an ontology first.');
      return;
    }
    downloadSessionBundle(sessionLibrary, active?.id);
    setNotice(
      active
        ? `Downloaded “${displayName(active)}” with matches and session actions.`
        : 'Downloaded your ontology session library.',
    );
  }

  function downloadActiveTurtle() {
    if (!active?.turtle) {
      setError('No Turtle to download on this ontology.');
      return;
    }
    downloadTextFile(`${displayName(active)}.ttl`, active.turtle, 'text/turtle');
    setNotice(`Downloaded ${displayName(active)}.ttl`);
  }

  function startEdit() {
    if (!active) return;
    setDraftTurtle(active.turtle || '');
    setEditing(true);
    setError('');
    setNotice('Edit the Turtle, then Apply to re-parse and bump the version. The catalog is not changed.');
  }

  async function applyEdit() {
    if (!active) return;
    await ingest(draftTurtle, active.fileName || `${displayName(active)}.ttl`, active.id);
    setEditing(false);
  }

  function cancelEdit() {
    setEditing(false);
    setDraftTurtle(active?.turtle || '');
    setNotice('');
  }

  async function copyFromCatalog(domain: string) {
    if (!domain) {
      setError('Choose a catalog domain to copy.');
      return;
    }
    setBusy(true);
    setError('');
    setNotice('');
    try {
      const ont = await catalogApi.ontology(domain);
      const body = (ont.turtle || '').trim();
      if (!body) {
        setError(`No Turtle is available for ${domain}.`);
        return;
      }
      const meta = domains.find((d) => d.id === domain);
      const label = meta?.acronym || domain.toUpperCase();
      await ingest(body, `${label}-yours.ttl`);
      setCopyDomainId('');
      setNotice(
        `Copied ${label} into Your ontology. Edit freely — this is your copy; the catalog is unchanged.`,
      );
    } catch {
      setError('Could not load that catalog domain. Check the gateway and try again.');
    } finally {
      setBusy(false);
    }
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
            : 'Adds a .ttl/.owl under Your ontology, or restores a .ecosystem-session.json'}
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
          : 'Load Turtle or OWL, start from a catalog domain as your editable copy, then browse and change classes.'}
        {' '}
        Closing the tab clears the browser list — download Turtle or a session file to keep your work. The catalog is
        not changed.
      </p>
      {error && <p className="error">{error}</p>}
      {notice && <p className="session-notice">{notice}</p>}
      {dropzone()}
      <div className="session-copy-catalog">
        <label className="session-match-label">
          Start from catalog domain
          <select
            value={copyDomainId}
            onChange={(e) => setCopyDomainId(e.target.value)}
            aria-label="Catalog domain to copy into Your ontology"
          >
            <option value="">Choose a domain…</option>
            {domains.map((d) => (
              <option key={d.id} value={d.id}>
                {d.acronym || d.id.toUpperCase()} — {d.name}
              </option>
            ))}
          </select>
        </label>
        <Button
          variant="primary"
          disabled={busy || !copyDomainId}
          onClick={() => void copyFromCatalog(copyDomainId)}
        >
          {busy ? <Loader2 className="spin" size={14} /> : null}
          Use as my ontology
        </Button>
      </div>
      <div className="session-alt">
        <Button onClick={() => void ingest(SAMPLE, 'demo')}>Try a 2-class sample</Button>
        <Button onClick={() => setShowPaste((v) => !v)}>
          {showPaste ? 'Hide paste box' : 'Paste Turtle instead'}
        </Button>
        <Button onClick={() => sessionFileRef.current?.click()}>
          <Upload size={14} /> Upload saved session
        </Button>
        {sessionLibrary.items.length > 0 && (
          <Button onClick={() => downloadSessionBundle(sessionLibrary)}>
            <Download size={14} /> Download all sessions
          </Button>
        )}
      </div>
      {showPaste && (
        <form className="session-paste" onSubmit={onPasteSubmit}>
          <textarea
            value={turtle}
            onChange={(e) => setTurtle(e.target.value)}
            rows={10}
            placeholder="@prefix : <https://example.com/ontology/mine#> ."
          />
          <Button variant="primary" disabled={busy} type="submit">
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
        accept=".ttl,.owl,.rdf,.txt,.json,.ecosystem-session.json,text/turtle,application/rdf+xml,application/json"
        hidden
        onChange={(e) => {
          const file = e.target.files?.[0];
          e.target.value = '';
          if (file) onFile(file, uploadTargetRef.current);
        }}
      />
      <input
        ref={sessionFileRef}
        type="file"
        accept=".json,.ecosystem-session.json,application/json"
        hidden
        onChange={(e) => {
          const file = e.target.files?.[0];
          e.target.value = '';
          if (file) onSessionFile(file);
        }}
      />
      {adding || !active ? (
        addForm
      ) : (
        <>
          <div className="session-toolbar session-toolbar-title">
            <span className="name">{displayName(active)}</span>
            <span className="chip">v{active.version}</span>
            <span className="muted">
              {active.classes.length} class{active.classes.length === 1 ? '' : 'es'}
              {acceptedCount ? ` · ${acceptedCount} matched` : ''}
            </span>
            <span className="grow" />
            {notice && <span className="session-notice">{notice}</span>}
            <Button onClick={() => navigate('/ontology/yours')}>
              <Plus size={14} /> Add another
            </Button>
            <Button variant="danger" onClick={() => removeItem(active.id)}>
              <Trash2 size={14} /> Remove
            </Button>
          </div>
          <div className="session-action-bar">
            <div className="session-action-group">
              <span className="session-action-label">Ontology</span>
              <div className="session-action-buttons">
                <Button onClick={startEdit} disabled={busy || !active.turtle} title="Edit Turtle for this ontology">
                  <Pencil size={14} /> Edit Turtle
                </Button>
                <Button onClick={() => pickFile(active.id)} disabled={busy} title="Replace with a new .ttl / .owl file">
                  <Upload size={14} /> Replace file
                </Button>
                <Button
                  onClick={() => void runValidation()}
                  disabled={validating || !active.turtle}
                  title="Validate & Recommendations"
                >
                  {validating ? <Loader2 size={14} className="spin" /> : <ShieldCheck size={14} />}
                  Validate
                </Button>
                <Button onClick={() => { setFocused(active.graph); setTrail([]); }} title="Show the full class graph">
                  Show all
                </Button>
              </div>
            </div>
            <div className="session-action-group">
              <span className="session-action-label">Save / restore</span>
              <div className="session-action-buttons">
                <Button onClick={downloadActiveTurtle} disabled={!active.turtle} title="Download Turtle (.ttl)">
                  <Download size={14} /> .ttl
                </Button>
                <Button onClick={downloadActiveOrLibrary} title="Download ontology plus matches and actions">
                  <Download size={14} /> Session
                </Button>
                <Button onClick={() => sessionFileRef.current?.click()} title="Restore a previously downloaded session">
                  <Upload size={14} /> Session
                </Button>
              </div>
            </div>
            <div className="session-action-group">
              <span className="session-action-label">Catalog match</span>
              <div className="session-action-buttons">
                <label className="session-match-label">
                  <span className="visually-hidden">Match to domain</span>
                  <select
                    value={domainId}
                    onChange={(e) => setDomainId(e.target.value)}
                    aria-label="Catalog domain to match against"
                  >
                    <option value="">Choose a domain…</option>
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
              </div>
            </div>
            <div className="session-action-group">
              <span className="session-action-label">Build</span>
              <div className="session-action-buttons">
                <Button
                  disabled={!active.turtle}
                  onClick={() => {
                    sessionStorage.setItem('ecosystem.generate.sessionId', active.id);
                    sessionStorage.setItem('ecosystem.generate.turtle', active.turtle);
                    navigate('/sources/generate');
                  }}
                >
                  Generate schema
                </Button>
                <Button
                  disabled={!active.turtle}
                  onClick={() => {
                    sessionStorage.setItem('ecosystem.crud.sessionId', active.id);
                    sessionStorage.setItem('ecosystem.crud.turtle', active.turtle);
                    navigate('/sources/crud');
                  }}
                >
                  CRUD agent
                </Button>
              </div>
            </div>
          </div>
          {error && <p className="error" style={{ padding: '0 16px' }}>{error}</p>}
          {validationReport && (
            <div className="val-summary-strip" onClick={() => setValidationOpen(true)} role="button" tabIndex={0}>
              <ShieldCheck size={14} style={{ color: 'var(--primary)' }} />
              <strong>
                {validationReport.summary?.passed
                  ? 'RDF 1.2 · OWL · SHACL · SKOS Validated'
                  : `Validation: ${validationReport.summary?.errors ?? 0} error(s), ${validationReport.summary?.warnings ?? 0} warning(s)`}
              </strong>
              <span className="muted">
                {(validationReport.issues || []).length} finding(s) ·{' '}
                {(validationReport.recommendations || []).length} recommendation(s)
              </span>
              <span className="grow" />
              <span style={{ color: 'var(--primary)', fontWeight: 600 }}>
                Open Validation &amp; Recommendations Modal →
              </span>
            </div>
          )}
          <OntologyValidationModal
            open={validationOpen}
            onClose={() => setValidationOpen(false)}
            ontologyName={displayName(active)}
            turtle={active.turtle}
            report={validationReport}
            busy={validating}
            selectedRecIds={selectedRecIds}
            onToggleRec={(id) =>
              setSelectedRecIds((prev) =>
                prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
              )
            }
            onSelectAllRecs={(ids) => setSelectedRecIds(ids)}
            onRevalidate={() => void runValidation()}
            onApplyRecommendations={(recs, customTtl) =>
              void applyRecommendationsToActive(recs, customTtl)
            }
            lastApplyFeedback={lastApplyFeedback}
          />
          {replaceId === active.id && <div className="session-update-banner">{dropzone(active.id)}</div>}
          {editing && (
            <div className="session-edit-panel">
              <div className="session-edit-head">
                <strong>Edit Turtle</strong>
                <span className="muted">Apply re-parses the graph and bumps the version. Catalog stays unchanged.</span>
                <span className="grow" />
                <Button variant="primary" disabled={busy} onClick={() => void applyEdit()}>
                  {busy ? <Loader2 className="spin" size={14} /> : null}
                  Apply changes
                </Button>
                <Button disabled={busy} onClick={cancelEdit}>
                  Cancel
                </Button>
              </div>
              <textarea
                className="session-edit-turtle"
                value={draftTurtle}
                onChange={(e) => setDraftTurtle(e.target.value)}
                spellCheck={false}
                aria-label="Edit ontology Turtle"
              />
            </div>
          )}
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
                  focusIri={selected?.iri}
                  agentPaths={agentPaths}
                  onAgentPathsChange={setAgentPaths}
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
              {selected ? (
                <ConceptInspector
                  selected={selected}
                  graph={graphView}
                  agentPaths={agentPaths}
                  fetchCatalog={!sessionIris.has(selected.iri)}
                  footer={
                    <>
                      {sessionIris.has(selected.iri) && selectedMatch && (
                        <div className="match-block">
                          <h4>Match to {domainId || 'a domain'}</h4>
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
                          <div className="session-alt" style={{ marginBottom: 8 }}>
                            <Button onClick={startEdit}>
                              <Pencil size={14} /> Edit
                            </Button>
                            <Button onClick={downloadActiveTurtle}>
                              <Download size={14} /> Download .ttl
                            </Button>
                          </div>
                          <TurtleView turtle={active.turtle} />
                        </details>
                      ) : null}
                    </>
                  }
                />
              ) : (
                <aside className="graph-inspector">
                  <p className="muted">Select a class from the list or the graph.</p>
                </aside>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
