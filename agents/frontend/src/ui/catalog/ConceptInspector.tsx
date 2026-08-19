import { catalogApi } from '../../adapters/catalogApi';
import {
  isMapped,
  ontologyKindLabel,
  type CatalogMatch,
  type GraphPayload,
  type MappingTriple,
  type ShapeConstraint,
} from '../../contracts/catalog';
import { type ReactNode, useEffect, useState } from 'react';

type Props = {
  selected: CatalogMatch;
  graph: GraphPayload | null;
  agentPaths?: boolean;
  onClose?: () => void;
  /** Extra blocks (e.g. session match UI) rendered after catalog sections. */
  footer?: ReactNode;
  /** When false, skip catalog mappings/alignments/concept fetches (session-only graphs). */
  fetchCatalog?: boolean;
};

export function ConceptInspector({
  selected,
  graph,
  agentPaths,
  onClose,
  footer,
  fetchCatalog = true,
}: Props) {
  const [mappings, setMappings] = useState<MappingTriple[]>([]);
  const [alignment, setAlignment] = useState<{ relation?: string; iri?: string; falseFriend?: boolean } | null>(null);
  const [concept, setConcept] = useState<CatalogMatch | null>(null);

  useEffect(() => {
    if (!fetchCatalog) {
      setMappings([]);
      setAlignment(null);
      setConcept(null);
      return;
    }
    let cancelled = false;
    setMappings([]);
    setAlignment(null);
    setConcept(null);
    void Promise.all([
      catalogApi.mappings(selected.iri),
      catalogApi.alignments(selected.iri),
      catalogApi.concept(selected.iri),
    ]).then(([mapRes, alignRes, conceptRes]) => {
      if (cancelled) return;
      setMappings((mapRes as { mappings?: MappingTriple[] }).mappings || []);
      const a = alignRes as { alignment?: { relation?: string; iri?: string }; falseFriend?: boolean };
      setAlignment({ ...(a.alignment || {}), falseFriend: a.falseFriend });
      if (conceptRes?.ok !== false) setConcept(conceptRes);
    }).catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [selected.iri, fetchCatalog]);

  const label = selected.prefLabel || selected.localName || selected.iri;
  const byIri = new Map((graph?.nodes || []).map((n) => [n.iri, n]));
  const relationships = (graph?.edges || [])
    .filter((e) => e.from === selected.iri || e.to === selected.iri)
    .map((e) => {
      const otherIri = e.from === selected.iri ? e.to : e.from;
      const other = byIri.get(otherIri);
      const otherLabel = other?.prefLabel || other?.localName || otherIri.split('#').pop() || otherIri;
      const verb = e.rel || 'related';
      if (e.from === selected.iri) return `${label} → ${verb} → ${otherLabel}`;
      return `${otherLabel} → ${verb} → ${label}`;
    });
  const shapes: ShapeConstraint[] = concept?.shapes || selected.shapes || [];
  const lifecycle = concept?.lifecycleStates || selected.lifecycleStates || [];

  const pathEdges = (graph?.edges || []).filter(
    (e) => e.rel === 'mapping' || !['subClassOf', 'equivalentClass', 'alignment'].includes(e.rel),
  );
  const touchIris = new Set<string>();
  for (const e of pathEdges) {
    touchIris.add(e.from);
    touchIris.add(e.to);
  }

  return (
    <aside className="graph-inspector">
      <div className="inspector-head">
        <h3>{label}</h3>
        {onClose && (
          <button type="button" className="chip" onClick={onClose}>
            Close
          </button>
        )}
      </div>
      <p className="muted">
        {ontologyKindLabel(selected.kind)}
        {selected.domainId ? ` · ontology ${selected.domainId}` : ''}
        {isMapped(concept || selected) ? ' · Mapped' : ''}
      </p>
      <p>{selected.definition || concept?.definition || 'No definition on this class.'}</p>
      {(selected.altLabels || concept?.altLabels || []).length > 0 && (
        <p className="muted">Also known as: {(selected.altLabels || concept?.altLabels || []).join(', ')}</p>
      )}

      <section className="inspector-section">
        <h4>Relationships</h4>
        {relationships.length ? (
          <ul className="rel-list">
            {relationships.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        ) : (
          <p className="muted">No graph neighbors for this class yet.</p>
        )}
      </section>

      <section className="inspector-section">
        <h4>Systems of Record</h4>
        {mappings.length ? (
          <ul className="rel-list">
            {mappings.map((m, i) => (
              <li key={`${m.source_iri}-${m.target_iri}-${i}`}>
                {(m.source_iri || '').split('#').pop()} → {m.predicate || 'mapped'} → {(m.target_iri || '').split('#').pop()}
                {m.source_path ? <span className="muted"> · {m.source_path}</span> : null}
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">No non-stub mappings on this class.</p>
        )}
        {alignment && alignment.relation && alignment.relation !== 'none' && (
          <p className="muted">
            Core alignment: {alignment.relation}
            {alignment.iri ? ` · ${alignment.iri.split('#').pop()}` : ''}
            {alignment.falseFriend ? ' · false friend' : ''}
          </p>
        )}
      </section>

      <section className="inspector-section">
        <h4>Validation rules</h4>
        {shapes.length || lifecycle.length ? (
          <ul className="rel-list">
            {shapes.map((s, i) => (
              <li key={`${s.path}-${i}`}>
                {s.path || 'property'}
                {s.minCount != null ? ` · minCount ${s.minCount}` : ''}
                {s.classLocal ? ` · class ${s.classLocal}` : ''}
                {s.in?.length ? ` · in (${s.in.join(', ')})` : ''}
              </li>
            ))}
            {!shapes.length && lifecycle.length > 0 && (
              <li>lifecycle · in ({lifecycle.join(', ')})</li>
            )}
          </ul>
        ) : (
          <p className="muted">No SHACL constraints indexed for this class.</p>
        )}
      </section>

      {agentPaths && (
        <section className="inspector-section">
          <h4>Execution metrics</h4>
          <ul className="rel-list">
            <li>Property / mapping paths: {pathEdges.length}</li>
            <li>Touched classes: {touchIris.size}</li>
            <li>Mapped classes: {(graph?.nodes || []).filter(isMapped).length}</li>
          </ul>
        </section>
      )}

      <details>
        <summary className="muted">IRI and local name</summary>
        <p className="muted">{selected.iri}</p>
        {selected.localName ? <p className="muted">{selected.localName}</p> : null}
      </details>
      {footer}
    </aside>
  );
}
