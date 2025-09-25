/**
 * TypeScript types for InsideX API
 */

// Base types
export interface Trade {
  id: number;
  trade_flag?: string;
  filing_date?: string;
  trade_date?: string;
  ticker?: string;
  company_name?: string;
  insider_name?: string;
  title?: string;
  trade_type?: string;
  price?: number;
  qty?: number;
  owned?: number;
  delta_own?: number;
  value?: number;
  performance_1d?: number;
  performance_1w?: number;
  performance_1m?: number;
  performance_6m?: number;
  scraped_at?: string;
}

export interface TradeResponse {
  trades: Trade[];
  total: number;
  limit: number;
  offset: number;
}

export interface CompanySummary {
  ticker: string;
  company_name?: string;
  total_trades: number;
  total_bought?: number;
  total_sold?: number;
  avg_buy_price?: number;
  avg_sell_price?: number;
  net_shares?: number;
  buy_sell_ratio?: number;
  recent_activity_30d?: number;
  recent_activity_90d?: number;
}

export interface CompanyResponse {
  company: CompanySummary;
  recent_trades?: Record<string, unknown>[];
}

export interface InsiderSummary {
  insider_name: string;
  total_trades: number;
  total_bought?: number;
  total_sold?: number;
  total_companies?: number;
  avg_trade_value?: number;
  success_rate_1m?: number;
  success_rate_3m?: number;
  success_rate_6m?: number;
  recent_activity_30d?: number;
}

export interface InsiderResponse {
  insider: InsiderSummary;
  recent_trades?: Record<string, unknown>[];
  performance_history?: Record<string, unknown>[];
}

export interface Signal {
  ticker: string;
  score: number;
  confidence: "low" | "medium" | "high";
  reasons: string[];
  trade_date?: string;
  insider_name?: string;
  trade_value?: number;
  expected_return?: number;
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

// API query parameters
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

export interface SignalRequest {
  ticker?: string;
  lookback_days?: number;
  filings?: FilingInput[];
}

export interface FilingInput {
  ticker: string;
  trade_date: string;
  insider_role: string;
  price: number;
  quantity: number;
  ownership_after?: number;
}

// Database stats
export interface DatabaseStats {
  total_records: number;
  date_range: {
    min_date: string;
    max_date: string;
  };
  unique_companies: number;
  unique_insiders: number;
}

// UI-specific types
export interface FilterState {
  ticker: string;
  insider_name: string;
  trade_type: string;
  date_from: string;
  date_to: string;
  min_value_usd: string;
}

export interface DashboardKPIs {
  total_trades_7d: number;
  total_trades_30d: number;
  buy_sell_ratio_7d: number;
  buy_sell_ratio_30d: number;
  top_signals_count: number;
  avg_signal_score: number;
}

export type SortDirection = "asc" | "desc";

export interface TableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  format?: (value: unknown) => string;
}