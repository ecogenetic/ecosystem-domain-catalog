export function JsonPlayground({
  value,
  onChange,
}: {
  value: string;
  onChange: (next: string) => void;
}) {
  return (
    <div className="form-group">
      <label>JSON body / query</label>
      <textarea rows={10} value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}
