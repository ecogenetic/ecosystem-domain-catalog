import type { ReactNode } from 'react';

export function Card({
  children,
  interactive,
  onClick,
}: {
  children: ReactNode;
  interactive?: boolean;
  onClick?: () => void;
}) {
  return (
    <div
      className={`card${interactive || onClick ? ' interactive' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </div>
  );
}
