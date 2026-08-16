export function TurtleView({ turtle }: { turtle: string }) {
  return <pre className="pre">{turtle || 'No Turtle returned.'}</pre>;
}
