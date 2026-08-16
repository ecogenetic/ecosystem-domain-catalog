import { useState } from 'react';
import { catalogApi } from '../../adapters/catalogApi';
import { dataApi } from '../../adapters/dataApi';
import { Button } from '../common/Button';
import { JsonView } from '../common/JsonView';

export function McpPanel() {
  const [agent, setAgent] = useState<'catalog' | 'data'>('catalog');
  const [name, setName] = useState('search_catalog');
  const [args, setArgs] = useState('{\n  "query": "deal"\n}');
  const [out, setOut] = useState<unknown>(null);
  const [error, setError] = useState('');
  const api = agent === 'catalog' ? catalogApi : dataApi;

  async function call() {
    setError('');
    try {
      const parsed = args.trim() ? JSON.parse(args) : {};
      setOut(await api.mcpCall(name, parsed));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div>
      <div className="filter-row" style={{ justifyContent: 'flex-start' }}>
        <select
          value={agent}
          onChange={(e) => {
            const next = e.target.value as 'catalog' | 'data';
            setAgent(next);
            setName(next === 'catalog' ? 'search_catalog' : 'query_mapped_data');
          }}
        >
          <option value="catalog">Catalog MCP</option>
          <option value="data">Data MCP</option>
        </select>
        <Button onClick={() => void api.mcpInfo().then(setOut)}>info</Button>
        <Button onClick={() => void api.mcpList().then(setOut)}>tools/list</Button>
      </div>
      <p className="muted">
        GET /{agent}/mcp/info · POST /{agent}/mcp/tools/list · POST /{agent}/mcp/tools/call
      </p>
      <div className="form-group">
        <label>Tool name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div className="form-group">
        <label>arguments JSON</label>
        <textarea rows={8} value={args} onChange={(e) => setArgs(e.target.value)} />
      </div>
      <Button variant="cta" onClick={() => void call()}>
        tools/call
      </Button>
      {error && <p className="error">{error}</p>}
      {out != null && <JsonView value={out} />}
    </div>
  );
}
