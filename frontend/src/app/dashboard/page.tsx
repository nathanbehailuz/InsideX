/**
 * Dashboard — Stitch layout with live API data
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  ActivityIcon,
  BuildingIcon,
  UsersIcon,
  TrendingUpIcon,
} from 'lucide-react';

import { AppShell } from '@/components/layout/Navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { SignalBadge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingSpinner';
import {
  getTopSignals,
  getTrades,
  getTradeStats,
  formatCurrency,
  formatNumber,
} from '@/lib/api';
import type { Signal, DatabaseStats } from '@/lib/types';

function isBuy(tradeType?: string | null) {
  const t = (tradeType || '').toLowerCase();
  return t === 'buy' || t.startsWith('p -') || t.includes('purchase');
}

export default function Dashboard() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [trades7d, setTrades7d] = useState(0);
  const [trades30d, setTrades30d] = useState(0);
  const [buyRatio, setBuyRatio] = useState(0);
  const [avgScore, setAvgScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const today = new Date();
      const iso = (d: Date) => d.toISOString().slice(0, 10);
      const from7 = new Date(today);
      from7.setDate(from7.getDate() - 7);
      const from30 = new Date(today);
      from30.setDate(from30.getDate() - 30);

      const [signalsResponse, statsResponse, trades7, trades30] =
        await Promise.all([
          getTopSignals({ window_days: 30, limit: 10 }),
          getTradeStats(),
          getTrades({ date_from: iso(from7), date_to: iso(today), limit: 1000 }),
          getTrades({ date_from: iso(from30), date_to: iso(today), limit: 1000 }),
        ]);

      setSignals(signalsResponse.signals);
      setStats(statsResponse);

      // Prefer API total when available; fall back to returned page length
      const count7 = trades7.total || trades7.trades.length;
      const count30 = trades30.total || trades30.trades.length;
      const buys = trades7.trades.filter((t) => isBuy(t.trade_type)).length;
      const sample = trades7.trades.length || 1;

      setTrades7d(count7);
      setTrades30d(count30);
      setBuyRatio(buys / sample);
      setAvgScore(
        signalsResponse.signals.length > 0
          ? signalsResponse.signals.reduce((s, x) => s + x.score, 0) /
              signalsResponse.signals.length
          : 0
      );
    } catch (err) {
      console.error(err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl md:text-[40px] md:leading-[48px] font-bold text-on-surface tracking-tight">
            Dashboard
          </h1>
          <p className="text-secondary mt-2 text-base">
            Overview of recent activity and top signals.
          </p>
        </div>
        <Link href="/signals" className="os-btn-primary inline-flex items-center justify-center">
          View Signals
        </Link>
      </div>

      <LoadingState loading={loading} error={error} loadingText="Loading dashboard...">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            {
              title: 'Trades (7d)',
              value: formatNumber(trades7d),
              hint: 'From live filings API',
              icon: ActivityIcon,
            },
            {
              title: 'Trades (30d)',
              value: formatNumber(trades30d),
              hint: 'From live filings API',
              icon: TrendingUpIcon,
            },
            {
              title: 'Buy / Sell Mix',
              value: `${Math.round(buyRatio * 100)}% / ${Math.round((1 - buyRatio) * 100)}%`,
              hint: 'Last 7 days sample',
              icon: BuildingIcon,
              bar: buyRatio,
            },
            {
              title: 'Avg Signal Score',
              value:
                signals.length > 0
                  ? `${Math.round(avgScore * 100)}%`
                  : '—',
              hint:
                signals.length > 0
                  ? `${signals.length} live signals`
                  : 'No signals yet',
              icon: UsersIcon,
            },
          ].map((card) => (
            <Card key={card.title} className="!p-5">
              <div className="flex items-start justify-between mb-3">
                <p className="text-xs font-semibold tracking-wider uppercase text-secondary">
                  {card.title}
                </p>
                <card.icon className="h-4 w-4 text-primary-container" />
              </div>
              <p className="text-3xl font-bold text-on-surface">{card.value}</p>
              {'bar' in card && typeof card.bar === 'number' ? (
                <>
                  <div className="mt-3 h-2 rounded-full bg-danger/20 overflow-hidden">
                    <div
                      className="h-full bg-success rounded-full"
                      style={{ width: `${Math.round(card.bar * 100)}%` }}
                    />
                  </div>
                  <p className="mt-2 text-sm text-secondary">{card.hint}</p>
                </>
              ) : (
                <p className="mt-2 text-sm text-secondary">{card.hint}</p>
              )}
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2 !p-0 overflow-hidden">
            <CardHeader className="px-6 pt-6 mb-0 flex items-center justify-between">
              <CardTitle>Top Signals</CardTitle>
              <Link href="/signals" className="text-sm font-semibold text-primary hover:underline">
                View All
              </Link>
            </CardHeader>
            <CardContent className="p-0">
              {signals.length === 0 ? (
                <p className="text-secondary text-center py-12">No signals available yet.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-surface-bright border-y border-border">
                      <tr className="text-left text-xs font-semibold tracking-wider uppercase text-secondary">
                        <th className="px-6 py-3">Ticker</th>
                        <th className="px-6 py-3">Score</th>
                        <th className="px-6 py-3">Reasons</th>
                        <th className="px-6 py-3 text-right">Value</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {signals.slice(0, 8).map((signal, i) => (
                        <tr key={`${signal.ticker}-${i}`} className="hover:bg-surface-bright/80">
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className="h-9 w-9 rounded bg-primary/10 text-primary font-bold flex items-center justify-center text-sm">
                                {signal.ticker.slice(0, 1)}
                              </div>
                              <span className="font-semibold text-on-surface">{signal.ticker}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <SignalBadge confidence={signal.confidence} score={signal.score} />
                          </td>
                          <td className="px-6 py-4 text-on-surface-variant max-w-xs truncate">
                            {signal.reasons.slice(0, 2).join(' · ') || '—'}
                          </td>
                          <td className="px-6 py-4 text-right font-semibold text-on-surface">
                            {formatCurrency(signal.trade_value)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ActivityIcon className="h-5 w-5 text-primary-container" />
                Coverage
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              {stats ? (
                <>
                  {[
                    ['Total Records', formatNumber(stats.total_records)],
                    ['Companies', formatNumber(stats.unique_companies)],
                    ['People', formatNumber(stats.unique_insiders)],
                  ].map(([label, value]) => (
                    <div key={label} className="flex justify-between items-center">
                      <span className="text-secondary">{label}</span>
                      <span className="font-semibold text-on-surface">{value}</span>
                    </div>
                  ))}
                  <div className="pt-2">
                    <span className="text-secondary block mb-2">Date Range</span>
                    <span className="inline-flex px-3 py-1.5 rounded-full bg-surface-container text-xs font-medium text-on-surface">
                      {stats.date_range.min_date || '—'} → {stats.date_range.max_date || '—'}
                    </span>
                  </div>
                </>
              ) : (
                <p className="text-secondary">Loading coverage…</p>
              )}
            </CardContent>
          </Card>
        </div>
      </LoadingState>
    </AppShell>
  );
}
