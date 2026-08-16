import { catalogPath, dataPath, request } from './http';
import type { ToolDef } from '../contracts/tools';

export async function runTool(tool: ToolDef, payload: Record<string, unknown>, sourceId?: string) {
  const prefix = tool.agent === 'catalog' ? catalogPath : dataPath;
  let path = tool.path;
  if (path.includes('{id}')) {
    const id = String(payload.id || payload.sourceId || sourceId || '');
    path = path.replace('{id}', encodeURIComponent(id));
  }
  if (tool.method === 'GET') {
    const q = new URLSearchParams();
    Object.entries(payload).forEach(([k, v]) => {
      if (v !== undefined && v !== null && k !== 'id' && k !== 'sourceId') q.set(k, String(v));
    });
    const qs = q.toString();
    return request(`${prefix(path)}${qs ? `?${qs}` : ''}`);
  }
  const body = { ...payload };
  return request(prefix(path), { method: 'POST', body: JSON.stringify(body) });
}

export function gatewayHealth() {
  return request<{ ok: boolean; catalog?: string; data?: string }>('/v1/health');
}
