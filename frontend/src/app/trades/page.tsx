/**
 * Trades page with searchable/filterable insider trade table
 */

'use client';

import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { ActivityIcon, FilterIcon, SearchIcon } from 'lucide-react';

import { AppShell } from '@/components/layout/Navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { TradeBadge } from '@/components/ui/Badge';
import { LoadingState, LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Table, Pagination } from '@/components/ui/Table';
import {
  getTrades,
  getTradeStats,
  formatCurrency,
  formatDate,
  formatNumber,
} from '@/lib/api';
import type { DatabaseStats, TableColumn, Trade } from '@/lib/types';

const PAGE_SIZE = 25;

interface TradeFilters {
  ticker: string;
  insider_name: string;
  trade_type: string;
  date_from: string;
  date_to: string;
  min_value_usd: string;
}

const emptyFilters: TradeFilters = {
  ticker: '',
  insider_name: '',
  trade_type: '',
  date_from: '',
  date_to: '',
  min_value_usd: '',
};

function TradesContent() {
  const searchParams = useSearchParams();
  const tickerParam = searchParams.get('ticker')?.toUpperCase() || '';

  const initialFilters: TradeFilters = {
    ...emptyFilters,
    ticker: tickerParam,
  };

  const [trades, setTrades] = useState<Trade[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<TradeFilters>(initialFilters);
  const [appliedFilters, setAppliedFilters] = useState<TradeFilters>(initialFilters);

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    if (tickerParam !== appliedFilters.ticker) {
      const next = { ...emptyFilters, ticker: tickerParam };
      setFilters(next);
      setAppliedFilters(next);
      setPage(1);
    }
  }, [tickerParam]);

  useEffect(() => {
    loadTrades();
  }, [page, appliedFilters]);

  const loadStats = async () => {
    try {
      const statsResponse = await getTradeStats();
      setStats(statsResponse);
    } catch (err) {
      console.error('Error loading trade stats:', err);
    }
  };

  const loadTrades = async () => {
    try {
      setLoading(true);
      setError(null);

      const minValue = appliedFilters.min_value_usd
        ? Number(appliedFilters.min_value_usd)
        : undefined;

      const response = await getTrades({
        limit: PAGE_SIZE,
        offset: (page - 1) * PAGE_SIZE,
        ticker: appliedFilters.ticker.trim() || undefined,
        insider_name: appliedFilters.insider_name.trim() || undefined,
        trade_type: appliedFilters.trade_type || undefined,
        date_from: appliedFilters.date_from || undefined,
        date_to: appliedFilters.date_to || undefined,
        min_value_usd:
          minValue != null && !Number.isNaN(minValue) ? minValue : undefined,
      });

      setTrades(response.trades);
      setTotal(response.total);
    } catch (err) {
      console.error('Error loading trades:', err);
      setError('Failed to load trades. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    setPage(1);
    setAppliedFilters({ ...filters });
  };

  const clearFilters = () => {
    setFilters(emptyFilters);
    setAppliedFilters(emptyFilters);
    setPage(1);
  };

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const columns: TableColumn[] = [
    {
      key: 'trade_date',
      label: 'Trade Date',
      format: (value) => formatDate(value as string),
    },
    {
      key: 'ticker',
      label: 'Ticker',
      format: (value) =>
        value ? (
          <Link
            href={`/companies?ticker=${encodeURIComponent(String(value))}`}
            className="font-semibold text-primary hover:text-primary"
          >
            {String(value)}
          </Link>
        ) : (
          '—'
        ),
    },
    {
      key: 'company_name',
      label: 'Company',
      format: (value) => (
        <span className="max-w-[180px] truncate block" title={String(value || '')}>
          {(value as string) || '—'}
        </span>
      ),
    },
    {
      key: 'insider_name',
      label: 'Insider',
      format: (value) => (value as string) || '—',
    },
    {
      key: 'title',
      label: 'Title',
      format: (value) => (value as string) || '—',
    },
    {
      key: 'trade_type',
      label: 'Type',
      format: (value) =>
        value ? <TradeBadge tradeType={String(value)} /> : '—',
    },
    {
      key: 'price',
      label: 'Price',
      format: (value) =>
        value != null ? formatCurrency(value as number) : '—',
    },
    {
      key: 'qty',
      label: 'Qty',
      format: (value) =>
        value != null ? formatNumber(value as number) : '—',
    },
    {
      key: 'value',
      label: 'Value',
      format: (value) =>
        value != null ? formatCurrency(Math.abs(value as number)) : '—',
    },
  ];

  return (
    <AppShell>
        <div className="mb-8">
          <h1 className="text-3xl md:text-[40px] md:leading-[48px] font-bold text-on-surface tracking-tight">Insider Trades</h1>
          <p className="text-secondary mt-2">
            Browse and filter Form 4 insider trading activity
          </p>
        </div>

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <CardContent className="p-6">
                <p className="text-sm font-medium text-secondary">Total Trades</p>
                <p className="text-2xl font-bold text-on-surface">
                  {formatNumber(stats.total_records)}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <p className="text-sm font-medium text-secondary">Companies</p>
                <p className="text-2xl font-bold text-on-surface">
                  {formatNumber(stats.unique_companies)}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <p className="text-sm font-medium text-secondary">People</p>
                <p className="text-2xl font-bold text-on-surface">
                  {formatNumber(stats.unique_insiders)}
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="flex items-center space-x-2 mb-4">
              <FilterIcon className="h-4 w-4 text-secondary" />
              <span className="text-sm font-medium text-on-surface">Filters</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs text-secondary mb-1">Ticker</label>
                <input
                  type="text"
                  value={filters.ticker}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, ticker: e.target.value.toUpperCase() }))
                  }
                  placeholder="e.g. AAPL"
                  className="w-full px-3 py-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary-container focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-xs text-secondary mb-1">Insider Name</label>
                <input
                  type="text"
                  value={filters.insider_name}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, insider_name: e.target.value }))
                  }
                  placeholder="Search by name"
                  className="w-full px-3 py-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary-container focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-xs text-secondary mb-1">Trade Type</label>
                <select
                  value={filters.trade_type}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, trade_type: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary-container focus:border-transparent"
                >
                  <option value="">All Types</option>
                  <option value="P - Purchase">Purchase</option>
                  <option value="S - Sale">Sale</option>
                  <option value="S - Sale+OE">Sale + OE</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-secondary mb-1">Date From</label>
                <input
                  type="date"
                  value={filters.date_from}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, date_from: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary-container focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-xs text-secondary mb-1">Date To</label>
                <input
                  type="date"
                  value={filters.date_to}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, date_to: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary-container focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-xs text-secondary mb-1">Min Value (USD)</label>
                <input
                  type="number"
                  min="0"
                  value={filters.min_value_usd}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, min_value_usd: e.target.value }))
                  }
                  placeholder="e.g. 100000"
                  className="w-full px-3 py-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary-container focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex flex-wrap gap-3 mt-4">
              <button
                onClick={applyFilters}
                className="inline-flex items-center px-4 py-2 bg-primary-container text-white text-sm rounded-lg hover:opacity-90 transition-colors"
              >
                <SearchIcon className="h-4 w-4 mr-2" />
                Apply Filters
              </button>
              <button
                onClick={clearFilters}
                className="px-4 py-2 bg-white border border-border text-on-surface text-sm rounded-lg hover:bg-surface-bright transition-colors"
              >
                Clear
              </button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <ActivityIcon className="h-5 w-5 mr-2" />
              Trade Activity
              {!loading && (
                <span className="ml-2 text-sm font-normal text-secondary">
                  ({formatNumber(total)} results)
                </span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <LoadingState loading={loading} error={error} loadingText="Loading trades...">
              <Table columns={columns} data={trades} sortable={false} />
              {total > 0 && (
                <Pagination
                  currentPage={page}
                  totalPages={totalPages}
                  totalItems={total}
                  itemsPerPage={PAGE_SIZE}
                  onPageChange={setPage}
                />
              )}
            </LoadingState>
          </CardContent>
        </Card>
    </AppShell>
  );
}

export default function TradesPage() {
  return (
    <Suspense
      fallback={
        <AppShell>
          <div className="flex flex-col items-center justify-center py-24">
            <LoadingSpinner size="lg" />
            <p className="mt-2 text-sm text-secondary">Loading trades...</p>
          </div>
        </AppShell>
      }
    >
      <TradesContent />
    </Suspense>
  );
}
