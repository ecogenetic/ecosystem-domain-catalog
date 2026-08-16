import { useEffect, useMemo, useState } from 'react';
import {
  BookOpen,
  ChevronRight,
  Database,
  Moon,
  PanelLeft,
  PanelLeftClose,
  Search,
  Sun,
  TerminalSquare,
} from 'lucide-react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useApp } from '../AppContext';
import { Button } from '../common/Button';
import {
  filterTree,
  groupIdsForPath,
  hydrateNav,
  pathIsActive,
  type NavIcon,
  type NavNode,
} from './nav';

const ECOSYSTEM_LOGO = 'https://ecosystemcode.com/favicon-48x48.png';

const ICONS: Record<NavIcon, typeof BookOpen> = {
  book: BookOpen,
  database: Database,
  terminal: TerminalSquare,
};

export function Sidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const { resetCatalog, domains, industries, sessionLibrary } = useApp();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [query, setQuery] = useState('');
  const tree = useMemo(
    () => hydrateNav(domains, industries, sessionLibrary.items),
    [domains, industries, sessionLibrary.items],
  );
  const visible = useMemo(() => filterTree(tree, query), [tree, query]);
  const [open, setOpen] = useState<Record<string, boolean>>({
    ontology: true,
    yours: true,
    types: false,
    overlays: false,
    data: false,
    developers: false,
  });

  useEffect(() => {
    const ids = groupIdsForPath(tree, pathname);
    if (!ids.length) return;
    setOpen((cur) => {
      const next = { ...cur };
      for (const id of ids) next[id] = true;
      return next;
    });
  }, [pathname, tree]);

  function goHome() {
    resetCatalog();
    navigate('/');
  }

  function toggleGroup(id: string) {
    setOpen((cur) => ({ ...cur, [id]: !cur[id] }));
  }

  if (collapsed) {
    return (
      <aside className="app-sidebar collapsed">
        <div className="brand">
          <button type="button" className="brand-mark" title="Ontology home" onClick={goHome}>
            <img src={ECOSYSTEM_LOGO} alt="ecosystem.Ai" />
          </button>
        </div>
        <nav className="nav-tree">
          {tree.map((group) => {
            const Icon = group.icon ? ICONS[group.icon] : BookOpen;
            const active =
              group.id === 'ontology'
                ? pathname === '/' || pathname.startsWith('/ontology')
                : group.id === 'data'
                  ? pathname.startsWith('/sources')
                  : pathname.startsWith('/advanced');
            return (
              <NavLink
                key={group.id}
                to={group.to || '/'}
                title={group.label}
                className={`nav-leaf icon-only${active ? ' active' : ''}`}
                onClick={onToggle}
              >
                <Icon size={16} />
              </NavLink>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <ThemeButton />
          <Button variant="icon" onClick={onToggle} title="Show sidebar">
            <PanelLeft size={16} />
          </Button>
        </div>
      </aside>
    );
  }

  return (
    <aside className="app-sidebar">
      <div className="brand">
        <button type="button" className="brand-mark" title="Ontology home" onClick={goHome}>
          <img src={ECOSYSTEM_LOGO} alt="ecosystem.Ai" />
        </button>
        <button type="button" className="brand-text" title="Ontology home" onClick={goHome}>
          ecosystem.Ai Ontology
        </button>
      </div>
      <label className="sidebar-search">
        <Search size={14} />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search"
          aria-label="Filter navigation"
        />
      </label>
      <nav className="nav-tree">
        {visible.map((group) => (
          <NavBranch
            key={group.id}
            node={group}
            depth={0}
            open={open}
            forceOpen={Boolean(query.trim())}
            onToggle={toggleGroup}
            pathname={pathname}
          />
        ))}
        {visible.length === 0 && <p className="nav-empty">No matching pages</p>}
      </nav>
      <div className="sidebar-footer">
        <ThemeButton />
        <Button variant="icon" onClick={onToggle} title="Hide sidebar">
          <PanelLeftClose size={16} />
        </Button>
      </div>
    </aside>
  );
}

function NavBranch({
  node,
  depth,
  open,
  forceOpen,
  onToggle,
  pathname,
}: {
  node: NavNode;
  depth: number;
  open: Record<string, boolean>;
  forceOpen: boolean;
  onToggle: (id: string) => void;
  pathname: string;
}) {
  const hasChildren = Boolean(node.children?.length);
  const expanded = forceOpen || Boolean(open[node.id]);
  const Icon = depth === 0 && node.icon ? ICONS[node.icon] : null;
  const active = !hasChildren && pathIsActive(node.to, pathname, node.end);

  if (!hasChildren && node.to) {
    return (
      <NavLink
        to={node.to}
        end={node.end || node.to === '/'}
        title={node.hint || node.label}
        className={`nav-leaf depth-${depth}${active ? ' active' : ''}`}
      >
        <span className="nav-leaf-label">{node.label}</span>
        {node.hint && <span className="nav-leaf-hint">{node.hint}</span>}
      </NavLink>
    );
  }

  return (
    <div className={`nav-group depth-${depth}`}>
      <button
        type="button"
        className="nav-group-toggle"
        onClick={() => onToggle(node.id)}
        aria-expanded={expanded}
      >
        <ChevronRight size={14} className={`nav-chevron${expanded ? ' open' : ''}`} />
        {Icon && <Icon size={15} />}
        <span>{node.label}</span>
      </button>
      {expanded && (
        <div className="nav-children">
          {node.children?.map((child) => (
            <NavBranch
              key={child.id}
              node={child}
              depth={depth + 1}
              open={open}
              forceOpen={forceOpen}
              onToggle={onToggle}
              pathname={pathname}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ThemeButton() {
  const { theme, toggleTheme } = useApp();
  return (
    <Button variant="icon" onClick={toggleTheme} title="Theme">
      {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
    </Button>
  );
}
