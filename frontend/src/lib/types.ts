/**
 * Shared TypeScript types matching backend/app/models/
 */

import type { ReactNode } from 'react';

export type SignalConfidence = 'low' | 'medium' | 'high';
export type SortDirection = 'asc' | 'desc';

export interface Signal {
  ticker: string;
  score: number;
  confidence: SignalConfidence;
  reasons: string[];
  trade_date?: string | null;
  insider_name?: string | null;
  trade_value?: number | null;
  expected_return?: number | null;
}

export interface TopSignalsResponse {
  generated_at: string;
  window_days: number;
  signals: Signal[];
  total: number;
}

export interface SignalResponse {
  generated_at: string;
  signals: Signal[];
  metadata?: Record<string, unknown>;
}

export interface Trade {
  id: number;
  trade_flag?: string | null;
  filing_date?: string | null;
  trade_date?: string | null;
  ticker?: string | null;
  company_name?: string | null;
  insider_name?: string | null;
  title?: string | null;
  trade_type?: string | null;
  price?: number | null;
  qty?: number | null;
  owned?: number | null;
  delta_own?: number | null;
  value?: number | null;
  performance_1d?: number | null;
  performance_1w?: number | null;
  performance_1m?: number | null;
  performance_6m?: number | null;
  scraped_at?: string | null;
}

export interface TradeQuery {
  ticker?: string;
  insider_name?: string;
  trade_type?: string;
  trade_flag?: string;
  date_from?: string;
  date_to?: string;
  min_value_usd?: number;
  limit?: number;
  offset?: number;
}

export interface TradeResponse {
  trades: Trade[];
  total: number;
  limit: number;
  offset: number;
}

export interface DatabaseStats {
  total_records: number;
  date_range: {
    min_date: string | null;
    max_date: string | null;
  };
  unique_companies: number;
  unique_insiders: number;
}

export interface Company {
  ticker: string;
  company_name?: string | null;
}

export interface CompanyListItem {
  ticker: string;
  company_name?: string | null;
  recent_trades?: number | null;
  total_bought?: number | null;
  total_sold?: number | null;
  last_trade_date?: string | null;
}

export interface CompaniesResponse {
  companies: CompanyListItem[];
  total: number;
}

export interface CompanySummary {
  ticker: string;
  company_name?: string | null;
  total_trades: number;
  total_bought?: number | null;
  total_sold?: number | null;
  avg_buy_price?: number | null;
  avg_sell_price?: number | null;
  net_shares?: number | null;
  buy_sell_ratio?: number | null;
  recent_activity_30d?: number | null;
  recent_activity_90d?: number | null;
}

export interface CompanyResponse {
  company: CompanySummary;
  recent_trades?: Trade[];
}

export interface Insider {
  insider_name: string;
  title?: string | null;
}

export interface InsiderListItem {
  insider_name: string;
  total_trades?: number | null;
  total_bought?: number | null;
  total_sold?: number | null;
  companies_traded?: number | null;
  avg_trade_value?: number | null;
  avg_performance?: number | null;
  last_trade_date?: string | null;
  recent_30d?: number | null;
  success_rate?: number | null;
}

export interface InsidersResponse {
  insiders: InsiderListItem[];
  total: number;
  sorted_by?: string;
}

export interface InsiderSummary {
  insider_name: string;
  total_trades: number;
  total_bought?: number | null;
  total_sold?: number | null;
  total_companies?: number | null;
  avg_trade_value?: number | null;
  success_rate_1m?: number | null;
  success_rate_3m?: number | null;
  success_rate_6m?: number | null;
  recent_activity_30d?: number | null;
}

export interface InsiderResponse {
  insider: InsiderSummary;
  recent_trades?: Trade[];
  performance_history?: unknown[];
}

export interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  format?: (value: unknown) => ReactNode;
}
