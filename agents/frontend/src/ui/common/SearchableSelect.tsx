import { ChevronDown } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';

export type SearchableOption = {
  id: string;
  label: string;
  hint?: string;
  /** Optional list section header (e.g. Your ontologies). */
  group?: string;
  /** Visual tone — session uploads use light blue. */
  tone?: 'session';
};

export function SearchableSelect({
  value,
  options,
  allLabel,
  placeholder = 'Search…',
  onChange,
  ariaLabel,
  className = '',
}: {
  value: string;
  options: SearchableOption[];
  allLabel: string;
  placeholder?: string;
  onChange: (id: string) => void;
  ariaLabel?: string;
  className?: string;
}) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [typed, setTyped] = useState('');
  const selected = options.find((o) => o.id === value);
  const display = open ? typed : selected?.label || allLabel;

  const filtered = useMemo(() => {
    const q = typed.trim().toLowerCase();
    const list = !q
      ? options
      : options.filter((o) =>
          [o.id, o.label, o.hint, o.group].filter(Boolean).join(' ').toLowerCase().includes(q),
        );
    // Session / uploaded options stay first when present.
    return [...list].sort((a, b) => {
      const at = a.tone === 'session' ? 0 : 1;
      const bt = b.tone === 'session' ? 0 : 1;
      if (at !== bt) return at - bt;
      return 0;
    });
  }, [options, typed]);

  const grouped = useMemo(() => {
    const sections: { label: string | null; items: SearchableOption[] }[] = [];
    for (const opt of filtered) {
      const label = opt.group || null;
      const last = sections[sections.length - 1];
      if (last && last.label === label) last.items.push(opt);
      else sections.push({ label, items: [opt] });
    }
    return sections;
  }, [filtered]);

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

  const sessionSelected = selected?.tone === 'session';

  return (
    <div
      className={`searchable-select${open ? ' open' : ''}${sessionSelected ? ' searchable-select--session' : ''}${className ? ` ${className}` : ''}`}
      ref={rootRef}
    >
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
          {grouped.map((section) => (
            <li key={section.label || '__ungrouped'} className="searchable-select-section">
              {section.label ? (
                <div
                  className={`searchable-select-group${
                    section.items.some((i) => i.tone === 'session') ? ' searchable-select-group--session' : ''
                  }`}
                >
                  {section.label}
                </div>
              ) : null}
              <ul className="searchable-select-sublist">
                {section.items.map((o) => (
                  <li key={o.id}>
                    <button
                      type="button"
                      role="option"
                      aria-selected={o.id === value}
                      className={o.tone === 'session' ? 'searchable-option--session' : undefined}
                      onClick={() => pick(o.id)}
                    >
                      <span>{o.label}</span>
                      {o.hint ? <span className="muted">{o.hint}</span> : null}
                    </button>
                  </li>
                ))}
              </ul>
            </li>
          ))}
          {!filtered.length && <li className="muted searchable-select-empty">No matching ontologies</li>}
        </ul>
      )}
    </div>
  );
}
