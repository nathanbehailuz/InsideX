/**
 * API client for InsideX backend
 */

import axios, { AxiosResponse } from 'axios';
import {
  Trade,
  TradeResponse,
  TradeQuery,
  CompanyResponse,
  InsiderResponse,
  TopSignalsResponse,
  SignalResponse,
  SignalRequest,
  DatabaseStats,
} from './types';

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging (development only)
if (process.env.NODE_ENV === 'development') {
  apiClient.interceptors.request.use((config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  });
}

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API functions

/**
 * Health check
 */
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await axios.get(`${API_BASE_URL}/../healthz`);
  return response.data;
};

/**
 * Get trades with filtering and pagination
 */
export const getTrades = async (params: TradeQuery = {}): Promise<TradeResponse> => {
  const response: AxiosResponse<TradeResponse> = await apiClient.get('/trades', { params });
  return response.data;
};

/**
 * Get database statistics
 */
export const getTradeStats = async (): Promise<DatabaseStats> => {
  const response: AxiosResponse<DatabaseStats> = await apiClient.get('/trades/stats');
  return response.data;
};

/**
 * Get company information
 */
export const getCompany = async (ticker: string): Promise<CompanyResponse> => {
  const response: AxiosResponse<CompanyResponse> = await apiClient.get(`/companies/${ticker}`);
  return response.data;
};

/**
 * Get list of companies with recent activity
 */
export const getCompanies = async (limit: number = 50): Promise<{ companies: any[]; total: number }> => {
  const response = await apiClient.get('/companies', { params: { limit } });
  return response.data;
};

/**
 * Get insider information
 */
export const getInsider = async (insiderName: string): Promise<InsiderResponse> => {
  const response: AxiosResponse<InsiderResponse> = await apiClient.get(`/insiders/${encodeURIComponent(insiderName)}`);
  return response.data;
};

/**
 * Get list of insiders
 */
export const getInsiders = async (params: {
  limit?: number;
  sort_by?: 'activity' | 'performance' | 'recent';
} = {}): Promise<{ insiders: any[]; total: number; sorted_by: string }> => {
  const response = await apiClient.get('/insiders', { params });
  return response.data;
};

/**
 * Get top insiders by activity
 */
export const getTopInsiders = async (limit: number = 10): Promise<{ insiders: any[]; total: number }> => {
  const response = await apiClient.get('/insiders/top', { params: { limit } });
  return response.data;
};

/**
 * Get top trading signals
 */
export const getTopSignals = async (params: {
  window_days?: number;
  limit?: number;
} = {}): Promise<TopSignalsResponse> => {
  const response: AxiosResponse<TopSignalsResponse> = await apiClient.get('/signals/top', { params });
  return response.data;
};

/**
 * Score signals for ticker or filings
 */
export const scoreSignals = async (request: SignalRequest): Promise<SignalResponse> => {
  const response: AxiosResponse<SignalResponse> = await apiClient.post('/signals/score', request);
  return response.data;
};

/**
 * Get ML model information
 */
export const getModelInfo = async (): Promise<any> => {
  const response = await apiClient.get('/signals/model-info');
  return response.data;
};

// Utility functions for data formatting

/**
 * Format currency values
 */
export const formatCurrency = (value: number | null | undefined): string => {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  
  if (Math.abs(value) >= 1e9) {
    return `$${(value / 1e9).toFixed(1)}B`;
  } else if (Math.abs(value) >= 1e6) {
    return `$${(value / 1e6).toFixed(1)}M`;
  } else if (Math.abs(value) >= 1e3) {
    return `$${(value / 1e3).toFixed(0)}K`;
  } else {
    return `$${value.toFixed(0)}`;
  }
};

/**
 * Format percentage values
 */
export const formatPercent = (value: number | null | undefined): string => {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  return `${(value * 100).toFixed(1)}%`;
};

/**
 * Format date strings
 */
export const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch {
    return 'N/A';
  }
};

/**
 * Format numbers with commas
 */
export const formatNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  return value.toLocaleString();
};

/**
 * Get confidence color for signals
 */
export const getConfidenceColor = (confidence: string): string => {
  switch (confidence.toLowerCase()) {
    case 'high':
      return 'text-green-600 bg-green-100';
    case 'medium':
      return 'text-yellow-600 bg-yellow-100';
    case 'low':
      return 'text-red-600 bg-red-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
};

/**
 * Get trade type color
 */
export const getTradeTypeColor = (tradeType: string): string => {
  switch (tradeType?.toLowerCase()) {
    case 'buy':
      return 'text-green-600 bg-green-100';
    case 'sell':
      return 'text-red-600 bg-red-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
};

// Error handling
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Transform axios errors to APIErrors
export const handleAPIError = (error: any): APIError => {
  if (axios.isAxiosError(error)) {
    return new APIError(
      error.response?.data?.detail || error.message,
      error.response?.status,
      error.response?.data
    );
  }
  return new APIError(error.message);
};