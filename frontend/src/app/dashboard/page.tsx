/**
 * Dashboard page showing overview and key metrics
 */

'use client';

import { useState, useEffect } from 'react';
import { 
  TrendingUpIcon, 
  ActivityIcon, 
  BuildingIcon, 
  UsersIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from 'lucide-react';

import { Navigation } from '@/components/layout/Navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge, SignalBadge } from '@/components/ui/Badge';
import { LoadingState, LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { getTopSignals, getTrades, getTradeStats } from '@/lib/api';
import { formatCurrency, formatNumber } from '@/lib/api';
import type { Signal, DatabaseStats } from '@/lib/types';

interface DashboardStats {
  total_trades_7d: number;
  total_trades_30d: number;
  buy_sell_ratio_7d: number;
  buy_sell_ratio_30d: number;
  top_signals_count: number;
  avg_signal_score: number;
}

export default function Dashboard() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load multiple data sources in parallel
      const [signalsResponse, statsResponse, recentTrades] = await Promise.all([
        getTopSignals({ window_days: 30, limit: 10 }),
        getTradeStats(),
        getTrades({ limit: 100 })
      ]);

      setSignals(signalsResponse.signals);
      setStats(statsResponse);

      // Calculate dashboard stats from trades
      const now = new Date();
      const trades7d = recentTrades.trades.filter(trade => {
        const tradeDate = new Date(trade.trade_date || '');
        const daysDiff = (now.getTime() - tradeDate.getTime()) / (1000 * 60 * 60 * 24);
        return daysDiff <= 7;
      });

      const trades30d = recentTrades.trades.filter(trade => {
        const tradeDate = new Date(trade.trade_date || '');
        const daysDiff = (now.getTime() - tradeDate.getTime()) / (1000 * 60 * 60 * 24);
        return daysDiff <= 30;
      });

      const buys7d = trades7d.filter(t => t.trade_type === 'Buy').length;
      const buys30d = trades30d.filter(t => t.trade_type === 'Buy').length;

      const calculatedStats: DashboardStats = {
        total_trades_7d: trades7d.length,
        total_trades_30d: trades30d.length,
        buy_sell_ratio_7d: trades7d.length > 0 ? buys7d / trades7d.length : 0,
        buy_sell_ratio_30d: trades30d.length > 0 ? buys30d / trades30d.length : 0,
        top_signals_count: signalsResponse.signals.length,
        avg_signal_score: signalsResponse.signals.length > 0 
          ? signalsResponse.signals.reduce((sum, s) => sum + s.score, 0) / signalsResponse.signals.length 
          : 0
      };

      setDashboardStats(calculatedStats);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ 
    title, 
    value, 
    change, 
    icon: Icon, 
    format = 'number' 
  }: {
    title: string;
    value: number | string;
    change?: number;
    icon: any;
    format?: 'number' | 'currency' | 'percent';
  }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">
              {format === 'number' && formatNumber(value as number)}
              {format === 'currency' && formatCurrency(value as number)}
              {format === 'percent' && `${Math.round((value as number) * 100)}%`}
            </p>
            {change !== undefined && (
              <div className="flex items-center mt-1">
                {change > 0 ? (
                  <ArrowUpIcon className="h-4 w-4 text-green-500" />
                ) : (
                  <ArrowDownIcon className="h-4 w-4 text-red-500" />
                )}
                <span className={`text-sm ml-1 ${change > 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {Math.abs(change)}%
                </span>
              </div>
            )}
          </div>
          <div className="p-3 bg-blue-100 rounded-lg">
            <Icon className="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Overview of insider trading signals and market activity
          </p>
        </div>

        <LoadingState loading={loading} error={error} loadingText="Loading dashboard...">
          {/* KPI Cards */}
          {dashboardStats && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Trades (7 days)"
                value={dashboardStats.total_trades_7d}
                icon={ActivityIcon}
              />
              <StatCard
                title="Buy/Sell Ratio"
                value={dashboardStats.buy_sell_ratio_7d}
                format="percent"
                icon={TrendingUpIcon}
              />
              <StatCard
                title="Active Signals"
                value={dashboardStats.top_signals_count}
                icon={BuildingIcon}
              />
              <StatCard
                title="Avg Signal Score"
                value={dashboardStats.avg_signal_score}
                format="percent"
                icon={UsersIcon}
              />
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Top Signals */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUpIcon className="h-5 w-5 mr-2" />
                  Top Trading Signals
                </CardTitle>
              </CardHeader>
              <CardContent>
                {signals.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    No signals available. Check back later.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {signals.slice(0, 5).map((signal, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-semibold text-gray-900">{signal.ticker}</span>
                            <SignalBadge confidence={signal.confidence} />
                          </div>
                          <p className="text-sm text-gray-600">
                            {signal.reasons[0] || 'Insider trading activity'}
                          </p>
                          {signal.insider_name && (
                            <p className="text-xs text-gray-500 mt-1">
                              {signal.insider_name}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-semibold text-gray-900">
                            {Math.round(signal.score * 100)}%
                          </div>
                          {signal.trade_value && (
                            <div className="text-sm text-gray-500">
                              {formatCurrency(signal.trade_value)}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Database Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <ActivityIcon className="h-5 w-5 mr-2" />
                  Database Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                {stats ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {formatNumber(stats.total_records)}
                        </div>
                        <div className="text-sm text-gray-600">Total Trades</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {formatNumber(stats.unique_companies)}
                        </div>
                        <div className="text-sm text-gray-600">Companies</div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {formatNumber(stats.unique_insiders)}
                        </div>
                        <div className="text-sm text-gray-600">Insiders</div>
                      </div>
                      <div className="text-center p-4 bg-orange-50 rounded-lg">
                        <div className="text-sm font-medium text-orange-600">Data Range</div>
                        <div className="text-xs text-gray-600 mt-1">
                          {stats.date_range.min_date} to<br />
                          {stats.date_range.max_date}
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <LoadingSpinner />
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </LoadingState>
      </main>
    </div>
  );
}
