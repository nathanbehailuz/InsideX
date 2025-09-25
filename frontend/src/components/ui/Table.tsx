/**
 * Reusable Table component with sorting and pagination
 */

import { ReactNode, useState } from 'react';
import { ChevronUpIcon, ChevronDownIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { TableColumn, SortDirection } from '@/lib/types';

interface TableProps {
  columns: TableColumn[];
  data: any[];
  loading?: boolean;
  sortable?: boolean;
  onSort?: (column: string, direction: SortDirection) => void;
  className?: string;
}

export function Table({ 
  columns, 
  data, 
  loading = false,
  sortable = true,
  onSort,
  className 
}: TableProps) {
  const [sortColumn, setSortColumn] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const handleSort = (column: TableColumn) => {
    if (!sortable || !column.sortable) return;

    const newDirection = sortColumn === column.key && sortDirection === 'asc' ? 'desc' : 'asc';
    setSortColumn(column.key);
    setSortDirection(newDirection);
    onSort?.(column.key, newDirection);
  };

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-12 bg-gray-200 rounded mb-4"></div>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-10 bg-gray-100 rounded mb-2"></div>
        ))}
      </div>
    );
  }

  return (
    <div className={cn('overflow-x-auto', className)}>
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                className={cn(
                  'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                  sortable && column.sortable && 'cursor-pointer hover:bg-gray-100'
                )}
                onClick={() => handleSort(column)}
              >
                <div className="flex items-center space-x-1">
                  <span>{column.label}</span>
                  {sortable && column.sortable && (
                    <span className="flex flex-col">
                      <ChevronUpIcon 
                        className={cn(
                          'h-3 w-3',
                          sortColumn === column.key && sortDirection === 'asc'
                            ? 'text-gray-900'
                            : 'text-gray-400'
                        )} 
                      />
                      <ChevronDownIcon 
                        className={cn(
                          'h-3 w-3 -mt-1',
                          sortColumn === column.key && sortDirection === 'desc'
                            ? 'text-gray-900'
                            : 'text-gray-400'
                        )} 
                      />
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.length === 0 ? (
            <tr>
              <td 
                colSpan={columns.length}
                className="px-6 py-12 text-center text-gray-500"
              >
                No data available
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr 
                key={rowIndex}
                className="hover:bg-gray-50 transition-colors duration-150"
              >
                {columns.map((column) => (
                  <td 
                    key={column.key}
                    className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                  >
                    {column.format ? column.format(row[column.key]) : row[column.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export function Pagination({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange,
  className
}: PaginationProps) {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  return (
    <div className={cn('flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200 sm:px-6', className)}>
      <div className="flex justify-between flex-1 sm:hidden">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="relative inline-flex items-center px-4 py-2 ml-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
      <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-gray-700">
            Showing <span className="font-medium">{startItem}</span> to{' '}
            <span className="font-medium">{endItem}</span> of{' '}
            <span className="font-medium">{totalItems}</span> results
          </p>
        </div>
        <div>
          <nav className="relative z-0 inline-flex -space-x-px rounded-md shadow-sm">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage <= 1}
              className="relative inline-flex items-center px-2 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-l-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            {/* Page numbers */}
            {[...Array(Math.min(totalPages, 5))].map((_, i) => {
              let pageNum = i + 1;
              if (totalPages > 5 && currentPage > 3) {
                pageNum = currentPage - 2 + i;
                if (pageNum > totalPages) pageNum = totalPages - 4 + i;
              }
              
              return (
                <button
                  key={pageNum}
                  onClick={() => onPageChange(pageNum)}
                  className={cn(
                    'relative inline-flex items-center px-4 py-2 text-sm font-medium border',
                    pageNum === currentPage
                      ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                  )}
                >
                  {pageNum}
                </button>
              );
            })}
            
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
              className="relative inline-flex items-center px-2 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-r-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </nav>
        </div>
      </div>
    </div>
  );
}