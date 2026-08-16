import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { AppShell } from './ui/layout/AppShell';
import { CatalogPage } from './ui/pages/CatalogPage';
import { DataPage } from './ui/pages/DataPage';
import { AdvancedPage } from './ui/pages/AdvancedPage';

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="*" element={<Workspaces />} />
      </Route>
    </Routes>
  );
}

function Workspaces() {
  const { pathname } = useLocation();
  if (pathname === '/data') return <Navigate to="/sources/connect" replace />;
  if (pathname === '/sources') return <Navigate to="/sources/connect" replace />;
  if (pathname.startsWith('/sources')) return <DataPage />;
  if (pathname === '/advanced') return <Navigate to="/advanced/catalog" replace />;
  if (pathname.startsWith('/advanced')) return <AdvancedPage />;
  if (pathname === '/' || pathname.startsWith('/ontology')) return <CatalogPage />;
  return <Navigate to="/" replace />;
}
