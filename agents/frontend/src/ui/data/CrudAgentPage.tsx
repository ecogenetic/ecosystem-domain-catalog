import { Download, Loader2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { dataApi } from '../../adapters/dataApi';
import type { PhysicalModel } from '../../contracts/data';
import { useApp } from '../AppContext';
import { Button } from '../common/Button';
import { SearchableSelect, type SearchableOption } from '../common/SearchableSelect';

type GenSelection = { kind: 'catalog' | 'session' | 'paste'; id: string };

function parseGenSelection(raw: string): GenSelection {
  if (raw.startsWith('domain:')) return { kind: 'catalog', id: raw.slice('domain:'.length) };
  if (raw.startsWith('session:')) return { kind: 'session', id: raw.slice('session:'.length) };
  return { kind: 'paste', id: '' };
}

function genSelectionValue(sel: GenSelection): string {
  if (sel.kind === 'catalog') return `domain:${sel.id}`;
  if (sel.kind === 'session') return `session:${sel.id}`;
  return '';
}

type CrudPreview = {
  target: string;
  tableCount: number;
  header: string;
  files: Record<string, string>;
  zipBase64: string;
  fileName: string;
  model: PhysicalModel | null;
};

function downloadBase64Zip(base64: string, filename: string) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  const blob = new Blob([bytes], { type: 'application/zip' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function CrudAgentPage() {
  const { domains, industries, sessionLibrary } = useApp();
  const [searchParams] = useSearchParams();
  const initialDomain = searchParams.get('domain') || '';
  const [genSelection, setGenSelection] = useState<GenSelection>(
    initialDomain ? { kind: 'catalog', id: initialDomain } : { kind: 'paste', id: '' },
  );
  const [genIndustry, setGenIndustry] = useState(searchParams.get('industry') || '');
  const [genTurtle, setGenTurtle] = useState('');
  const [genTarget, setGenTarget] = useState<'postgresql' | 'mongodb'>('postgresql');
  const [preview, setPreview] = useState<CrudPreview | null>(null);
  const [fileTab, setFileTab] = useState('README.md');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const sessionId = sessionStorage.getItem('ecosystem.crud.sessionId');
    const stored = sessionStorage.getItem('ecosystem.crud.turtle');
    if (sessionId) {
      setGenSelection({ kind: 'session', id: sessionId });
      sessionStorage.removeItem('ecosystem.crud.sessionId');
    }
    if (stored) {
      setGenTurtle(stored);
      sessionStorage.removeItem('ecosystem.crud.turtle');
    }
  }, []);

  const selectedSession = genSelection.kind === 'session'
    ? sessionLibrary.items.find((row) => row.id === genSelection.id)
    : undefined;

  const catalogDomainOptions = useMemo((): SearchableOption[] => {
    const sessionOpts: SearchableOption[] = sessionLibrary.items.map((item) => ({
      id: `session:${item.id}`,
      label: item.name,
      sub: `${item.classes.length} classes · this session`,
      group: 'Your ontologies',
      tone: 'session',
    }));
    const catalogOpts: SearchableOption[] = domains.map((d) => ({
      id: `domain:${d.id}`,
      label: `${d.acronym || d.id.toUpperCase()} — ${d.name}`,
      sub: d.id,
      group: 'Catalog',
    }));
    return [...sessionOpts, ...catalogOpts];
  }, [domains, sessionLibrary.items]);

  function ontologyPayload(): { domainId?: string; industry?: string; turtle?: string } {
    if (genSelection.kind === 'catalog' && genSelection.id) {
      return { domainId: genSelection.id, industry: genIndustry || undefined };
    }
    const turtle = (genSelection.kind === 'session' ? selectedSession?.turtle : genTurtle) || '';
    return { turtle: turtle.trim() || undefined };
  }

  async function buildPreview() {
    setBusy(true);
    setError('');
    try {
      const payload = ontologyPayload();
      if (!payload.domainId && !payload.turtle) {
        setError('Choose a catalog domain, one of your ontologies, or paste Turtle.');
        return;
      }
      const res = await dataApi.generateCrudAgent({ ...payload, target: genTarget });
      if (!res.ok || !res.files || !res.zipBase64) {
        setError((res as { error?: string }).error || 'Could not build the CRUD agent package.');
        return;
      }
      const fileNames = Object.keys(res.files);
      const preferred = fileNames.includes('README.md')
        ? 'README.md'
        : fileNames.includes('app.py')
          ? 'app.py'
          : fileNames[0];
      setFileTab(preferred || 'README.md');
      setPreview({
        target: res.target || genTarget,
        tableCount: res.tableCount || 0,
        header: res.header || '',
        files: res.files,
        zipBase64: res.zipBase64,
        fileName: `crud-agent-${res.target || genTarget}.zip`,
        model: res.model || null,
      });
    } catch {
      setError('CRUD agent build failed. Check domain selection or Turtle syntax.');
    } finally {
      setBusy(false);
    }
  }

  function downloadZip() {
    if (!preview?.zipBase64) {
      void buildPreview();
      return;
    }
    downloadBase64Zip(preview.zipBase64, preview.fileName);
  }

  const fileNames = preview ? Object.keys(preview.files) : [];

  return (
    <div className="page crud-agent-page">
      <div className="crud-agent-toolbar">
        <div className="crud-agent-toolbar-copy">
          <h3>CRUD agent</h3>
          <p className="muted">
            Build a downloadable Python 3.14 agent from a catalog domain or your ontology. Preview the package here,
            then download the zip.
          </p>
        </div>
        <div className="crud-agent-controls">
          <div className="form-group crud-agent-ontology">
            <label>Ontology</label>
            <div className="crud-agent-ontology-row">
              <SearchableSelect
                className="select-catalog-domain"
                value={genSelectionValue(genSelection)}
                allLabel={sessionLibrary.items.length ? 'Paste Turtle' : 'Session Turtle only'}
                placeholder="Search catalog or your ontologies…"
                ariaLabel="Ontology for CRUD agent"
                options={catalogDomainOptions}
                onChange={(id) => {
                  const next = parseGenSelection(id);
                  setGenSelection(next);
                  setPreview(null);
                  if (next.kind === 'session') {
                    const item = sessionLibrary.items.find((row) => row.id === next.id);
                    if (item?.turtle) setGenTurtle(item.turtle);
                  }
                  if (next.kind !== 'catalog') setGenIndustry('');
                }}
              />
              {genSelection.kind === 'session' && selectedSession && (
                <p className="muted crud-agent-session-note">
                  Using “{selectedSession.name}” ({selectedSession.classes.length} classes).
                </p>
              )}
            </div>
          </div>
          {genSelection.kind === 'catalog' && (
            <div className="form-group">
              <label>Industry overlay</label>
              <select
                value={genIndustry}
                onChange={(e) => {
                  setGenIndustry(e.target.value);
                  setPreview(null);
                }}
              >
                <option value="">Base domain only</option>
                {industries.map((i) => (
                  <option key={i.id} value={i.id}>
                    {i.label}
                  </option>
                ))}
              </select>
            </div>
          )}
          {genSelection.kind === 'paste' && (
            <div className="form-group crud-agent-turtle">
              <label>Session Turtle</label>
              <textarea
                value={genTurtle}
                onChange={(e) => {
                  setGenTurtle(e.target.value);
                  setPreview(null);
                }}
                rows={4}
                placeholder="@prefix : <https://example.com/ontology/mine#> ."
              />
            </div>
          )}
          <div className="form-group crud-agent-target">
            <label>Database target</label>
            <div className="crud-agent-target-row">
              <div className="chip-row">
                <button
                  className={`chip${genTarget === 'postgresql' ? ' active' : ''}`}
                  type="button"
                  onClick={() => {
                    setGenTarget('postgresql');
                    setPreview(null);
                  }}
                >
                  PostgreSQL
                </button>
                <button
                  className={`chip${genTarget === 'mongodb' ? ' active' : ''}`}
                  type="button"
                  onClick={() => {
                    setGenTarget('mongodb');
                    setPreview(null);
                  }}
                >
                  MongoDB
                </button>
              </div>
              <Button variant="primary" disabled={busy} onClick={() => void buildPreview()}>
                {busy ? <Loader2 className="spin" size={16} /> : null} Build agent
              </Button>
              <Button disabled={busy || !preview} onClick={() => downloadZip()}>
                <Download size={14} /> Download zip
              </Button>
            </div>
          </div>
        </div>
        {error && <p className="error">{error}</p>}
      </div>

      {!preview && !busy && (
        <div className="crud-agent-empty">
          <p className="muted">Choose an ontology and target, then Build agent to inspect the package.</p>
        </div>
      )}

      {preview && (
        <div className="workspace crud-agent-workspace">
          <div className="workspace-left crud-agent-aside">
            <div className="crud-agent-meta">
              <strong>
                {preview.target} · {preview.tableCount} tables
              </strong>
              <p className="muted">{preview.fileName}</p>
            </div>
            <div className="crud-agent-file-list" role="tablist" aria-label="Package files">
              {fileNames.map((name) => (
                <button
                  key={name}
                  type="button"
                  role="tab"
                  aria-selected={fileTab === name}
                  className={`crud-agent-file${fileTab === name ? ' active' : ''}`}
                  onClick={() => setFileTab(name)}
                >
                  {name}
                </button>
              ))}
            </div>
            {preview.model?.tables && (
              <details className="crud-agent-tables">
                <summary className="muted">{preview.model.tables.length} tables</summary>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Table</th>
                      <th>Class</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.model.tables.map((t) => (
                      <tr key={t.table}>
                        <td>{t.table}</td>
                        <td>{t.entity}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </details>
            )}
            {preview.header && (
              <details className="crud-agent-header-block">
                <summary className="muted">Connection</summary>
                <pre className="pre">{preview.header}</pre>
              </details>
            )}
          </div>
          <div className="workspace-right crud-agent-code">
            <div className="crud-agent-code-title">{fileTab}</div>
            <pre className="pre crud-agent-code-body">{preview.files[fileTab] || ''}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
