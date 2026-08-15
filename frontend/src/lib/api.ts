/**
 * API client for OpenSignal backend
 */

import axios from 'axios';
import type {
  CompaniesResponse,
  CompanyResponse,
  DatabaseStats,
  InsidersResponse,
  InsiderResponse,
  TopSignalsResponse,
  TradeQuery,
  TradeResponse,
} from './types';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function getTopSignals(params?: {
  window_days?: number;
  limit?: number;
}): Promise<TopSignalsResponse> {
  const { data } = await api.get<TopSignalsResponse>('/signals/top', {
    params: {
      window_days: params?.window_days ?? 30,
      limit: params?.limit ?? 50,
    },
  });
  return data;
}

export async function getTrades(params?: TradeQuery): Promise<TradeResponse> {
  const { data } = await api.get<TradeResponse>('/trades', {
    params: {
      limit: params?.limit ?? 50,
      offset: params?.offset ?? 0,
      ticker: params?.ticker,
      insider_name: params?.insider_name,
      trade_type: params?.trade_type,
      trade_flag: params?.trade_flag,
      date_from: params?.date_from,
      date_to: params?.date_to,
      min_value_usd: params?.min_value_usd,
    },
  });
  return data;
}

export async function getTradeStats(): Promise<DatabaseStats> {
  const { data } = await api.get<DatabaseStats>('/trades/stats');
  return data;
}

export async function getCompanies(params?: {
  limit?: number;
}): Promise<CompaniesResponse> {
  const { data } = await api.get<CompaniesResponse>('/companies', {
    params: {
      limit: params?.limit ?? 50,
    },
  });
  return data;
}

export async function getCompany(ticker: string): Promise<CompanyResponse> {
  const { data } = await api.get<CompanyResponse>(
    `/companies/${encodeURIComponent(ticker.toUpperCase())}`
  );
  return data;
}

export async function getInsiders(params?: {
  limit?: number;
  sort_by?: 'activity' | 'performance' | 'recent';
}): Promise<InsidersResponse> {
  const { data } = await api.get<InsidersResponse>('/insiders', {
    params: {
      limit: params?.limit ?? 50,
      sort_by: params?.sort_by ?? 'activity',
    },
  });
  return data;
}

export async function getInsider(name: string): Promise<InsiderResponse> {
  const { data } = await api.get<InsiderResponse>(
    `/insiders/${encodeURIComponent(name)}`
  );
  return data;
}

export function formatCurrency(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) {
    return '—';
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) {
    return '—';
  }
  return new Intl.NumberFormat('en-US').format(value);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) {
    return '—';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
}

export function formatPercent(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) {
    return '—';
  }
  return `${(value * 100).toFixed(0)}%`;
}

export default api;
