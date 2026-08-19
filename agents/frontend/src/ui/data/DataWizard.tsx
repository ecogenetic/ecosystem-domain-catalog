import { ArrowUp, Loader2 } from 'lucide-react';
import { FormEvent, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { dataApi } from '../../adapters/dataApi';
import { DATA_EXAMPLES, type QueryResult } from '../../contracts/data';
import { useApp } from '../AppContext';
import { Button } from '../common/Button';
import { Card } from '../common/Card';
import { EmptyState } from '../common/EmptyState';
import { GraphCanvas } from '../common/GraphCanvas';
import type { GraphPayload } from '../../contracts/catalog';
import { DATA_STEPS, dataStepFromPath } from '../layout/nav';

const SAMPLE_DDL = `CREATE TABLE customer (
  id TEXT PRIMARY KEY,
  status TEXT,
  region TEXT
);
CREATE TABLE "order" (
  id TEXT PRIMARY KEY,
  customer_id TEXT REFERENCES customer(id),
  ordered_at TIMESTAMP,
  status TEXT
);`;

type SourceKind = 'mongodb' | 'postgresql' | 'ddl';

export function DataWizard() {
  const { useLlm, dataOk, sourceId, setSourceId, setSourceKind, domains } = useApp();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const step = DATA_STEPS.indexOf(dataStepFromPath(pathname));
  const [kind, setKind] = useState<SourceKind>('mongodb');
  const [uri, setUri] = useState('mongodb://localhost:27017');
  const [database, setDatabase] = useState('mydb');
  const [ddl, setDdl] = useState(SAMPLE_DDL);
  const [ddlName, setDdlName] = useState('uploaded-schema');
  const [schemaOnly, setSchemaOnly] = useState(false);
  const [collections, setCollections] = useState<{ name: string; entity?: string; count?: number; infrastructure?: boolean }[]>([]);
  const [mapped, setMapped] = useState<{ entity: string; collection?: string; prefLabel?: string; catalogDomain?: string; joins?: { field: string; targetEntity: string }[] }[]>([]);
  const [unmapped, setUnmapped] = useState<{ entity: string; reason?: string }[]>([]);
  const [coverage, setCoverage] = useState<number | null>(null);
  const [preferDomain, setPreferDomain] = useState('');
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState<QueryResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [preview, setPreview] = useState<{ collection: string; documents: unknown[] } | null>(null);
  const [joinGraph, setJoinGraph] = useState<GraphPayload | null>(null);

  if (dataOk === false) {
    return (
      <div className="page">
        <EmptyState title="Data agent is offline" body="Start the catalog agents gateway, then reload this page." />
      </div>
    );
  }

  async function connect(sample = false) {
    setBusy(true);
    setError('');
    try {
      const res = sample
        ? await dataApi.connect({ kind: 'memory', uri: 'memory://sample', database: 'sample', sourceId: 'sample' })
        : kind === 'ddl'
          ? await dataApi.connect({ kind: 'ddl', ddl, sourceId: ddlName || 'uploaded-schema' })
          : await dataApi.connect({ kind, uri, database, sourceId: database || undefined });
      if (!res.ok) {
        setError(res.error || 'Could not connect.');
        return;
      }
      setSourceId(res.sourceId);
      setSourceKind(sample ? 'memory' : kind === 'ddl' ? 'ddl' : kind);
      setSchemaOnly(Boolean(res.schemaOnly));
      navigate('/sources/understand');
      const schema = await dataApi.introspect(res.sourceId);
      setCollections((schema.collections || []).filter((c) => !c.infrastructure));
    } catch {
      setError('Could not connect. Check the database, paste DDL, or use sample data.');
    } finally {
      setBusy(false);
    }
  }

  async function mapNow() {
    setBusy(true);
    setError('');
    try {
      await dataApi.generateOntology(sourceId);
      await dataApi.validateOntology(sourceId);
      const mappedRes = await dataApi.map(sourceId, preferDomain);
      setMapped(mappedRes.mapped || []);
      setUnmapped(mappedRes.unmapped || []);
      const cov = await dataApi.coverage(sourceId);
      setCoverage(cov.coveragePct);
      const nodes = [
        ...(mappedRes.mapped || []).map((m) => ({
          iri: m.catalogIri || m.entity,
          prefLabel: m.prefLabel || m.entity,
          domainId: m.catalogDomain,
          kind: 'class',
        })),
        ...(mappedRes.unmapped || []).map((m) => ({
          iri: m.entity,
          prefLabel: m.entity,
          kind: 'unmapped',
        })),
      ];
      const edges = (mappedRes.mapped || []).flatMap(
        (m) =>
          (m.joins || []).map((j) => ({
            from: m.catalogIri || m.entity,
            to: j.targetEntity,
            rel: 'mapping',
          })),
      );
      setJoinGraph({ nodes, edges });
      navigate('/sources/map');
    } catch {
      setError('Mapping failed. Try Advanced → heal_mapping.');
    } finally {
      setBusy(false);
    }
  }

  async function ask(text: string) {
    const q = text.trim();
    if (!q) return;
    setBusy(true);
    setError('');
    navigate('/sources/ask');
    try {
      const res = await dataApi.query(sourceId, q, useLlm);
      setAnswer(res);
    } catch {
      setError('The question could not be answered through the mapping.');
    } finally {
      setBusy(false);
    }
  }

  function onAsk(e: FormEvent) {
    e.preventDefault();
    void ask(query);
  }

  function setKindAndDefaults(next: SourceKind) {
    setKind(next);
    if (next === 'mongodb') {
      setUri('mongodb://localhost:27017');
      setDatabase('mydb');
    }
    if (next === 'postgresql') {
      setUri('postgresql://user:pass@localhost:5432/mydb');
      setDatabase('mydb');
    }
  }

  return (
    <div className="page">
      {error && <p className="error">{error}</p>}
      {step > 0 && !sourceId ? (
        <EmptyState
          title="Connect a source first"
          body="Open Data sources in the left navigation, then attach MongoDB, PostgreSQL, DDL, or sample data."
        />
      ) : null}

      {step === 0 && (
        <Card>
          <h3>Where is the data?</h3>
          <p className="muted">Connect MongoDB or PostgreSQL, or upload CREATE TABLE statements. Sample data works without a database.</p>
          <div className="chip-row" style={{ marginBottom: 16 }}>
            <button className={`chip${kind === 'mongodb' ? ' active' : ''}`} type="button" onClick={() => setKindAndDefaults('mongodb')}>
              MongoDB
            </button>
            <button className={`chip${kind === 'postgresql' ? ' active' : ''}`} type="button" onClick={() => setKindAndDefaults('postgresql')}>
              PostgreSQL
            </button>
            <button className={`chip${kind === 'ddl' ? ' active' : ''}`} type="button" onClick={() => setKind('ddl')}>
              DDL
            </button>
          </div>
          {kind !== 'ddl' ? (
            <>
              <div className="form-group">
                <label>Connection</label>
                <input value={uri} onChange={(e) => setUri(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Database</label>
                <input value={database} onChange={(e) => setDatabase(e.target.value)} />
              </div>
            </>
          ) : (
            <>
              <div className="form-group">
                <label>Source name</label>
                <input value={ddlName} onChange={(e) => setDdlName(e.target.value)} />
              </div>
              <div className="form-group">
                <label>CREATE TABLE</label>
                <textarea value={ddl} onChange={(e) => setDdl(e.target.value)} rows={10} />
              </div>
            </>
          )}
          <div style={{ display: 'flex', gap: 8 }}>
            <Button variant="primary" disabled={busy} onClick={() => void connect(false)}>
              {busy ? <Loader2 className="spin" size={16} /> : null} Connect
            </Button>
            <Button onClick={() => void connect(true)}>Use sample data</Button>
          </div>
        </Card>
      )}

      {step === 1 && sourceId && (
        <Card>
          <h3>Here is what we found</h3>
          <p className="muted">Business collections only. Infrastructure tables are hidden.</p>
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Rows</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {collections.map((c) => (
                <tr key={c.name}>
                  <td>{c.entity || c.name}</td>
                  <td>{c.count ?? '—'}</td>
                  <td>
                    {!schemaOnly && (
                      <Button
                        onClick={() =>
                          void dataApi.sample(sourceId, c.name).then((s) =>
                            setPreview({ collection: c.name, documents: s.documents || [] }),
                          )
                        }
                      >
                        Preview rows
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {preview && (
            <details open>
              <summary className="muted">Preview: {preview.collection}</summary>
              <pre className="pre">{JSON.stringify(preview.documents, null, 2)}</pre>
            </details>
          )}
          <div className="form-group" style={{ marginTop: 16 }}>
            <label>Prefer catalog domain (optional)</label>
            <select value={preferDomain} onChange={(e) => setPreferDomain(e.target.value)}>
              <option value="">Graph-first (no preference)</option>
              {domains.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name || d.id}
                </option>
              ))}
            </select>
          </div>
          <Button variant="primary" disabled={busy} onClick={() => void mapNow()}>
            Match to catalog
          </Button>
        </Card>
      )}

      {step === 2 && sourceId && (
        <div className="workspace" style={{ minHeight: 480 }}>
          <div className="workspace-left">
            <h3>Matched to the catalog</h3>
            {coverage != null && (
              <div className="form-group">
                <label>Coverage {coverage}%</label>
                <div className="coverage">
                  <span style={{ width: `${coverage}%` }} />
                </div>
              </div>
            )}
            {mapped.map((m) => (
              <Card key={m.entity}>
                <h3>{m.prefLabel || m.entity}</h3>
                <p>{m.catalogDomain || m.collection}</p>
              </Card>
            ))}
            {unmapped.length > 0 && (
              <Button onClick={() => void dataApi.heal(sourceId).then(() => mapNow())}>Fix unmatched</Button>
            )}
            <Button variant="primary" onClick={() => navigate('/sources/ask')}>
              {schemaOnly ? 'Review mapping' : 'Ask a question'}
            </Button>
          </div>
          <div className="workspace-right">
            <GraphCanvas payload={joinGraph} />
          </div>
        </div>
      )}

      {step === 3 && sourceId && (
        <div style={{ maxWidth: 720, margin: '0 auto' }}>
          {schemaOnly ? (
            <Card>
              <h3>Schema only</h3>
              <p>This source has no rows. Mapping is available; counts need MongoDB, PostgreSQL, or sample data.</p>
            </Card>
          ) : (
            <>
              <form className="composer" onSubmit={onAsk}>
                <textarea value={query} onChange={(e) => setQuery(e.target.value)} placeholder="How many customers do I have?" rows={2} />
                <button className="send-btn" type="submit" disabled={busy}>
                  {busy ? <Loader2 className="spin" size={16} /> : <ArrowUp size={16} />}
                </button>
              </form>
              <div className="chip-row">
                {DATA_EXAMPLES.map((q) => (
                  <button key={q} className="chip" type="button" onClick={() => { setQuery(q); void ask(q); }}>
                    {q}
                  </button>
                ))}
              </div>
              {answer && (
                <Card>
                  <h3>{answer.ok === false ? 'Could not count that' : `${answer.result ?? 0}`}</h3>
                  <p>
                    {answer.ok === false
                      ? answer.error || 'That question is outside the mapped data.'
                      : `We counted ${answer.plan?.targetClass || 'records'} using only mapped fields.`}
                  </p>
                  <details>
                    <summary className="muted">How we counted</summary>
                    <pre className="pre">{JSON.stringify(answer.plan || answer, null, 2)}</pre>
                    {answer.plan?.joins?.length ? (
                      <div style={{ height: 320, marginTop: 12 }}>
                        <GraphCanvas
                          payload={(() => {
                            const nodeMap = new Map<string, { iri: string; prefLabel: string }>();
                            const target = answer.plan!.targetClass || 'Result';
                            nodeMap.set(target, { iri: target, prefLabel: target });
                            for (const j of answer.plan!.joins!) {
                              if (!nodeMap.has(j.from)) nodeMap.set(j.from, { iri: j.from, prefLabel: j.from });
                              if (!nodeMap.has(j.to)) nodeMap.set(j.to, { iri: j.to, prefLabel: j.to });
                            }
                            return {
                              nodes: [...nodeMap.values()],
                              edges: answer.plan!.joins!.map((j) => ({ from: j.from, to: j.to, rel: 'mapping' })),
                            };
                          })()}
                        />
                      </div>
                    ) : null}
                  </details>
                </Card>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
