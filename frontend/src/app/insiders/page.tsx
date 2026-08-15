/**
 * People page — browse decision-makers and look up trading profiles
 * Route: /insiders (nav label: People)
 */

'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  UsersIcon,
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
  getInsiders,
  getInsider,
  formatCurrency,
  formatDate,
  formatNumber,
  formatPercent,
} from '@/lib/api';
import type {
  InsiderListItem,
  InsiderResponse,
  InsidersResponse,
  TableColumn,
} from '@/lib/types';

type SortBy = 'activity' | 'performance' | 'recent';

function PeopleContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const nameParam = searchParams.get('name') || '';
  const sortParam = (searchParams.get('sort') as SortBy) || 'activity';

  const [people, setPeople] = useState<InsiderListItem[]>([]);
  const [selected, setSelected] = useState<InsiderResponse | null>(null);
  const [nameInput, setNameInput] = useState(nameParam);
  const [sortBy, setSortBy] = useState<SortBy>(
    ['activity', 'performance', 'recent'].includes(sortParam) ? sortParam : 'activity'
  );
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [listError, setListError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  useEffect(() => {
    loadPeople();
  }, [sortBy]);

  useEffect(() => {
    setNameInput(nameParam);
    if (nameParam) {
      loadPersonDetail(nameParam);
    } else {
      setSelected(null);
      setDetailError(null);
    }
  }, [nameParam]);

  const loadPeople = async () => {
    try {
      setLoadingList(true);
      setListError(null);
      const response: InsidersResponse = await getInsiders({
        limit: 50,
        sort_by: sortBy,
      });
      setPeople(response.insiders);
    } catch (err) {
      console.error('Error loading people:', err);
      setListError('Failed to load people. Please try again.');
    } finally {
      setLoadingList(false);
    }
  };

  const loadPersonDetail = async (name: string) => {
    try {
      setLoadingDetail(true);
      setDetailError(null);
      const response = await getInsider(name);
      setSelected(response);
    } catch (err) {
      console.error('Error loading person:', err);
      setSelected(null);
      setDetailError(`No profile found for “${name}”.`);
    } finally {
      setLoadingDetail(false);
    }
  };

  const pushQuery = (next: { name?: string; sort?: SortBy }) => {
    const params = new URLSearchParams();
    const name = next.name !== undefined ? next.name : nameParam;
    const sort = next.sort !== undefined ? next.sort : sortBy;
    if (name) params.set('name', name);
    if (sort && sort !== 'activity') params.set('sort', sort);
    const qs = params.toString();
    router.push(qs ? `/insiders?${qs}` : '/insiders');
  };

  const handleSearch = (e?: React.FormEvent) => {
    e?.preventDefault();
    const name = nameInput.trim();
    pushQuery({ name });
  };

  const handleSortChange = (value: SortBy) => {
    setSortBy(value);
    pushQuery({ sort: value });
  };

  const peopleColumns: TableColumn[] = [
    {
      key: 'insider_name',
      label: 'Name',
      format: (value) => (
        <button
          type="button"
          onClick={() =>
            pushQuery({ name: String(value) })
          }
          className="font-semibold text-primary hover:text-primary text-left"
        >
          {String(value)}
        </button>
      ),
    },
    {
      key: 'total_trades',
      label: 'Trades',
      format: (value) => formatNumber(value as number | null),
    },
    {
      key: 'companies_traded',
      label: 'Companies',
      format: (value) => formatNumber(value as number | null),
    },
    {
      key: 'avg_trade_value',
      label: 'Avg Value',
      format: (value) => formatCurrency(value as number | null),
    },
    {
      key: 'recent_30d',
      label: '30d Activity',
      format: (value) => formatNumber(value as number | null),
    },
    {
      key: 'last_trade_date',
      label: 'Last Trade',
      format: (value) => formatDate(value as string | null),
    },
    {
      key: 'success_rate',
      label: 'Success',
      format: (value) => formatPercent(value as number | null),
    },
  ];

  const recentTradeColumns: TableColumn[] = [
    {
      key: 'trade_date',
      label: 'Date',
      format: (value) => formatDate(value as string | null),
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
      key: 'trade_type',
      label: 'Type',
      format: (value) => <TradeBadge tradeType={String(value ?? '')} />,
    },
    {
      key: 'value',
      label: 'Value',
      format: (value) => formatCurrency(value as number | null),
    },
    {
      key: 'qty',
      label: 'Qty',
      format: (value) => formatNumber(value as number | null),
    },
  ];

  return (
    <AppShell>
        <div className="mb-8">
          <h1 className="text-3xl md:text-[40px] md:leading-[48px] font-bold text-on-surface tracking-tight flex items-center gap-3">
            <UsersIcon className="h-8 w-8 text-primary" />
            People
          </h1>
          <p className="mt-2 text-secondary">
            Influential decision-makers—executives and other filers—ranked by
            disclosure and trading activity.
          </p>
        </div>

        <Card className="mb-6">
          <CardContent className="pt-6">
            <form
              onSubmit={handleSearch}
              className="flex flex-col sm:flex-row gap-4 items-start sm:items-end"
            >
              <div className="flex items-center text-sm font-medium text-on-surface gap-2">
                <FilterIcon className="h-4 w-4" />
                Filters:
              </div>
              <div className="flex-1 w-full">
                <label className="block text-xs text-secondary mb-1">Search by name</label>
                <div className="relative">
                  <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary" />
                  <input
                    type="text"
                    value={nameInput}
                    onChange={(e) => setNameInput(e.target.value)}
                    placeholder="e.g. Musk"
                    className="w-full pl-9 pr-3 py-2 border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary-container focus:border-primary-container"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs text-secondary mb-1">Sort by</label>
                <select
                  value={sortBy}
                  onChange={(e) => handleSortChange(e.target.value as SortBy)}
                  className="px-3 py-2 border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary-container focus:border-primary-container"
                >
                  <option value="activity">Most active</option>
                  <option value="performance">Performance</option>
                  <option value="recent">Most recent</option>
                </select>
              </div>
              <button
                type="submit"
                className="px-4 py-2 bg-primary-container text-white text-sm font-medium rounded-lg hover:opacity-90"
              >
                Search
              </button>
              {nameParam && (
                <button
                  type="button"
                  onClick={() => {
                    setNameInput('');
                    pushQuery({ name: '' });
                  }}
                  className="px-4 py-2 text-sm text-secondary hover:text-on-surface"
                >
                  Clear
                </button>
              )}
            </form>
          </CardContent>
        </Card>

        {nameParam && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Profile</CardTitle>
            </CardHeader>
            <CardContent>
              <LoadingState
                loading={loadingDetail}
                error={detailError}
                loadingText="Loading profile…"
              >
                {selected ? (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-semibold text-on-surface">
                      {selected.insider.insider_name}
                    </h2>
                    <p className="text-sm text-secondary mt-1">
                      {formatNumber(selected.insider.total_trades)} trades across{' '}
                      {formatNumber(selected.insider.total_companies)} companies
                    </p>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-surface-bright rounded-lg p-4">
                      <p className="text-xs text-secondary">Bought</p>
                      <p className="text-lg font-semibold">
                        {formatNumber(selected.insider.total_bought)}
                      </p>
                    </div>
                    <div className="bg-surface-bright rounded-lg p-4">
                      <p className="text-xs text-secondary">Sold</p>
                      <p className="text-lg font-semibold">
                        {formatNumber(selected.insider.total_sold)}
                      </p>
                    </div>
                    <div className="bg-surface-bright rounded-lg p-4">
                      <p className="text-xs text-secondary">Avg Trade Value</p>
                      <p className="text-lg font-semibold">
                        {formatCurrency(selected.insider.avg_trade_value)}
                      </p>
                    </div>
                    <div className="bg-surface-bright rounded-lg p-4">
                      <p className="text-xs text-secondary">30d Activity</p>
                      <p className="text-lg font-semibold">
                        {formatNumber(selected.insider.recent_activity_30d)}
                      </p>
                    </div>
                  </div>
                  {selected.recent_trades && selected.recent_trades.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-on-surface mb-3 flex items-center gap-2">
                        <ActivityIcon className="h-4 w-4" />
                        Recent trades
                      </h3>
                      <Table
                        data={selected.recent_trades}
                        columns={recentTradeColumns}
                      />
                    </div>
                  )}
                </div>
                ) : null}
              </LoadingState>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Active people</CardTitle>
          </CardHeader>
          <CardContent>
            <LoadingState
              loading={loadingList}
              error={listError}
              loadingText="Loading people…"
            >
              {people.length === 0 ? (
              <div className="text-center py-12 text-secondary">
                <UsersIcon className="h-12 w-12 mx-auto mb-3 text-border" />
                <p className="font-medium text-on-surface">No people found</p>
                <p className="text-sm mt-1">Try a different sort or check back after more data loads.</p>
              </div>
              ) : (
              <Table data={people} columns={peopleColumns} sortable={false} />
              )}
            </LoadingState>
          </CardContent>
        </Card>
    </AppShell>
  );
}

export default function PeoplePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-surface-bright flex items-center justify-center">
          <LoadingSpinner />
        </div>
      }
    >
      <PeopleContent />
    </Suspense>
  );
}
