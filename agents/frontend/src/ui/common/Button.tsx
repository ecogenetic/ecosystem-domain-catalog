import type { ButtonHTMLAttributes, ReactNode } from 'react';

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'cta' | 'danger' | 'ghost' | 'icon';
  children: ReactNode;
};

export function Button({ variant, className = '', children, ...rest }: Props) {
  const v = variant === 'icon' ? 'btn btn-icon' : variant ? `btn btn-${variant}` : 'btn';
  return (
    <button className={`${v} ${className}`.trim()} {...rest}>
      {children}
    </button>
  );
}
