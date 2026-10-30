import {
  Background,
  BaseEdge,
  ConnectionMode,
  ControlButton,
  Controls,
  EdgeLabelRenderer,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  ReactFlowProvider,
  applyNodeChanges,
  useReactFlow,
  type Edge,
  type EdgeProps,
  type Node,
  type NodeChange,
  type NodeProps,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Activity, CornerLeftUp } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import type { CatalogMatch, GraphPayload } from '../../contracts/catalog';

const REL_LABEL: Record<string, string> = {
  subClassOf: 'rdfs:subClassOf',
  equivalentClass: 'owl:equivalentClass',
  mapping: 'mapped to',
  alignment: 'aligned with',
};

const STRUCTURAL = new Set(['subClassOf', 'equivalentClass', 'alignment']);

const NODE_W = 176;
const NODE_H = 58;
const LEVEL_GAP_Y = 170;
const SIBLING_GAP_X = 260;
const MAX_COLS_PER_ROW = 5;
const SAME_ROW_DY = NODE_H * 0.6;

type ConceptData = {
  label: string;
  sub?: string;
  muted?: boolean;
  pulse?: boolean;
  selected?: boolean;
  table?: boolean;
};
type EdgeData = {
  rel: string;
  hot?: boolean;
  labelOffset?: number;
  labelTitle?: string;
  /** When false, draw the path but hide the floating label (dense-graph declutter). */
  showLabel?: boolean;
  dimmed?: boolean;
  /** -1..1 lateral fan so parallel edges arc apart instead of stacking. */
  fan?: number;
  curvature?: number;
};

function isHotPathRel(rel: string): boolean {
  return rel === 'mapping' || !STRUCTURAL.has(rel);
}

function isTableKind(kind?: string): boolean {
  return kind === 'unknown' || kind === 'unmapped';
}

function nodeSubLabel(n: CatalogMatch): string {
  if (n.kind === 'unknown') return 'source table';
  if (n.kind === 'unmapped') return 'unmapped';
  return n.domainId || n.kind || '';
}

function ConceptNode({ data }: NodeProps<Node<ConceptData>>) {
  const classes = [
    'xy-node',
    data.muted ? 'muted' : '',
    data.pulse ? 'agent-pulse' : '',
    data.selected ? 'selected' : '',
    data.table ? 'table' : '',
  ]
    .filter(Boolean)
    .join(' ');
  return (
    <div className={classes} title={data.label}>
      <Handle type="source" position={Position.Top} id="top" />
      <Handle type="source" position={Position.Right} id="right" />
      <Handle type="source" position={Position.Bottom} id="bottom" />
      <Handle type="source" position={Position.Left} id="left" />
      <strong className="xy-node-label">{data.label}</strong>
      {data.sub ? <div className="sub">{data.sub}</div> : null}
    </div>
  );
}

const NODE_TYPES = { concept: ConceptNode };

function controlPoint(
  x: number,
  y: number,
  position: Position,
  distance: number,
): { x: number; y: number } {
  switch (position) {
    case Position.Left:
      return { x: x - distance, y };
    case Position.Right:
      return { x: x + distance, y };
    case Position.Top:
      return { x, y: y - distance };
    default:
      return { x, y: y + distance };
  }
}

