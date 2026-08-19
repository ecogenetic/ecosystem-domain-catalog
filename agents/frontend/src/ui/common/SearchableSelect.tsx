import { ChevronDown } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

export type SearchableOption = { id: string; label: string; hint?: string };

export function SearchableSelect({
  value,
  options,
  allLabel,
  placeholder = 'Search…',
  onChange,
  ariaLabel,
}: {
  value: string;
  options: SearchableOption[];
  allLabel: string;
  placeholder?: string;
  onChange: (id: string) => void;
  ariaLabel?: string;
}) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [typed, setTyped] = useState('');
  const selected = options.find((o) => o.id === value);
  const display = open ? typed : selected?.label || allLabel;

  const filtered = useMemo(() => {
    const q = typed.trim().toLowerCase();
    if (!q) return options;
    return options.filter((o) =>
      [o.id, o.label, o.hint].filter(Boolean).join(' ').toLowerCase().includes(q),
    );
  }, [options, typed]);

  useEffect(() => {
    function onDoc(e: MouseEvent) {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, []);

  function pick(id: string) {
    onChange(id);
    setTyped('');
    setOpen(false);
  }

  return (
    <div className={`searchable-select${open ? ' open' : ''}`} ref={rootRef}>
      <input
        value={display}
        aria-label={ariaLabel || allLabel}
        aria-expanded={open}
        aria-autocomplete="list"
        role="combobox"
        placeholder={placeholder}
        onFocus={() => {
          setOpen(true);
          setTyped('');
        }}
        onChange={(e) => {
          setOpen(true);
          setTyped(e.target.value);
        }}
        onKeyDown={(e) => {
          if (e.key === 'Escape') {
            setOpen(false);
            setTyped('');
          }
          if (e.key === 'Enter') {
            e.preventDefault();
            const first = filtered[0];
            if (typed.trim() === '') pick('');
            else if (first) pick(first.id);
          }
        }}
      />
      <ChevronDown size={14} className="searchable-select-caret" />
      {open && (
        <ul className="searchable-select-list" role="listbox">
          <li>
            <button type="button" role="option" aria-selected={!value} onClick={() => pick('')}>
              {allLabel}
            </button>
          </li>
          {filtered.map((o) => (
            <li key={o.id}>
              <button type="button" role="option" aria-selected={o.id === value} onClick={() => pick(o.id)}>
                <span>{o.label}</span>
                {o.hint ? <span className="muted">{o.hint}</span> : null}
              </button>
            </li>
          ))}
          {!filtered.length && <li className="muted searchable-select-empty">No matching ontologies</li>}
        </ul>
      )}
    </div>
  );
}
