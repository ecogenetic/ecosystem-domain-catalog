import type { ReactNode } from 'react';

export function Card({
  children,
  interactive,
  onClick,
  className,
}: {
  children: ReactNode;
  interactive?: boolean;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <div
      className={`card${interactive || onClick ? ' interactive' : ''}${className ? ` ${className}` : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </div>
  );
}
