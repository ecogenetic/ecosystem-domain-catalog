import {
  AlertTriangle,
  Check,
  CheckCircle2,
  Copy,
  Info,
  Loader2,
  Pencil,
  ShieldCheck,
  Sparkles,
  X,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';
import { Button } from '../common/Button';
import { TurtleView } from '../common/TurtleView';

export type ValidationIssue = {
  ruleId?: string;
  aspect?: string;
  severity?: string;
  subject?: string;
  message?: string;
  hint?: string;
};

export type ValidationRecommendation = {
  id: string;
  ruleId?: string;
  category?: string;
  severity?: string;
  subject?: string;
  title?: string;
  rationale?: string;
  actionType?: string;
  suggestedTtl?: string;
  autoApplicable?: boolean;
};

export type ValidationReportPayload = {
  ok?: boolean;
  validationSource?: string;
  validationServer?: string;
  remoteError?: string;
  serviceVersion?: string;
  detectedFeatures?: { ruleId?: string; detail?: string }[];
  validationSummary?: {
    tripleCount?: number;
    classCount?: number;
    objectPropertyCount?: number;
    datatypePropertyCount?: number;
    shaclNodeShapeCount?: number;
    bfoRoleCount?: number;
    conforms?: boolean;
    rdfVersion?: string;
    errors?: number;
    warnings?: number;
  };
  summary?: {
    errors?: number;
    warnings?: number;
    suggestions?: number;
    info?: number;
    issueCount?: number;
    recommendationCount?: number;
    passed?: boolean;
  };
  issues?: ValidationIssue[];
  recommendations?: ValidationRecommendation[];
};

type TabId = 'overview' | 'issues' | 'recommendations' | 'source';

const ASPECT_LABELS: Record<string, { title: string; subtitle: string }> = {
  syntax: {
    title: 'Syntax (RDF 1.2 / TTL / OWL)',
    subtitle: 'Prefixes, statement termination, XML/Turtle structure, RDF 1.2 features',
  },
  owl_skos: {
    title: 'OWL 2 & SKOS Vocabulary',
    subtitle: 'Ontology header, owl:Class, domain/range, skos:prefLabel & skos:definition',
  },
  shacl: {
    title: 'SHACL Completeness',
    subtitle: 'sh:NodeShape, sh:targetClass, sh:path, sh:minCount, sh:in, sh:or',
  },
  role_policy: {
    title: 'Roles & BFO Policy',
    subtitle: 'bfo:0000023 role hierarchy, Bearer & Permissions annotations',
  },
};

function severityTone(sev?: string): 'error' | 'warn' | 'info' | 'ok' {
  if (sev === 'error') return 'error';
  if (sev === 'warning') return 'warn';
  if (sev === 'suggestion') return 'info';
  return 'ok';
}

export function OntologyValidationModal({
  open,
  onClose,
  ontologyName,
  turtle,
  report,
  busy,
  selectedRecIds,
  onToggleRec,
  onSelectAllRecs,
  onRevalidate,
  onApplyRecommendations,
  lastApplyFeedback,
}: {
  open: boolean;
  onClose: () => void;
  ontologyName: string;
  turtle: string;
  report: ValidationReportPayload | null;
  busy: boolean;
  selectedRecIds: string[];
  onToggleRec: (id: string) => void;
  onSelectAllRecs: (ids: string[]) => void;
  onRevalidate: () => void;
  onApplyRecommendations: (recs: ValidationRecommendation[], customTtl?: string) => void;
  lastApplyFeedback?: string;
}) {
  const [tab, setTab] = useState<TabId>('overview');
  const [sevFilter, setSevFilter] = useState<string>('all');
  const [aspectFilter, setAspectFilter] = useState<string>('all');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [editingRecId, setEditingRecId] = useState<string | null>(null);
  const [editedTtlByRecId, setEditedTtlByRecId] = useState<Record<string, string>>({});
  const [customTtlDraft, setCustomTtlDraft] = useState('');
  const [showCustomTtl, setShowCustomTtl] = useState(false);

  const issues = report?.issues || [];
  const recs = report?.recommendations || [];
  const vs = report?.validationSummary || {};
  const errors = report?.summary?.errors ?? vs.errors ?? 0;
  const warnings = report?.summary?.warnings ?? vs.warnings ?? 0;
  const suggestions =
    report?.summary?.suggestions ??
    issues.filter((i) => i.severity === 'suggestion').length;
  const passed = report?.summary?.passed ?? errors === 0;

  useEffect(() => {
    setEditingRecId(null);
    setEditedTtlByRecId({});
  }, [report]);

  function effectiveTtl(rec: ValidationRecommendation): string {
    return editedTtlByRecId[rec.id] !== undefined
      ? editedTtlByRecId[rec.id]
      : rec.suggestedTtl || '';
  }

  function withEffectiveTtl(rec: ValidationRecommendation): ValidationRecommendation {
    return { ...rec, suggestedTtl: effectiveTtl(rec) };
  }

  const filteredIssues = useMemo(
    () =>
      issues.filter((i) => {
        if (sevFilter !== 'all' && i.severity !== sevFilter) return false;
        if (aspectFilter !== 'all' && (i.aspect || 'syntax') !== aspectFilter) return false;
        return true;
      }),
    [issues, sevFilter, aspectFilter],
  );

  const filteredRecs = useMemo(
    () =>
      recs.filter((r) => {
        if (sevFilter !== 'all' && r.severity !== sevFilter) return false;
        if (aspectFilter !== 'all' && (r.category || '') !== aspectFilter) return false;
        return true;
      }),
    [recs, sevFilter, aspectFilter],
  );

  if (!open) return null;

  const applicableRecs = recs.filter((r) => effectiveTtl(r).trim().length > 0);
  const applicableIds = applicableRecs.map((r) => r.id);
  const selectedRecObjects = recs
    .filter((r) => selectedRecIds.includes(r.id) && effectiveTtl(r).trim().length > 0)
    .map(withEffectiveTtl);

  async function copySnippet(rec: ValidationRecommendation) {
    const text = effectiveTtl(rec);
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(rec.id);
      setTimeout(() => setCopiedId(null), 1500);
    } catch {
      /* ignore */
    }
  }

  function applyOne(rec: ValidationRecommendation) {
    const item = withEffectiveTtl(rec);
    if (!item.suggestedTtl?.trim()) return;
    onApplyRecommendations([item]);
  }

  function applySelected() {
    if (!selectedRecObjects.length && !customTtlDraft.trim()) return;
    onApplyRecommendations(selectedRecObjects, customTtlDraft.trim() || undefined);
    setCustomTtlDraft('');
  }

  function applyAll() {
    if (!applicableRecs.length) return;
    onApplyRecommendations(applicableRecs.map(withEffectiveTtl));
  }

  return createPortal(
    <div
      className="val-modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`${ontologyName} — Validation & Recommendations`}
    >
      <div className="val-modal" onClick={(e) => e.stopPropagation()}>
        <header className="val-modal-header">
          <ShieldCheck size={20} style={{ color: 'var(--primary)', flexShrink: 0 }} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="val-modal-title">{ontologyName} — Validation &amp; Recommendations</div>
            <div className="val-modal-sub">
              RDF 1.2 · TTL · OWL 2 · SKOS · SHACL · BFO · engine:{' '}
              <code>{report?.validationSource || 'remote'}</code>
              {report?.validationServer ? ` (${report.validationServer})` : ''}
            </div>
          </div>
          <span
            className={`val-status-pill ${
              errors > 0 ? 'tone-error' : warnings > 0 ? 'tone-warn' : 'tone-ok'
            }`}
          >
            {errors > 0 ? (
              <>
                <AlertTriangle size={13} /> Action needed ({errors} error{errors === 1 ? '' : 's'})
              </>
            ) : warnings > 0 ? (
              <>
                <AlertTriangle size={13} /> {warnings} warning{warnings === 1 ? '' : 's'}
              </>
            ) : (
              <>
                <CheckCircle2 size={13} /> Valid &amp; Conformant
              </>
            )}
          </span>
          {applicableRecs.length > 0 && (
            <Button variant="primary" onClick={applyAll} disabled={busy}>
              {busy ? <Loader2 size={14} className="spin" /> : <Sparkles size={14} />}
              Apply All ({applicableRecs.length})
            </Button>
          )}
          <Button onClick={onRevalidate} disabled={busy}>
            {busy ? <Loader2 size={14} className="spin" /> : <ShieldCheck size={14} />}
            Re-validate
          </Button>
          <button type="button" className="val-modal-close" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </header>

        {lastApplyFeedback && (
          <div className="val-apply-banner">
            <CheckCircle2 size={15} style={{ color: 'var(--success)', flexShrink: 0 }} />
            <span>{lastApplyFeedback}</span>
            <span className="grow" />
            <button type="button" className="val-link-btn" onClick={() => setTab('source')}>
              Inspect updated Turtle →
            </button>
          </div>
        )}

        <div className="val-metrics-bar">
          <Metric label="Triples" value={vs.tripleCount ?? '—'} />
          <Metric label="Classes" value={vs.classCount ?? 0} />
          <Metric label="Object Props" value={vs.objectPropertyCount ?? 0} />
          <Metric label="Datatype Props" value={vs.datatypePropertyCount ?? 0} />
          <Metric label="SHACL Shapes" value={vs.shaclNodeShapeCount ?? 0} />
          <Metric label="BFO Roles" value={vs.bfoRoleCount ?? 0} />
          <Metric label="Errors" value={errors} tone={errors > 0 ? 'error' : 'ok'} />
          <Metric label="Warnings" value={warnings} tone={warnings > 0 ? 'warn' : 'ok'} />
          <Metric label="Fixes Ready" value={applicableRecs.length} tone={applicableRecs.length > 0 ? 'info' : 'ok'} />
        </div>

        <nav className="val-tabs" aria-label="Validation views">
          <button
            type="button"
            className={`val-tab ${tab === 'overview' ? 'active' : ''}`}
            onClick={() => setTab('overview')}
          >
            Overview &amp; Aspects
          </button>
          <button
            type="button"
            className={`val-tab ${tab === 'issues' ? 'active' : ''}`}
            onClick={() => setTab('issues')}
          >
            Issues &amp; Warnings ({issues.length})
          </button>
          <button
            type="button"
            className={`val-tab ${tab === 'recommendations' ? 'active' : ''}`}
            onClick={() => setTab('recommendations')}
          >
            Recommendations ({recs.length})
          </button>
          <button
            type="button"
            className={`val-tab ${tab === 'source' ? 'active' : ''}`}
            onClick={() => setTab('source')}
          >
            Source ({turtle.split('\n').length} lines)
          </button>
        </nav>

        <div className="val-modal-body">
          {tab === 'overview' && (
            <div className="val-overview">
              <div className="val-aspect-grid">
                {Object.entries(ASPECT_LABELS).map(([aspect, meta]) => {
                  const aspectIssues = issues.filter((i) => (i.aspect || 'syntax') === aspect);
                  const aErr = aspectIssues.filter((i) => i.severity === 'error').length;
                  const aWarn = aspectIssues.filter((i) => i.severity === 'warning').length;
                  const aSug = aspectIssues.filter(
                    (i) => i.severity !== 'error' && i.severity !== 'warning',
                  ).length;
                  const tone = aErr > 0 ? 'error' : aWarn > 0 ? 'warn' : 'ok';
                  return (
                    <div
                      key={aspect}
                      className={`val-aspect-card tone-${tone}`}
                      onClick={() => {
                        setAspectFilter(aspect);
                        setTab('issues');
                      }}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          setAspectFilter(aspect);
                          setTab('issues');
                        }
                      }}
                    >
                      <div className="val-aspect-head">
                        <strong>{meta.title}</strong>
                        <span className={`val-badge tone-${tone}`}>
                          {aErr > 0 ? `${aErr} error(s)` : aWarn > 0 ? `${aWarn} warning(s)` : 'Pass'}
                        </span>
                      </div>
                      <p className="muted" style={{ margin: '4px 0 8px', fontSize: 12 }}>
                        {meta.subtitle}
                      </p>
                      <div style={{ fontSize: 12 }}>
                        {aErr} errors · {aWarn} warnings · {aSug} notes —{' '}
                        <span style={{ color: 'var(--primary)' }}>Inspect →</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="val-overview-split">
                <div className="val-overview-col">
                  <div className="val-section-head">
                    <strong>Top Findings</strong>
                    <button
                      type="button"
                      className="val-link-btn"
                      onClick={() => {
                        setAspectFilter('all');
                        setSevFilter('all');
                        setTab('issues');
                      }}
                    >
                      View all ({issues.length}) →
                    </button>
                  </div>
                  {issues.length === 0 ? (
                    <p className="muted">No issues reported — ontology passes all checks.</p>
                  ) : (
                    <ul className="val-list">
                      {issues.slice(0, 8).map((iss, idx) => (
                        <li key={`${iss.ruleId}-${idx}`} className="val-list-item">
                          <span className={`val-badge tone-${severityTone(iss.severity)}`}>
                            {iss.severity || 'info'}
                          </span>
                          <code>{iss.ruleId}</code>
                          {iss.subject ? <span className="chip">{iss.subject}</span> : null}
                          <span>{iss.message}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="val-overview-col">
                  <div className="val-section-head">
                    <strong>Actionable Recommendations ({recs.length})</strong>
                    {recs.length > 0 && (
                      <button
                        type="button"
                        className="val-link-btn"
                        onClick={() => setTab('recommendations')}
                      >
                        Review &amp; edit all →
                      </button>
                    )}
                  </div>
                  {recs.length === 0 ? (
                    <p className="muted">No recommendations needed.</p>
                  ) : (
                    <>
                      <ul className="val-list">
                        {recs.slice(0, 6).map((rec) => (
                          <li key={rec.id} className="val-list-item">
                            <span className={`val-badge tone-${severityTone(rec.severity)}`}>
                              {rec.severity}
                            </span>
                            <strong style={{ flex: 1 }}>{rec.title}</strong>
                            {effectiveTtl(rec).trim() && (
                              <Button
                                variant="primary"
                                disabled={busy}
                                onClick={() => applyOne(rec)}
                              >
                                <Check size={12} /> Apply
                              </Button>
                            )}
                          </li>
                        ))}
                      </ul>
                      {applicableRecs.length > 0 && (
                        <div style={{ marginTop: 10, display: 'flex', justifyContent: 'flex-end' }}>
                          <Button variant="primary" disabled={busy} onClick={applyAll}>
                            <Sparkles size={13} /> Apply All {applicableRecs.length} Fixes to Your Ontology
                          </Button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {tab === 'issues' && (
            <div>
              <div className="val-filter-bar">
                <select
                  value={sevFilter}
                  onChange={(e) => setSevFilter(e.target.value)}
                  aria-label="Filter by severity"
                >
                  <option value="all">All severities ({issues.length})</option>
                  <option value="error">Errors ({errors})</option>
                  <option value="warning">Warnings ({warnings})</option>
                  <option value="suggestion">Suggestions ({suggestions})</option>
                  <option value="info">Info</option>
                </select>
                <select
                  value={aspectFilter}
                  onChange={(e) => setAspectFilter(e.target.value)}
                  aria-label="Filter by aspect"
                >
                  <option value="all">All aspects</option>
                  <option value="syntax">Syntax (RDF 1.2 / TTL / OWL)</option>
                  <option value="owl_skos">OWL 2 &amp; SKOS</option>
                  <option value="shacl">SHACL Shapes</option>
                  <option value="role_policy">BFO Roles</option>
                </select>
                {(sevFilter !== 'all' || aspectFilter !== 'all') && (
                  <Button
                    onClick={() => {
                      setSevFilter('all');
                      setAspectFilter('all');
                    }}
                  >
                    Reset filters
                  </Button>
                )}
              </div>

              {filteredIssues.length === 0 ? (
                <p className="muted">No issues match the current filter.</p>
              ) : (
                <div className="val-issue-table">
                  {filteredIssues.map((iss, idx) => {
                    const matchingRec = recs.find(
                      (r) =>
                        r.ruleId === iss.ruleId &&
                        (!iss.subject || !r.subject || r.subject === iss.subject),
                    );
                    return (
                      <div key={`${iss.ruleId}-${idx}`} className="val-issue-row">
                        <div className="val-issue-meta">
                          <span className={`val-badge tone-${severityTone(iss.severity)}`}>
                            {iss.severity || 'info'}
                          </span>
                          <code>{iss.ruleId}</code>
                          <span className="chip">{iss.aspect || 'syntax'}</span>
                          {iss.subject ? <strong className="val-subject">{iss.subject}</strong> : null}
                          <span className="grow" />
                          {matchingRec && effectiveTtl(matchingRec).trim() && (
                            <Button
                              variant="primary"
                              disabled={busy}
                              onClick={() => applyOne(matchingRec)}
                            >
                              <Sparkles size={12} /> Fix this now
                            </Button>
                          )}
                        </div>
                        <div className="val-issue-msg">{iss.message}</div>
                        {iss.hint ? (
                          <div className="val-issue-hint">
                            <Info size={12} /> {iss.hint}
                          </div>
                        ) : null}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {tab === 'recommendations' && (
            <div>
              <div className="val-filter-bar">
                <select
                  value={sevFilter}
                  onChange={(e) => setSevFilter(e.target.value)}
                  aria-label="Filter recommendations by severity"
                >
                  <option value="all">All severities ({recs.length})</option>
                  <option value="error">error</option>
                  <option value="warning">warning</option>
                  <option value="suggestion">suggestion</option>
                </select>
                <Button
                  onClick={() =>
                    onSelectAllRecs(
                      selectedRecIds.length === applicableIds.length ? [] : applicableIds,
                    )
                  }
                  disabled={!applicableIds.length}
                >
                  {selectedRecIds.length === applicableIds.length ? 'Clear selection' : 'Select all'}
                </Button>
                <Button onClick={() => setShowCustomTtl((v) => !v)}>
                  <Pencil size={12} /> {showCustomTtl ? 'Hide custom TTL' : 'Add custom TTL'}
                </Button>
                <span className="grow" />
                <Button
                  variant="primary"
                  disabled={busy || (!selectedRecObjects.length && !customTtlDraft.trim())}
                  onClick={applySelected}
                >
                  {busy ? <Loader2 size={14} className="spin" /> : <Sparkles size={14} />}
                  Apply Selected ({selectedRecObjects.length}) to Your Ontology
                </Button>
              </div>

              {showCustomTtl && (
                <div className="val-rec-card" style={{ marginBottom: 12 }}>
                  <strong>Custom Turtle patch to append</strong>
                  <textarea
                    value={customTtlDraft}
                    onChange={(e) => setCustomTtlDraft(e.target.value)}
                    rows={4}
                    placeholder=":MyClass skos:prefLabel &quot;My Class&quot; ; skos:definition &quot;Definition...&quot; ."
                    style={{
                      width: '100%',
                      marginTop: 6,
                      background: 'var(--bg-primary)',
                      color: 'var(--text-primary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 6,
                      padding: 8,
                      fontFamily: 'monospace',
                      fontSize: 12,
                    }}
                  />
                </div>
              )}

              {filteredRecs.length === 0 ? (
                <p className="muted">No recommendations for this filter.</p>
              ) : (
                <div className="val-rec-list">
                  {filteredRecs.map((rec) => {
                    const checked = selectedRecIds.includes(rec.id);
                    const ttlValue = effectiveTtl(rec);
                    const isEditing = editingRecId === rec.id;
                    return (
                      <div key={rec.id} className={`val-rec-card ${checked ? 'selected' : ''}`}>
                        <div className="val-rec-head">
                          <label style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, cursor: 'pointer' }}>
                            <input
                              type="checkbox"
                              checked={checked}
                              disabled={!ttlValue.trim()}
                              onChange={() => onToggleRec(rec.id)}
                            />
                            <span className={`val-badge tone-${severityTone(rec.severity)}`}>
                              {rec.severity}
                            </span>
                            <code>{rec.ruleId}</code>
                            {rec.subject ? <span className="chip">{rec.subject}</span> : null}
                            <strong>{rec.title}</strong>
                          </label>
                          {ttlValue ? (
                            <div style={{ display: 'flex', gap: 6 }}>
                              <Button
                                onClick={() =>
                                  setEditingRecId(isEditing ? null : rec.id)
                                }
                              >
                                <Pencil size={12} /> {isEditing ? 'Done' : 'Edit TTL'}
                              </Button>
                              <Button onClick={() => void copySnippet(rec)}>
                                <Copy size={12} /> {copiedId === rec.id ? 'Copied' : 'Copy'}
                              </Button>
                              <Button
                                variant="primary"
                                disabled={busy || !ttlValue.trim()}
                                onClick={() => applyOne(rec)}
                              >
                                <Check size={12} /> Apply this fix
                              </Button>
                            </div>
                          ) : null}
                        </div>
                        {rec.rationale ? (
                          <div className="val-rec-rationale">{rec.rationale}</div>
                        ) : null}
                        {isEditing ? (
                          <textarea
                            value={ttlValue}
                            onChange={(e) =>
                              setEditedTtlByRecId((prev) => ({
                                ...prev,
                                [rec.id]: e.target.value,
                              }))
                            }
                            rows={Math.max(3, ttlValue.split('\n').length + 1)}
                            aria-label={`Edit TTL for ${rec.title}`}
                            style={{
                              width: '100%',
                              marginTop: 8,
                              background: 'var(--bg-primary)',
                              color: 'var(--text-primary)',
                              border: '1px solid var(--primary)',
                              borderRadius: 6,
                              padding: 10,
                              fontFamily: 'monospace',
                              fontSize: 12,
                            }}
                          />
                        ) : ttlValue ? (
                          <pre className="val-rec-ttl">{ttlValue}</pre>
                        ) : null}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {tab === 'source' && (
            <div style={{ maxHeight: '60vh', overflow: 'auto' }}>
              <TurtleView turtle={turtle} />
            </div>
          )}
        </div>

        <footer className="val-modal-footer">
          <span className="muted">
            {passed
              ? 'Ontology passes syntax & structural checks.'
              : `${errors} error(s) and ${warnings} warning(s) detected — apply individual fixes or selected recommendations above.`}
          </span>
          <span className="grow" />
          {selectedRecObjects.length > 0 && (
            <Button variant="primary" disabled={busy} onClick={applySelected}>
              <Sparkles size={14} /> Apply Selected ({selectedRecObjects.length}) to Your Ontology
            </Button>
          )}
          <Button onClick={onClose}>Close</Button>
        </footer>
      </div>
    </div>,
    document.body,
  );
}

function Metric({
  label,
  value,
  tone,
}: {
  label: string;
  value: string | number;
  tone?: 'ok' | 'warn' | 'error' | 'info';
}) {
  return (
    <div className={`val-metric ${tone ? `tone-${tone}` : ''}`}>
      <div className="val-metric-label">{label}</div>
      <div className="val-metric-value">{value}</div>
    </div>
  );
}
