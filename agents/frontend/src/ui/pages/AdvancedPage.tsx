import { useLocation } from 'react-router-dom';
import { ToolRunner } from '../advanced/ToolRunner';
import { SwaggerPanel } from '../advanced/SwaggerPanel';
import { McpPanel } from '../advanced/McpPanel';
import { advancedSection } from '../layout/nav';

export function AdvancedPage() {
  const { pathname } = useLocation();
  const section = advancedSection(pathname);
  return (
    <div className="page">
      {section === 'catalog' && <ToolRunner agent="catalog" />}
      {section === 'data' && <ToolRunner agent="data" />}
      {section === 'docs' && <SwaggerPanel />}
      {section === 'mcp' && <McpPanel />}
    </div>
  );
}
