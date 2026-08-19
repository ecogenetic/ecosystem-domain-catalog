import { Moon, Sun } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { useApp } from '../AppContext';
import { Button } from '../common/Button';
import { HealthChip } from '../common/HealthChip';
import { headerCopy } from './nav';

export function Header() {
  const { pathname } = useLocation();
  const {
    useLlm,
    setUseLlm,
    catalogOk,
    dataOk,
    domains,
    industries,
    sessionLibrary,
    theme,
    toggleTheme,
    sourceKind,
  } = useApp();
  const copy = headerCopy(pathname, domains, industries, sessionLibrary.items);
  const showLlm = !pathname.startsWith('/advanced') && !pathname.includes('/ontology/yours');
  const llmCopy = pathname.startsWith('/sources')
    ? {
        label: 'Ask with AI',
        title: 'Uses mapped fields first, then the AI may refine the query plan',
      }
    : {
        label: 'Rank with AI',
        title: 'Looks up classes in the graph first, then the AI re-ranks matching IRIs',
      };
  const env =
    sourceKind === 'mongodb' || sourceKind === 'postgresql' ? 'PRODUCTION' : 'SANDBOX';

  return (
    <header className="app-header">
      <div className="header-left">
        <div>
          <h1 className="header-title">{copy.title}</h1>
          <div className="header-sub">{copy.sub}</div>
        </div>
      </div>
      <div className="header-right">
        <span className={`env-pill${env === 'PRODUCTION' ? ' production' : ''}`} title="Connected source environment">
          {env}
        </span>
        {showLlm && (
          <label className="toggle" title={llmCopy.title}>
            <input type="checkbox" checked={useLlm} onChange={(e) => setUseLlm(e.target.checked)} />
            {llmCopy.label}
          </label>
        )}
        <HealthChip ok={catalogOk} label="Catalog" />
        <HealthChip ok={dataOk} label="Data" />
        <Button variant="icon" onClick={toggleTheme} title="Theme">
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </Button>
      </div>
    </header>
  );
}
