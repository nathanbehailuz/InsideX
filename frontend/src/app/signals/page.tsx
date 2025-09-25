/**
 * Signals page showing AI-generated trading signals
 */

'use client';

import { useState, useEffect } from 'react';
import { TrendingUpIcon, FilterIcon } from 'lucide-react';

import { Navigation } from '@/components/layout/Navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { SignalBadge, TradeBadge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingSpinner';
import { getTopSignals } from '@/lib/api';
import { formatCurrency, formatDate } from '@/lib/api';
import type { Signal } from '@/lib/types';

export default function Signals() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [windowDays, setWindowDays] = useState(30);
  const [confidenceFilter, setConfidenceFilter] = useState<string>('all');

  useEffect(() => {
    loadSignals();
  }, [windowDays]);

  const loadSignals = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await getTopSignals({
        window_days: windowDays,
        limit: 50
      });

      setSignals(response.signals);
    } catch (err) {
      console.error('Error loading signals:', err);
      setError('Failed to load signals. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filteredSignals = signals.filter(signal => 
    confidenceFilter === 'all' || signal.confidence === confidenceFilter
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Trading Signals</h1>
          <p className="text-gray-600 mt-2">
            AI-powered insider trading signals ranked by confidence and potential
          </p>
        </div>

        {/* Filters */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
              <div className="flex items-center space-x-2">
                <FilterIcon className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Filters:</span>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Time Window</label>
                  <select
                    value={windowDays}
                    onChange={(e) => setWindowDays(Number(e.target.value))}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value={7}>Last 7 days</option>
                    <option value={30}>Last 30 days</option>
                    <option value={90}>Last 90 days</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Confidence</label>
                  <select
                    value={confidenceFilter}
                    onChange={(e) => setConfidenceFilter(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="all">All Confidence</option>
                    <option value="high">High Only</option>
                    <option value="medium">Medium Only</option>
                    <option value="low">Low Only</option>
                  </select>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <LoadingState loading={loading} error={error} loadingText="Loading signals...">
          {/* Signals List */}
          <div className="space-y-6">
            {filteredSignals.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <TrendingUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Signals Found</h3>
                  <p className="text-gray-500">
                    No trading signals match your current filters. Try adjusting the time window or confidence level.
                  </p>
                </CardContent>
              </Card>
            ) : (
              filteredSignals.map((signal, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between">
                      {/* Signal Info */}
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-3">
                          <h3 className="text-xl font-bold text-gray-900">{signal.ticker}</h3>
                          <SignalBadge 
                            confidence={signal.confidence} 
                            score={signal.score}
                          />
                          {signal.expected_return && (
                            <span className="text-sm text-green-600 bg-green-100 px-2 py-1 rounded-full">
                              +{Math.round(signal.expected_return * 100)}% expected
                            </span>
                          )}
                        </div>

                        <div className="space-y-2 mb-4">
                          {signal.reasons.map((reason, reasonIndex) => (
                            <div key={reasonIndex} className="flex items-start space-x-2">
                              <div className="w-1 h-1 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                              <p className="text-sm text-gray-600">{reason}</p>
                            </div>
                          ))}
                        </div>

                        <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                          {signal.insider_name && (
                            <span>Insider: {signal.insider_name}</span>
                          )}
                          {signal.trade_date && (
                            <span>Trade Date: {formatDate(signal.trade_date)}</span>
                          )}
                          {signal.trade_value && (
                            <span>Value: {formatCurrency(signal.trade_value)}</span>
                          )}
                        </div>
                      </div>

                      {/* Score */}
                      <div className="mt-4 sm:mt-0 sm:ml-6 flex-shrink-0">
                        <div className="text-center">
                          <div className="text-3xl font-bold text-gray-900">
                            {Math.round(signal.score * 100)}%
                          </div>
                          <div className="text-xs text-gray-500">Confidence</div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>

          {/* Load More */}
          {filteredSignals.length > 0 && (
            <div className="text-center mt-8">
              <button
                onClick={loadSignals}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Refresh Signals
              </button>
            </div>
          )}
        </LoadingState>
      </main>
    </div>
  );
}