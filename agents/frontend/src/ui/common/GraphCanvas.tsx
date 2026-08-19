import {
  Background,
  BaseEdge,
  ConnectionMode,
  ControlButton,
  Controls,
  EdgeLabelRenderer,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  ReactFlowProvider,
  applyNodeChanges,
  getSmoothStepPath,
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

const NODE_W = 168;
const NODE_H = 52;
const LEVEL_GAP_Y = 140;
const SIBLING_GAP_X = 200;

type ConceptData = { label: string; sub?: string; muted?: boolean; pulse?: boolean };
type EdgeData = { rel: string; hot?: boolean };

function isHotPathRel(rel: string): boolean {
  return rel === 'mapping' || !STRUCTURAL.has(rel);
}

function ConceptNode({ data }: NodeProps<Node<ConceptData>>) {
  return (
    <div className={`xy-node${data.muted ? ' muted' : ''}${data.pulse ? ' agent-pulse' : ''}`}>
      <Handle type="source" position={Position.Top} id="top" />
      <Handle type="source" position={Position.Right} id="right" />
      <Handle type="source" position={Position.Bottom} id="bottom" />
      <Handle type="source" position={Position.Left} id="left" />
      <strong>{data.label}</strong>
      {data.sub ? <div className="sub">{data.sub}</div> : null}
    </div>
  );
}

const NODE_TYPES = { concept: ConceptNode };

function LabeledSmoothStep({
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
}: EdgeProps<Edge<EdgeData>>) {
  const hot = Boolean(data?.hot);
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
  });
  return (
    <>
      <BaseEdge id={id} path={edgePath} style={style} className={hot ? 'agent-path-edge' : undefined} />
      {label && (
        <EdgeLabelRenderer>
          <div
            className="edge-label-floating"
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
              pointerEvents: 'none',
            }}
          >
            {label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}

const EDGE_TYPES = { labeled: LabeledSmoothStep };

function pickHandles(source: { x: number; y: number }, target: { x: number; y: number }) {
  const dx = target.x + NODE_W / 2 - (source.x + NODE_W / 2);
  const dy = target.y + NODE_H / 2 - (source.y + NODE_H / 2);
  if (Math.abs(dx) >= Math.abs(dy)) {
    return dx >= 0
      ? { sourceHandle: 'right', targetHandle: 'left' }
      : { sourceHandle: 'left', targetHandle: 'right' };
  }
  return dy >= 0
    ? { sourceHandle: 'bottom', targetHandle: 'top' }
    : { sourceHandle: 'top', targetHandle: 'bottom' };
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

function layout(
  payload: GraphPayload,
  agentPaths: boolean,
): { nodes: Node<ConceptData>[]; edges: Edge[]; hotEdgeCount: number; hotNodeCount: number } {
  const raw = payload.nodes || [];
  const rawEdges = payload.edges || [];

  if (raw.length === 0) return { nodes: [], edges: [], hotEdgeCount: 0, hotNodeCount: 0 };

  const childrenMap = new Map<string, string[]>();
  const parentSet = new Set<string>();
  for (const e of rawEdges) {
    const kids = childrenMap.get(e.from) || [];
    kids.push(e.to);
    childrenMap.set(e.from, kids);
    parentSet.add(e.to);
  }

  const roots = raw.filter((n) => !parentSet.has(n.iri));
  if (roots.length === 0 && raw.length > 0) roots.push(raw[0]);

  const visited = new Set<string>();
  const levels: string[][] = [];

  function bfs(startIds: string[]) {
    let frontier = startIds.filter((id) => !visited.has(id));
    while (frontier.length > 0) {
      levels.push(frontier);
      frontier.forEach((id) => visited.add(id));
      const next: string[] = [];
      for (const id of frontier) {
        for (const kid of childrenMap.get(id) || []) {
          if (!visited.has(kid)) next.push(kid);
        }
      }
      frontier = [...new Set(next)];
    }
  }

  bfs(roots.map((r) => r.iri));
  const unvisited = raw.filter((n) => !visited.has(n.iri)).map((n) => n.iri);
  if (unvisited.length > 0) bfs(unvisited);

  const posMap = new Map<string, { x: number; y: number }>();
  for (let level = 0; level < levels.length; level++) {
    const row = levels[level];
    const totalWidth = row.length * NODE_W + (row.length - 1) * (SIBLING_GAP_X - NODE_W);
    const startX = -totalWidth / 2;
    for (let i = 0; i < row.length; i++) {
      posMap.set(row[i], {
        x: startX + i * SIBLING_GAP_X,
        y: level * (NODE_H + LEVEL_GAP_Y),
      });
    }
  }

  const hotIris = new Set<string>();
  let hotEdgeCount = 0;
  for (const e of rawEdges) {
    if (!isHotPathRel(e.rel)) continue;
    hotEdgeCount += 1;
    hotIris.add(e.from);
    hotIris.add(e.to);
  }

  const nodes: Node<ConceptData>[] = raw.map((n) => ({
    id: n.iri,
    type: 'concept',
    position: posMap.get(n.iri) || { x: 0, y: 0 },
    data: {
      label: n.prefLabel || n.localName || n.iri.split('#').pop() || n.iri,
      sub: n.domainId || n.kind,
      muted: n.kind === 'unmapped',
      pulse: agentPaths && hotIris.has(n.iri),
    },
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
  }));

  const edges: Edge<EdgeData>[] = rawEdges.map((e, i) => {
    const hot = agentPaths && isHotPathRel(e.rel);
    return {
      id: `${e.from}-${e.to}-${e.rel}-${i}`,
      source: e.from,
      target: e.to,
      label: REL_LABEL[e.rel] || e.rel,
      type: 'labeled',
      style: hot
        ? { stroke: 'var(--cta-orange)', strokeWidth: 2, strokeDasharray: '6 4' }
        : { stroke: 'var(--primary)', strokeWidth: 1.5 },
      data: { rel: e.rel, hot },
    };
  });

  return {
    nodes,
    edges: attachHandles(nodes, edges),
    hotEdgeCount,
    hotNodeCount: hotIris.size,
  };
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
}) {
  const byIri = useMemo(() => new Map((payload?.nodes || []).map((n) => [n.iri, n])), [payload]);
  const [nodes, setNodes] = useState<Node<ConceptData>[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [metrics, setMetrics] = useState({ hotEdgeCount: 0, hotNodeCount: 0 });

  useEffect(() => {
    const next = payload
      ? layout(payload, agentPaths)
      : { nodes: [], edges: [], hotEdgeCount: 0, hotNodeCount: 0 };
    setNodes(next.nodes);
    setEdges(next.edges);
    setMetrics({ hotEdgeCount: next.hotEdgeCount, hotNodeCount: next.hotNodeCount });
  }, [payload, agentPaths]);

  const onNodesChange = useCallback((changes: NodeChange<Node<ConceptData>>[]) => {
    setNodes((current) => {
      const next = applyNodeChanges(changes, current);
      setEdges((currentEdges) => attachHandles(next, currentEdges));
      return next;
    });
  }, []);

  if (!payload?.nodes?.length) {
    return <p className="muted">Look up a class, then expand its hierarchy.</p>;
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
          fitViewOptions={{ padding: 0.3 }}
          nodesConnectable={false}
          onNodeClick={(_, node) => {
            const match = byIri.get(node.id);
            if (match && onSelect) onSelect(match);
          }}
          proOptions={{ hideAttribution: true }}
          defaultEdgeOptions={{ type: 'labeled' }}
        >
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
