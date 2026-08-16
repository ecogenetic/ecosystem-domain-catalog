export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="card" style={{ textAlign: 'center', margin: '24px auto', maxWidth: 480 }}>
      <h3>{title}</h3>
      <p>{body}</p>
    </div>
  );
}
