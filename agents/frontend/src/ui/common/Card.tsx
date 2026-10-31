import type { CSSProperties, ReactNode } from 'react';

export function Card({
  children,
  interactive,
  onClick,
  className,
  style,
}: {
  children: ReactNode;
  interactive?: boolean;
  onClick?: () => void;
  className?: string;
  style?: CSSProperties;
}) {
  return (
    <div
      className={`card${interactive || onClick ? ' interactive' : ''}${className ? ` ${className}` : ''}`}
      style={style}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </div>
  );
}
