/**
 * Trading Signals — Stitch filter bar + table layout
 */

'use client';

import { useState, useEffect } from 'react';
import { SearchIcon, TrendingUpIcon } from 'lucide-react';

import { AppShell } from '@/components/layout/Navigation';
import { Card, CardContent } from '@/components/ui/Card';
import { SignalBadge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingSpinner';
import { getTopSignals, formatCurrency, formatDate } from '@/lib/api';
import type { Signal } from '@/lib/types';
import { cn } from '@/lib/utils';

export default function Signals() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [windowDays, setWindowDays] = useState(30);
  const [confidenceFilter, setConfidenceFilter] = useState<string>('all');
  const [query, setQuery] = useState('');

  useEffect(() => {
    loadSignals();
  }, [windowDays]);

  const loadSignals = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getTopSignals({ window_days: windowDays, limit: 50 });
      setSignals(response.signals);
    } catch (err) {
      console.error(err);
      setError('Failed to load signals. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filteredSignals = signals.filter((signal) => {
    const confOk =
      confidenceFilter === 'all' || signal.confidence === confidenceFilter;
    const q = query.trim().toLowerCase();
    const qOk =
      !q ||
      signal.ticker.toLowerCase().includes(q) ||
      (signal.insider_name || '').toLowerCase().includes(q) ||
      signal.reasons.some((r) => r.toLowerCase().includes(q));
    return confOk && qOk;
  });

  return (
    <AppShell>
      <header className="mb-8">
        <h1 className="text-3xl md:text-[40px] md:leading-[48px] font-bold text-on-surface tracking-tight">
          Trading Signals
        </h1>
        <p className="text-secondary mt-2 text-base">
          AI-ranked by confidence and potential.
        </p>
      </header>

      <Card className="mb-8 !p-4">
        <div className="flex flex-wrap gap-6 items-center justify-between">
          <div className="flex flex-wrap gap-6 items-center">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold tracking-wider uppercase text-secondary">
                Time Window
              </span>
              <select
                value={windowDays}
                onChange={(e) => setWindowDays(Number(e.target.value))}
                className="text-sm bg-background border border-border rounded-md px-3 py-2 text-on-surface focus:outline-none focus:ring-2 focus:ring-primary-container"
              >
                <option value={7}>7 Days</option>
                <option value={30}>30 Days</option>
                <option value={90}>90 Days</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold tracking-wider uppercase text-secondary">
                Confidence
              </span>
              <div className="inline-flex rounded-md border border-border overflow-hidden">
                {['all', 'high', 'medium', 'low'].map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setConfidenceFilter(level)}
                    className={cn(
                      'px-3 py-1.5 text-xs font-semibold tracking-wider uppercase transition-colors',
                      confidenceFilter === level
                        ? 'bg-primary-container text-on-primary'
                        : 'bg-surface text-secondary hover:bg-surface-bright'
                    )}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="relative w-full sm:w-64">
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search signals..."
              className="w-full pl-9 pr-3 py-2 text-sm bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-container"
            />
          </div>
        </div>
      </Card>

      <LoadingState loading={loading} error={error} loadingText="Loading signals...">
        {filteredSignals.length === 0 ? (
          <Card className="!p-12 text-center">
            <TrendingUpIcon className="h-12 w-12 text-secondary mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-on-surface mb-2">No Signals Found</h3>
            <p className="text-secondary text-sm">
              No trading signals match your current filters. Try adjusting the time window or
              confidence level.
            </p>
          </Card>
        ) : (
          <Card className="!p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-surface-bright border-b border-border">
                  <tr className="text-left text-xs font-semibold tracking-wider uppercase text-secondary">
                    <th className="px-6 py-3">Ticker</th>
                    <th className="px-6 py-3">Confidence</th>
                    <th className="px-6 py-3">Signal Drivers</th>
                    <th className="px-6 py-3">Person</th>
                    <th className="px-6 py-3">Trade Date</th>
                    <th className="px-6 py-3 text-right">Value</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredSignals.map((signal, index) => (
                    <tr key={`${signal.ticker}-${index}`} className="hover:bg-surface-bright/70">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="h-9 w-9 rounded bg-primary/10 text-primary font-bold flex items-center justify-center">
                            {signal.ticker.slice(0, 1)}
                          </div>
                          <span className="font-semibold text-on-surface">{signal.ticker}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <SignalBadge confidence={signal.confidence} score={signal.score} />
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1.5 max-w-sm">
                          {signal.reasons.slice(0, 3).map((reason) => (
                            <span
                              key={reason}
                              className="inline-flex px-2 py-0.5 rounded-full bg-surface-container text-xs text-on-surface-variant"
                            >
                              {reason}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-on-surface-variant">
                        {signal.insider_name || '—'}
                      </td>
                      <td className="px-6 py-4 text-on-surface-variant">
                        {formatDate(signal.trade_date)}
                      </td>
                      <td
                        className={cn(
                          'px-6 py-4 text-right font-semibold',
                          (signal.trade_value || 0) >= 0 ? 'text-success' : 'text-danger'
                        )}
                      >
                        {formatCurrency(signal.trade_value)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-6 py-3 border-t border-border flex justify-between text-xs text-secondary">
              <span>
                Showing {filteredSignals.length} of {signals.length} signals
              </span>
              <button type="button" onClick={loadSignals} className="font-semibold text-primary">
                Refresh
              </button>
            </div>
          </Card>
        )}
      </LoadingState>
    </AppShell>
  );
}
