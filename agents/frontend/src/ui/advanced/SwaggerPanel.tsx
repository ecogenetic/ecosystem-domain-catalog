import { useState } from 'react';

export function SwaggerPanel() {
  const [agent, setAgent] = useState<'catalog' | 'data'>('catalog');
  const base = `/${agent}`;
  return (
    <div>
      <div className="tabs">
        <button className={`tab${agent === 'catalog' ? ' active' : ''}`} type="button" onClick={() => setAgent('catalog')}>
          Catalog Swagger
        </button>
        <button className={`tab${agent === 'data' ? ' active' : ''}`} type="button" onClick={() => setAgent('data')}>
          Data Swagger
        </button>
        <a className="tab" href={`${base}/docs`} target="_blank" rel="noreferrer">
          Open in new tab
        </a>
        <a className="tab" href={`${base}/redoc`} target="_blank" rel="noreferrer">
          ReDoc
        </a>
        <a className="tab" href={`${base}/openapi.json`} target="_blank" rel="noreferrer">
          openapi.json
        </a>
      </div>
      <iframe className="swagger-frame" title={`${agent} Swagger`} src={`${base}/docs`} />
    </div>
  );
}
