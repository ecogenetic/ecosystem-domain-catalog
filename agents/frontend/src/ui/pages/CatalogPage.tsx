import { useLocation } from 'react-router-dom';
import { CatalogHome } from '../catalog/CatalogHome';
import { GraphPanel } from '../catalog/GraphPanel';
import { SessionOntologyPage } from '../catalog/SessionOntologyPage';
import { useApp } from '../AppContext';
import { catalogSection } from '../layout/nav';

export function CatalogPage() {
  const { catalogKey } = useApp();
  const { pathname } = useLocation();
  const section = catalogSection(pathname);

  if (section === 'session') return <SessionOntologyPage />;
  if (section === 'hierarchy') return <GraphPanel advanced />;
  return (
    <div className="page-fill">
      <CatalogHome key={catalogKey} mode={section === 'overview' ? 'overview' : 'workspace'} />
    </div>
  );
}
