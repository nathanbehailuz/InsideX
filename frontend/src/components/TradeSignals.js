import React, { useState } from 'react';
import './TradeSignals.css';

const TradeSignals = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [dateRange, setDateRange] = useState('7d');

  // Mock data - replace with actual API calls
  const trades = [
    {
      id: 1,
      ticker: 'AAPL',
      cik: '0000320193',
      company: 'Apple Inc.',
      executive: 'Tim Cook',
      role: 'CEO',
      tradeType: 'Sale',
      shares: 10000,
      value: 1750000,
      date: '2024-01-15',
      score: 8.5,
      cluster: 'Tech Leadership',
      modelPerformance: '95.2%',
      prediction: 'Bearish',
      actualReturn: '-2.3%'
    },
    {
      id: 2,
      ticker: 'TSLA',
      cik: '0001318605',
      company: 'Tesla Inc.',
      executive: 'Zachary Kirkhorn',
      role: 'CFO',
      tradeType: 'Purchase',
      shares: 5000,
      value: 875000,
      date: '2024-01-14',
      score: 7.8,
      cluster: 'Finance Leadership',
      modelPerformance: '92.1%',
      prediction: 'Bullish',
      actualReturn: '+4.7%'
    },
    {
      id: 3,
      ticker: 'MSFT',
      cik: '0000789019',
      company: 'Microsoft Corporation',
      executive: 'Satya Nadella',
      role: 'CEO',
      tradeType: 'Sale',
      shares: 15000,
      value: 5250000,
      date: '2024-01-13',
      score: 9.1,
      cluster: 'Tech Leadership',
      modelPerformance: '97.8%',
      prediction: 'Bearish',
      actualReturn: '-1.8%'
    }
  ];

  const filteredTrades = trades.filter(trade => {
    const matchesSearch = 
      trade.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
      trade.cik.includes(searchTerm) ||
      trade.executive.toLowerCase().includes(searchTerm.toLowerCase()) ||
      trade.company.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = selectedFilter === 'all' || 
      (selectedFilter === 'high-score' && trade.score >= 8) ||
      (selectedFilter === 'tech' && trade.cluster === 'Tech Leadership') ||
      (selectedFilter === 'finance' && trade.cluster === 'Finance Leadership');
    
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="trade-signals">
      <div className="container">
        <div className="page-header">
          <h1>Trade Signals Database</h1>
          <p>Real-time executive trading data with AI-powered signal analysis</p>
        </div>

        <div className="search-filters">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search by ticker, CIK, executive, or company..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="filter-controls">
            <select 
              value={selectedFilter} 
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Trades</option>
              <option value="high-score">High Score (8+)</option>
              <option value="tech">Tech Leadership</option>
              <option value="finance">Finance Leadership</option>
            </select>
            
            <select 
              value={dateRange} 
              onChange={(e) => setDateRange(e.target.value)}
              className="filter-select"
            >
              <option value="1d">Last 24h</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>
        </div>

        <div className="trades-table">
          <div className="table-header">
            <div className="header-cell">Company</div>
            <div className="header-cell">Executive</div>
            <div className="header-cell">Trade Details</div>
            <div className="header-cell">Signal Score</div>
            <div className="header-cell">Model Performance</div>
            <div className="header-cell">Prediction vs Actual</div>
          </div>
          
          {filteredTrades.map(trade => (
            <div key={trade.id} className="trade-row">
              <div className="company-cell">
                <div className="ticker">{trade.ticker}</div>
                <div className="company-name">{trade.company}</div>
                <div className="cik">CIK: {trade.cik}</div>
              </div>
              
              <div className="executive-cell">
                <div className="executive-name">{trade.executive}</div>
                <div className="role">{trade.role}</div>
                <div className="cluster">{trade.cluster}</div>
              </div>
              
              <div className="trade-details-cell">
                <div className="trade-type">
                  <span className={`type-badge ${trade.tradeType.toLowerCase()}`}>
                    {trade.tradeType}
                  </span>
                </div>
                <div className="shares">{trade.shares.toLocaleString()} shares</div>
                <div className="value">${trade.value.toLocaleString()}</div>
                <div className="date">{trade.date}</div>
              </div>
              
              <div className="score-cell">
                <div className="score-value">{trade.score}</div>
                <div className="score-bar">
                  <div 
                    className="score-fill" 
                    style={{width: `${(trade.score / 10) * 100}%`}}
                  ></div>
                </div>
                <div className="score-label">Signal Strength</div>
              </div>
              
              <div className="model-cell">
                <div className="model-performance">{trade.modelPerformance}</div>
                <div className="model-label">Accuracy</div>
              </div>
              
              <div className="prediction-cell">
                <div className="prediction">
                  <span className={`prediction-badge ${trade.prediction.toLowerCase()}`}>
                    {trade.prediction}
                  </span>
                </div>
                <div className="actual-return">
                  Actual: <span className={trade.actualReturn.startsWith('+') ? 'positive' : 'negative'}>
                    {trade.actualReturn}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="table-footer">
          <div className="results-count">
            Showing {filteredTrades.length} of {trades.length} trades
          </div>
          <div className="export-actions">
            <button className="export-btn">Export CSV</button>
            <button className="export-btn">Export JSON</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeSignals; 