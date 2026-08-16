export function HealthChip({ ok, label }: { ok: boolean | null; label: string }) {
  const cls = ok ? 'ok' : ok === false ? 'bad' : '';
  return <span className={`health-dot ${cls}`} title={label} aria-label={`${label} ${ok ? 'online' : 'offline'}`} />;
}
