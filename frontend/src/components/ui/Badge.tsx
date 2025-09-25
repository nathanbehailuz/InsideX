/**
 * Reusable Badge component for signals and status indicators
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
  className 
}: BadgeProps) {
  const variantClasses = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
    outline: 'border border-gray-300 text-gray-700 bg-white'
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full font-medium',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {children}
    </span>
  );
}

interface SignalBadgeProps {
  confidence: 'low' | 'medium' | 'high';
  score?: number;
  className?: string;
}

export function SignalBadge({ confidence, score, className }: SignalBadgeProps) {
  const variant = confidence === 'high' ? 'success' : 
                 confidence === 'medium' ? 'warning' : 'danger';

  return (
    <Badge variant={variant} className={className}>
      {confidence.toUpperCase()}
      {score && ` (${Math.round(score * 100)}%)`}
    </Badge>
  );
}

interface TradeBadgeProps {
  tradeType: 'Buy' | 'Sell' | string;
  className?: string;
}

export function TradeBadge({ tradeType, className }: TradeBadgeProps) {
  const variant = tradeType?.toLowerCase() === 'buy' ? 'success' : 'danger';

  return (
    <Badge variant={variant} size="sm" className={className}>
      {tradeType}
    </Badge>
  );
}
