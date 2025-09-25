/**
 * Loading spinner components
 */

import { cn } from '@/lib/utils';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export function LoadingSpinner({ size = 'md', className }: SpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12'
  };

  return (
    <div className="flex justify-center items-center">
      <div
        className={cn(
          'animate-spin rounded-full border-2 border-gray-300 border-t-blue-600',
          sizeClasses[size],
          className
        )}
      />
    </div>
  );
}

interface LoadingStateProps {
  loading: boolean;
  error?: string | null;
  children: React.ReactNode;
  loadingText?: string;
  className?: string;
}

export function LoadingState({
  loading,
  error,
  children,
  loadingText = 'Loading...',
  className
}: LoadingStateProps) {
  if (loading) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12', className)}>
        <LoadingSpinner size="lg" />
        <p className="mt-2 text-sm text-gray-500">{loadingText}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12', className)}>
        <div className="text-red-500 text-center">
          <svg className="h-12 w-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Data</h3>
          <p className="text-sm text-gray-500 max-w-md">{error}</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

export function TableSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="animate-pulse">
      {/* Table header */}
      <div className="bg-gray-50 p-4 rounded-t-lg">
        <div className="flex space-x-4">
          {[...Array(columns)].map((_, i) => (
            <div key={i} className="flex-1 h-4 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
      
      {/* Table rows */}
      <div className="bg-white border border-t-0 rounded-b-lg">
        {[...Array(rows)].map((_, rowIndex) => (
          <div key={rowIndex} className="p-4 border-b border-gray-200 last:border-b-0">
            <div className="flex space-x-4">
              {[...Array(columns)].map((_, colIndex) => (
                <div key={colIndex} className="flex-1">
                  <div className={cn(
                    'h-4 bg-gray-200 rounded',
                    colIndex === 0 ? 'bg-gray-300' : 'bg-gray-200'
                  )}></div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="animate-pulse bg-white p-6 rounded-lg border border-gray-200">
      <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded w-full"></div>
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    </div>
  );
}
