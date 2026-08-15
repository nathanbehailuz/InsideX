/**
 * Badges — Stitch confidence / trade chips
 */

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  className,
}: BadgeProps) {
  const variantClasses = {
    default: 'bg-surface-container text-on-surface-variant',
    success: 'bg-success/15 text-success',
    warning: 'bg-warning/15 text-warning',
    danger: 'bg-danger/15 text-danger',
    info: 'bg-primary/10 text-primary',
    outline: 'border border-border text-secondary bg-surface',
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-semibold tracking-wide',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {children}
    </span>
  );
}

export function SignalBadge({
  confidence,
  score,
  className,
}: {
  confidence: 'low' | 'medium' | 'high';
  score?: number;
  className?: string;
}) {
  const variant =
    confidence === 'high' ? 'success' : confidence === 'medium' ? 'warning' : 'default';

  return (
    <Badge variant={variant} size="sm" className={className}>
      {confidence.toUpperCase()}
      {score != null && ` · ${Math.round(score * 100)}%`}
    </Badge>
  );
}

export function TradeBadge({
  tradeType,
  className,
}: {
  tradeType: string;
  className?: string;
}) {
  const normalized = tradeType?.toLowerCase() ?? '';
  const isBuy =
    normalized === 'buy' ||
    normalized.startsWith('p -') ||
    normalized.includes('purchase');

  return (
    <Badge variant={isBuy ? 'success' : 'danger'} size="sm" className={className}>
      {tradeType}
    </Badge>
  );
}
