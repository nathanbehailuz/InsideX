/**
 * Companies page — browse active tickers and look up company details
 */

'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  BuildingIcon,
  FilterIcon,
  SearchIcon,
  ActivityIcon,
} from 'lucide-react';

import { AppShell } from '@/components/layout/Navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { TradeBadge } from '@/components/ui/Badge';
import { LoadingState, LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Table } from '@/components/ui/Table';
import {
  getCompanies,
  getCompany,
  formatCurrency,
  formatDate,
  formatNumber,
} from '@/lib/api';
import type {
  CompaniesResponse,
  CompanyListItem,
  CompanyResponse,
  TableColumn,
} from '@/lib/types';

function CompaniesContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tickerParam = searchParams.get('ticker')?.toUpperCase() || '';

  const [companies, setCompanies] = useState<CompanyListItem[]>([]);
  const [selected, setSelected] = useState<CompanyResponse | null>(null);
  const [tickerInput, setTickerInput] = useState(tickerParam);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [listError, setListError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  useEffect(() => {
    loadCompanies();
  }, []);

  useEffect(() => {
    setTickerInput(tickerParam);
    if (tickerParam) {
      loadCompanyDetail(tickerParam);
    } else {
      setSelected(null);
      setDetailError(null);
    }
  }, [tickerParam]);

  const loadCompanies = async () => {
    try {
      setLoadingList(true);
      setListError(null);
      const response: CompaniesResponse = await getCompanies({ limit: 50 });
      setCompanies(response.companies);
    } catch (err) {
      console.error('Error loading companies:', err);
      setListError('Failed to load companies. Please try again.');
    } finally {
      setLoadingList(false);
    }
  };

  const loadCompanyDetail = async (ticker: string) => {
    try {
      setLoadingDetail(true);
      setDetailError(null);
      const response = await getCompany(ticker);
      setSelected(response);
    } catch (err) {
      console.error('Error loading company:', err);
      setSelected(null);
      setDetailError(`No company data found for ${ticker}.`);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleSearch = (e?: React.FormEvent) => {
    e?.preventDefault();
    const ticker = tickerInput.trim().toUpperCase();
    if (!ticker) {
      router.push('/companies');
      return;
    }
    router.push(`/companies?ticker=${encodeURIComponent(ticker)}`);
  };

  const companyColumns: TableColumn[] = [
    {
      key: 'ticker',
      label: 'Ticker',
      format: (value) => (
        <button
          type="button"
          onClick={() =>
            router.push(`/companies?ticker=${encodeURIComponent(String(value))}`)
          }
          className="font-semibold text-primary hover:text-primary"
        >
          {String(value)}
        </button>
      ),
    },
    {
      key: 'company_name',
      label: 'Company',
      format: (value) => (value as string) || '—',
    },
    {
      key: 'recent_trades',
      label: 'Recent Trades (90d)',
      format: (value) =>
        value != null ? formatNumber(value as number) : '—',
    },
    {
      key: 'last_trade_date',
      label: 'Last Trade',
      format: (value) => formatDate(value as string),
    },
  ];

  const tradeColumns: TableColumn[] = [
    {
      key: 'trade_date',
      label: 'Date',
      format: (value) => formatDate(value as string),
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
      key: 'value',
      label: 'Value',
      format: (value) =>
        value != null ? formatCurrency(Math.abs(value as number)) : '—',
    },
  ];

  const summary = selected?.company;

  return (
    <AppShell>
        <div className="mb-8">
          <h1 className="text-3xl md:text-[40px] md:leading-[48px] font-bold text-on-surface tracking-tight">Companies</h1>
          <p className="text-secondary mt-2">
            Search by ticker or browse companies with recent insider activity
          </p>
        </div>

        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="flex items-center space-x-2 mb-4">
              <FilterIcon className="h-4 w-4 text-secondary" />
              <span className="text-sm font-medium text-on-surface">Ticker Lookup</span>
            </div>
            <form
              onSubmit={handleSearch}
              className="flex flex-col sm:flex-row gap-3"
            >
              <input
                type="text"
                value={tickerInput}
                onChange={(e) => setTickerInput(e.target.value.toUpperCase())}
                placeholder="Enter ticker (e.g. AAPL)"
                className="flex-1 px-3 py-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary-container focus:border-transparent"
              />
              <button
                type="submit"
                className="inline-flex items-center justify-center px-4 py-2 bg-primary-container text-white text-sm rounded-lg hover:opacity-90 transition-colors"
              >
                <SearchIcon className="h-4 w-4 mr-2" />
                Search
              </button>
            </form>
          </CardContent>
        </Card>

        {(tickerParam || loadingDetail || detailError || selected) && (
          <div className="mb-8">
            {loadingDetail ? (
              <Card>
                <CardContent className="p-12">
                  <div className="flex flex-col items-center">
                    <LoadingSpinner size="lg" />
                    <p className="mt-2 text-sm text-secondary">
                      Loading company details...
                    </p>
                  </div>
                </CardContent>
              </Card>
            ) : detailError ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <BuildingIcon className="h-12 w-12 text-secondary mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-on-surface mb-2">
                    Company Not Found
                  </h3>
                  <p className="text-secondary">{detailError}</p>
                </CardContent>
              </Card>
            ) : summary ? (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="flex items-center">
                        <BuildingIcon className="h-5 w-5 mr-2" />
                        {summary.ticker}
                        {summary.company_name && (
                          <span className="ml-2 text-base font-normal text-secondary">
                            {summary.company_name}
                          </span>
                        )}
                      </span>
                      <Link
                        href={`/trades?ticker=${encodeURIComponent(summary.ticker)}`}
                        className="text-sm font-normal text-primary hover:text-primary"
                      >
                        View all trades →
                      </Link>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-primary">
                          {formatNumber(summary.total_trades)}
                        </div>
                        <div className="text-sm text-secondary">Total Trades</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {formatNumber(summary.recent_activity_30d ?? 0)}
                        </div>
                        <div className="text-sm text-secondary">Activity (30d)</div>
                      </div>
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {formatNumber(summary.recent_activity_90d ?? 0)}
                        </div>
                        <div className="text-sm text-secondary">Activity (90d)</div>
                      </div>
                      <div className="text-center p-4 bg-orange-50 rounded-lg">
                        <div className="text-2xl font-bold text-orange-600">
                          {summary.buy_sell_ratio != null
                            ? `${Math.round(summary.buy_sell_ratio * 100)}%`
                            : '—'}
                        </div>
                        <div className="text-sm text-secondary">Buy/Sell Ratio</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <ActivityIcon className="h-5 w-5 mr-2" />
                      Recent Insider Trades
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    <Table
                      columns={tradeColumns}
                      data={selected?.recent_trades || []}
                      sortable={false}
                    />
                  </CardContent>
                </Card>
              </div>
            ) : null}
          </div>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BuildingIcon className="h-5 w-5 mr-2" />
              Most Active Companies (90 days)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <LoadingState
              loading={loadingList}
              error={listError}
              loadingText="Loading companies..."
            >
              <Table columns={companyColumns} data={companies} sortable={false} />
            </LoadingState>
          </CardContent>
        </Card>
    </AppShell>
  );
}

export default function CompaniesPage() {
  return (
    <Suspense
      fallback={
        <AppShell>
          <div className="flex flex-col items-center justify-center py-24">
            <LoadingSpinner size="lg" />
            <p className="mt-2 text-sm text-secondary">Loading companies...</p>
          </div>
        </AppShell>
      }
    >
      <CompaniesContent />
    </Suspense>
  );
}