/** Cubic bezier with lateral fan so sibling edges arc apart instead of stacking. */
function getFlexiblePath({
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition = Position.Bottom,
  targetPosition = Position.Top,
  curvature = 0.35,
  fan = 0,
}: {
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  sourcePosition?: Position;
  targetPosition?: Position;
  curvature?: number;
  fan?: number;
}): [string, number, number] {
  const dx = targetX - sourceX;
  const dy = targetY - sourceY;
  const dist = Math.hypot(dx, dy) || 1;
  const curvatureDist = Math.max(40, dist * curvature);
  const c1 = controlPoint(sourceX, sourceY, sourcePosition, curvatureDist);
  const c2 = controlPoint(targetX, targetY, targetPosition, curvatureDist);

  // Perpendicular unit vector — push control points sideways by fan amount.
  const nx = -dy / dist;
  const ny = dx / dist;
  const fanPx = fan * Math.min(90, dist * 0.28);
  c1.x += nx * fanPx;
  c1.y += ny * fanPx;
  c2.x += nx * fanPx;
  c2.y += ny * fanPx;

  // Slight mid-arc lift so long horizontals don't cut through node rows.
  const midLift = Math.abs(dx) > Math.abs(dy) ? Math.min(48, dist * 0.12) * (fan === 0 ? 0.35 : Math.sign(fan) || 1) : 0;
  c1.y -= midLift;
  c2.y -= midLift;

  const path = `M ${sourceX},${sourceY} C ${c1.x},${c1.y} ${c2.x},${c2.y} ${targetX},${targetY}`;
  const labelX = 0.125 * sourceX + 0.375 * c1.x + 0.375 * c2.x + 0.125 * targetX;
  const labelY = 0.125 * sourceY + 0.375 * c1.y + 0.375 * c2.y + 0.125 * targetY;
  return [path, labelX, labelY];
}

function LabeledFlexibleEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  label,
  style,
  data,
  markerEnd,
}: EdgeProps<Edge<EdgeData>>) {
  const hot = Boolean(data?.hot);
  const showLabel = data?.showLabel !== false;
  const dimmed = Boolean(data?.dimmed);
  const offset = data?.labelOffset ?? 0;
  const [edgePath, labelX, labelY] = getFlexiblePath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    curvature: data?.curvature ?? 0.35,
    fan: data?.fan ?? 0,
  });
  const title = data?.labelTitle || (typeof label === 'string' ? label : undefined);
  const pathStyle = dimmed
    ? { ...style, strokeOpacity: 0.2, strokeWidth: 1 }
    : style;
  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={pathStyle}
        markerEnd={markerEnd}
        className={hot && !dimmed ? 'agent-path-edge' : undefined}
      />
      {label && showLabel && (
        <EdgeLabelRenderer>
          <div
            className="edge-label-floating"
            title={title}
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY + offset}px)`,
              pointerEvents: 'auto',
            }}
          >
            {label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}

const EDGE_TYPES = { labeled: LabeledFlexibleEdge };

function pickHandles(source: { x: number; y: number }, target: { x: number; y: number }) {
  const dx = target.x + NODE_W / 2 - (source.x + NODE_W / 2);
  const dy = target.y + NODE_H / 2 - (source.y + NODE_H / 2);
  // Prefer top/bottom when nodes are on different visual rows so edges do not
  // cut horizontally through sibling cards in the same row.
  if (Math.abs(dy) > SAME_ROW_DY) {
    return dy >= 0
      ? { sourceHandle: 'bottom', targetHandle: 'top' }
      : { sourceHandle: 'top', targetHandle: 'bottom' };
  }
  return dx >= 0
    ? { sourceHandle: 'right', targetHandle: 'left' }
    : { sourceHandle: 'left', targetHandle: 'right' };
}

function attachHandles(nodes: Node<ConceptData>[], edges: Edge[]): Edge[] {
  const pos = new Map(nodes.map((n) => [n.id, n.position]));
  return edges.map((edge) => {
    const from = pos.get(edge.source);
    const to = pos.get(edge.target);
    if (!from || !to) return edge;
    return { ...edge, ...pickHandles(from, to) };
  });
}

function buildAdjacency(rawEdges: { from: string; to: string; rel: string }[]) {
  const out = new Map<string, string[]>();
  const inn = new Map<string, string[]>();
  for (const e of rawEdges) {
    const kids = out.get(e.from) || [];
    kids.push(e.to);
    out.set(e.from, kids);
    const parents = inn.get(e.to) || [];
    parents.push(e.from);
    inn.set(e.to, parents);
  }
  return { out, inn };
}

function bfsLevels(
  startIds: string[],
  neighbors: Map<string, string[]>,
  visited: Set<string>,
): string[][] {
  const levels: string[][] = [];
  let frontier = startIds.filter((id) => !visited.has(id));
  while (frontier.length > 0) {
    levels.push(frontier);
    frontier.forEach((id) => visited.add(id));
    const next: string[] = [];
    for (const id of frontier) {
      for (const n of neighbors.get(id) || []) {
        if (!visited.has(n)) next.push(n);
      }
    }
    frontier = [...new Set(next)];
  }
  return levels;
}

function barycenterOrder(
  row: string[],
  previous: string[],
  links: Map<string, string[]>,
  reverseLinks: Map<string, string[]>,
): string[] {
  if (previous.length === 0) return row;
  const prevIndex = new Map(previous.map((id, i) => [id, i]));
  const scored = row.map((id, fallback) => {
    const related = [...(links.get(id) || []), ...(reverseLinks.get(id) || [])];
    const hits = related.map((r) => prevIndex.get(r)).filter((v): v is number => v != null);
    const score = hits.length ? hits.reduce((a, b) => a + b, 0) / hits.length : fallback;
    return { id, score, fallback };
  });
  scored.sort((a, b) => a.score - b.score || a.fallback - b.fallback);
  return scored.map((s) => s.id);
}

function placeWrappedRows(
  levels: string[][],
  posMap: Map<string, { x: number; y: number }>,
  startY: number,
): number {
  let yCursor = startY;
  for (const level of levels) {
    const chunks: string[][] = [];
    for (let i = 0; i < level.length; i += MAX_COLS_PER_ROW) {
      chunks.push(level.slice(i, i + MAX_COLS_PER_ROW));
    }
    for (const chunk of chunks) {
      const totalWidth = chunk.length * NODE_W + Math.max(0, chunk.length - 1) * (SIBLING_GAP_X - NODE_W);
      const startX = -totalWidth / 2;
      for (let i = 0; i < chunk.length; i++) {
        posMap.set(chunk[i], {
          x: startX + i * SIBLING_GAP_X,
          y: yCursor,
        });
      }
      yCursor += NODE_H + LEVEL_GAP_Y;
    }
  }
  return yCursor;
}

function relDisplay(rel: string): string {
  return REL_LABEL[rel] || rel;
}

function applyEdgeVisibility(
  edges: Edge<EdgeData>[],
  labelIri?: string,
): Edge<EdgeData>[] {
  // Dense CRM expansions have dozens of crossing edges. Only label edges that
  // touch the focused / hovered class; dim the rest so class names stay readable.
  const dense = edges.length > 12;
  if (!dense && !labelIri) {
    return edges.map((e) => ({
      ...e,
      data: { ...e.data, rel: e.data?.rel || '', showLabel: true, dimmed: false },
    }));
  }
  return edges.map((e) => {
    const incident = Boolean(labelIri && (e.source === labelIri || e.target === labelIri));
    const showLabel = labelIri ? incident : !dense;
    return {
      ...e,
      data: {
        ...e.data,
        rel: e.data?.rel || '',
        showLabel,
        dimmed: Boolean(labelIri) && !incident,
      },
    };
  });
}

function bundleEdges(
  rawEdges: { from: string; to: string; rel: string }[],
  agentPaths: boolean,
  labelIri?: string,
): Edge<EdgeData>[] {
  const groups = new Map<string, { from: string; to: string; rels: string[] }>();
  for (const e of rawEdges) {
    const key = `${e.from}\0${e.to}`;
    const g = groups.get(key);
    if (g) {
      if (!g.rels.includes(e.rel)) g.rels.push(e.rel);
    } else {
      groups.set(key, { from: e.from, to: e.to, rels: [e.rel] });
    }
  }

  // Fan edges that share an endpoint so curves arc apart instead of stacking.
  const fromGroups = new Map<string, { from: string; to: string; rels: string[] }[]>();
  const toGroups = new Map<string, { from: string; to: string; rels: string[] }[]>();
  for (const g of groups.values()) {
    const fl = fromGroups.get(g.from) || [];
    fl.push(g);
    fromGroups.set(g.from, fl);
    const tl = toGroups.get(g.to) || [];
    tl.push(g);
    toGroups.set(g.to, tl);
  }
  // Stable left-to-right fan order by target/source id.
  for (const list of fromGroups.values()) list.sort((a, b) => a.to.localeCompare(b.to));
  for (const list of toGroups.values()) list.sort((a, b) => a.from.localeCompare(b.from));

  const edges: Edge<EdgeData>[] = [];
  let i = 0;
  for (const g of groups.values()) {
    const hot = agentPaths && g.rels.some(isHotPathRel);
    const labels = g.rels.map(relDisplay);
    const primary = labels[0];
    const label =
      labels.length === 1 ? primary : `${primary} (+${labels.length - 1})`;
    const title = labels.join(' · ');

    const fromList = fromGroups.get(g.from) || [g];
    const toList = toGroups.get(g.to) || [g];
    const fromIdx = fromList.indexOf(g);
    const toIdx = toList.indexOf(g);
    const busy = Math.max(fromList.length, toList.length);
    const fromFan = fromList.length > 1 ? (fromIdx - (fromList.length - 1) / 2) / Math.max(1, (fromList.length - 1) / 2) : 0;
    const toFan = toList.length > 1 ? (toIdx - (toList.length - 1) / 2) / Math.max(1, (toList.length - 1) / 2) : 0;
    const fan = Math.max(-1, Math.min(1, fromFan * 0.7 + toFan * 0.3));
    const curvature = 0.28 + Math.min(0.22, busy * 0.03);
    const labelOffset = busy > 1 ? ((fromIdx + toIdx) / 2 - (busy - 1) / 2) * 14 : 0;

    edges.push({
      id: `${g.from}-${g.to}-${g.rels.join('_')}-${i}`,
      source: g.from,
      target: g.to,
      label,
      type: 'labeled',
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 14,
        height: 14,
        color: hot ? 'var(--cta-orange)' : 'var(--primary)',
      },
      style: hot
        ? { stroke: 'var(--cta-orange)', strokeWidth: 2, strokeDasharray: '6 4' }
        : { stroke: 'var(--primary)', strokeWidth: 1.6 },
      data: { rel: g.rels[0], hot, labelOffset, labelTitle: title, fan, curvature },
    });
    i += 1;
  }
  return applyEdgeVisibility(edges, labelIri);
}

function layout(
  payload: GraphPayload,
  agentPaths: boolean,
  focusIri?: string,
): { nodes: Node<ConceptData>[]; edges: Edge[]; hotEdgeCount: number; hotNodeCount: number } {
  const raw = payload.nodes || [];
  const rawEdges = payload.edges || [];

  if (raw.length === 0) return { nodes: [], edges: [], hotEdgeCount: 0, hotNodeCount: 0 };

  const { out, inn } = buildAdjacency(rawEdges);
  const iriSet = new Set(raw.map((n) => n.iri));
  const focus = focusIri && iriSet.has(focusIri) ? focusIri : undefined;

  const visited = new Set<string>();
  let upstream: string[][] = [];
  let center: string[] = [];
  let downstream: string[][] = [];

  if (focus) {
    center = [focus];
    visited.add(focus);

    // Walk parents from focus; reverse so farthest ancestors sit at the top
    // and immediate parents sit just above the focal class.
    const upSeed = [...new Set((inn.get(focus) || []).filter((id) => iriSet.has(id)))];
    const upLevels = bfsLevels(upSeed, inn, visited);
    upstream = [...upLevels].reverse();

    // Walk children / outgoing neighbors below the focal class.
    const downSeed = [...new Set((out.get(focus) || []).filter((id) => iriSet.has(id) && !visited.has(id)))];
    const downLevels = bfsLevels(downSeed, out, visited);
    downstream = downLevels;

    // Bridge remaining nodes connected via undirected adjacency, then orphans.
    const undirected = new Map<string, string[]>();
    for (const e of rawEdges) {
      if (!iriSet.has(e.from) || !iriSet.has(e.to)) continue;
      const a = undirected.get(e.from) || [];
      a.push(e.to);
      undirected.set(e.from, a);
      const b = undirected.get(e.to) || [];
      b.push(e.from);
      undirected.set(e.to, b);
    }
    const bridgeSeed: string[] = [];
    for (const id of visited) {
      for (const n of undirected.get(id) || []) {
        if (!visited.has(n)) bridgeSeed.push(n);
      }
    }
    if (bridgeSeed.length) {
      downstream = [...downstream, ...bfsLevels([...new Set(bridgeSeed)], undirected, visited)];
    }
    const orphan = raw.filter((n) => !visited.has(n.iri)).map((n) => n.iri);
    if (orphan.length) downstream = [...downstream, orphan];
  } else {
    const parentSet = new Set<string>();
    for (const e of rawEdges) parentSet.add(e.to);
    const roots = raw.filter((n) => !parentSet.has(n.iri));
    if (roots.length === 0 && raw.length > 0) roots.push(raw[0]);
    const levels = bfsLevels(
      roots.map((r) => r.iri),
      out,
      visited,
    );
    const unvisited = raw.filter((n) => !visited.has(n.iri)).map((n) => n.iri);
    if (unvisited.length > 0) levels.push(...bfsLevels(unvisited, out, visited));
    center = levels[0] || [];
    downstream = levels.slice(1);
  }

  // Barycenter ordering within each tier to reduce crossings.
  const orderedUpstream: string[][] = [];
  let prev = center;
  for (let i = upstream.length - 1; i >= 0; i--) {
    const ordered = barycenterOrder(upstream[i], prev, inn, out);
    orderedUpstream[i] = ordered;
    prev = ordered;
  }
  const orderedDownstream: string[][] = [];
  prev = center;
  for (let i = 0; i < downstream.length; i++) {
    const ordered = barycenterOrder(downstream[i], prev, out, inn);
    orderedDownstream.push(ordered);
    prev = ordered;
  }

  const posMap = new Map<string, { x: number; y: number }>();
  let y = 0;
  y = placeWrappedRows(orderedUpstream, posMap, y);
  y = placeWrappedRows([center], posMap, y);
  placeWrappedRows(orderedDownstream, posMap, y);

  const hotIris = new Set<string>();
  let hotEdgeCount = 0;
  for (const e of rawEdges) {
    if (!isHotPathRel(e.rel)) continue;
    hotEdgeCount += 1;
    hotIris.add(e.from);
    hotIris.add(e.to);
  }

  const nodes: Node<ConceptData>[] = raw.map((n) => {
    const table = isTableKind(n.kind);
    return {
      id: n.iri,
      type: 'concept',
      position: posMap.get(n.iri) || { x: 0, y: 0 },
      data: {
        label: n.prefLabel || n.localName || n.iri.split('#').pop() || n.iri,
        sub: nodeSubLabel(n),
        muted: n.kind === 'unmapped',
        pulse: agentPaths && hotIris.has(n.iri),
        selected: Boolean(focus && n.iri === focus),
        table,
      },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
    };
  });

  const edges = attachHandles(nodes, bundleEdges(rawEdges, agentPaths, focus));

  return {
    nodes,
    edges,
    hotEdgeCount,
    hotNodeCount: hotIris.size,
  };
}

function FitViewOnChange({ layoutKey }: { layoutKey: string }) {
  const { fitView } = useReactFlow();
  useEffect(() => {
    const id = requestAnimationFrame(() => {
      void fitView({ padding: 0.18, maxZoom: 1.1, duration: 200 });
    });
    return () => cancelAnimationFrame(id);
  }, [layoutKey, fitView]);
  return null;
}

export function GraphCanvas({
  payload,
  onSelect,
  onGoUp,
  canGoUp,
  upLabel,
  agentPaths = false,
  onAgentPathsChange,
  showMetricsChip = false,
  focusIri,
}: {
  payload: GraphPayload | null;
  onSelect?: (node: CatalogMatch) => void;
  onGoUp?: () => void;
  canGoUp?: boolean;
  upLabel?: string;
  agentPaths?: boolean;
  onAgentPathsChange?: (on: boolean) => void;
  /** Compact path counts when inspector is closed (two-pane). */
  showMetricsChip?: boolean;
  /** IRI of the inspected / expanded class — centered in the layout. */
  focusIri?: string;
}) {
  const byIri = useMemo(() => new Map((payload?.nodes || []).map((n) => [n.iri, n])), [payload]);
  const [nodes, setNodes] = useState<Node<ConceptData>[]>([]);
  const [edges, setEdges] = useState<Edge<EdgeData>[]>([]);
  const [metrics, setMetrics] = useState({ hotEdgeCount: 0, hotNodeCount: 0 });
  const [hoverIri, setHoverIri] = useState<string | undefined>();
  const labelIri = hoverIri || focusIri;
  const layoutKey = useMemo(() => {
    const iris = (payload?.nodes || []).map((n) => n.iri).join('|');
    const edgeKey = (payload?.edges || []).map((e) => `${e.from}>${e.to}:${e.rel}`).join('|');
    return `${focusIri || ''}:${agentPaths ? 1 : 0}:${iris}:${edgeKey}`;
  }, [payload, focusIri, agentPaths]);

  useEffect(() => {
    const next = payload
      ? layout(payload, agentPaths, focusIri)
      : { nodes: [], edges: [], hotEdgeCount: 0, hotNodeCount: 0 };
    setNodes(next.nodes);
    setEdges(applyEdgeVisibility(next.edges as Edge<EdgeData>[], hoverIri || focusIri));
    setMetrics({ hotEdgeCount: next.hotEdgeCount, hotNodeCount: next.hotNodeCount });
    // Hover is applied in a separate effect so layout does not thrash on mouse move.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [payload, agentPaths, focusIri]);

  useEffect(() => {
    setEdges((current) => applyEdgeVisibility(current, labelIri));
  }, [labelIri]);

  const onNodesChange = useCallback((changes: NodeChange<Node<ConceptData>>[]) => {
    setNodes((current) => {
      const next = applyNodeChanges(changes, current);
      setEdges((currentEdges) => attachHandles(next, currentEdges) as Edge<EdgeData>[]);
      return next;
    });
  }, []);

  if (!payload?.nodes?.length) {
    return <p className="muted">Search the catalog, then expand a term’s neighbourhood.</p>;
  }

  return (
    <div className="graph-canvas">
      <div className="graph-toolbar">
        {onGoUp && canGoUp ? (
          <button type="button" className="graph-up" onClick={onGoUp} title="Up to previous class">
            <CornerLeftUp size={14} />
            {upLabel ? `Up to ${upLabel}` : 'Up'}
          </button>
        ) : (
          <span />
        )}
        <div className="graph-toolbar-right">
          {showMetricsChip && agentPaths ? (
            <span className="chip agent-metrics-chip" title="Graph-derived path counts">
              {metrics.hotEdgeCount} paths · {metrics.hotNodeCount} classes
            </span>
          ) : null}
          {onAgentPathsChange ? (
            <button
              type="button"
              className={`chip agent-paths-toggle${agentPaths ? ' active' : ''}`}
              onClick={() => onAgentPathsChange(!agentPaths)}
              title="Highlight object-property and mapping edges"
            >
              <Activity size={12} />
              Agent paths
            </button>
          ) : null}
        </div>
      </div>
      <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={NODE_TYPES}
          edgeTypes={EDGE_TYPES}
          onNodesChange={onNodesChange}
          connectionMode={ConnectionMode.Loose}
          fitView
          fitViewOptions={{ padding: 0.18, maxZoom: 1.1 }}
          nodesConnectable={false}
          onNodeMouseEnter={(_, node) => setHoverIri(node.id)}
          onNodeMouseLeave={() => setHoverIri(undefined)}
          onNodeClick={(_, node) => {
            const match = byIri.get(node.id);
            if (match && onSelect) onSelect(match);
          }}
          proOptions={{ hideAttribution: true }}
          defaultEdgeOptions={{ type: 'labeled' }}
        >
          <FitViewOnChange layoutKey={layoutKey} />
          <Background color="var(--border-color)" gap={18} />
          <MiniMap pannable zoomable />
          <Controls>
            {onGoUp ? (
              <ControlButton onClick={onGoUp} disabled={!canGoUp} title="Up to previous class" aria-label="Up to previous class">
                <CornerLeftUp size={14} />
              </ControlButton>
            ) : null}
          </Controls>
        </ReactFlow>
      </ReactFlowProvider>
    </div>
  );
}
