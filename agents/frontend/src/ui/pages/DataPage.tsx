import { useLocation } from 'react-router-dom';
import { CrudAgentPage } from '../data/CrudAgentPage';
import { DataWizard } from '../data/DataWizard';
import { isCrudAgentPath } from '../layout/nav';

export function DataPage() {
  const { pathname } = useLocation();
  if (isCrudAgentPath(pathname)) return <CrudAgentPage />;
  return <DataWizard />;
}
