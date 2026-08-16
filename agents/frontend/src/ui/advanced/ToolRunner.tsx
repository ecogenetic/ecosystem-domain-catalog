import { useMemo, useState } from 'react';
import { CATALOG_TOOLS, DATA_TOOLS, type ToolDef } from '../../contracts/tools';
import { runTool } from '../../adapters/toolsApi';
import { useApp } from '../AppContext';
import { Button } from '../common/Button';
import { JsonPlayground } from './JsonPlayground';
import { TurtleView } from '../common/TurtleView';
import { GraphCanvas } from '../common/GraphCanvas';
import type { GraphPayload } from '../../contracts/catalog';

export function ToolRunner({ agent }: { agent: 'catalog' | 'data' }) {
  const { sourceId } = useApp();
  const tools = agent === 'data' ? DATA_TOOLS : CATALOG_TOOLS;
  const [toolName, setToolName] = useState(tools[0].name);
  const tool = useMemo(() => tools.find((t) => t.name === toolName) || tools[0], [tools, toolName]);
  const [body, setBody] = useState(JSON.stringify(tools[0].example || {}, null, 2));
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  function pick(next: ToolDef) {
    setToolName(next.name);
    setBody(JSON.stringify(next.example || {}, null, 2));
    setResult(null);
    setError('');
  }

  async function send() {
    setBusy(true);
    setError('');
    try {
      const payload = body.trim() ? JSON.parse(body) : {};
      setResult(await runTool(tool, payload, sourceId));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  const turtle = typeof result === 'object' && result && 'turtle' in result ? String((result as { turtle?: string }).turtle || '') : '';
  const graph: GraphPayload | null =
    typeof result === 'object' && result && 'nodes' in (result as object)
      ? (result as GraphPayload)
      : null;

  return (
    <div className="workspace" style={{ minHeight: '70vh' }}>
      <div className="workspace-left">
        {tools.map((t) => (
          <button key={t.name} className={`nav-item${t.name === tool.name ? ' active' : ''}`} type="button" onClick={() => pick(t)}>
            <span className="nav-label">
              {t.method} {t.name}
            </span>
          </button>
        ))}
      </div>
      <div className="workspace-right">
        <p className="muted">
          {tool.method} /{agent}
          {tool.path} — {tool.description}
        </p>
        <JsonPlayground value={body} onChange={setBody} />
        <Button variant="cta" disabled={busy} onClick={() => void send()}>
          Run
        </Button>
        {error && <p className="error">{error}</p>}
        {result != null && (
          <>
            <pre className="pre">{JSON.stringify(result, null, 2)}</pre>
            {turtle ? <TurtleView turtle={turtle} /> : null}
            {graph?.nodes?.length ? <div style={{ height: 320 }}><GraphCanvas payload={graph} /></div> : null}
          </>
        )}
      </div>
    </div>
  );
}
