#!/usr/bin/env python3
"""
Insider Trading Data Analysis Script

This script provides various analysis functions for the insider trading database.
"""

import pandas as pd
from database import InsiderTradingDB
import argparse

def main():
    parser = argparse.ArgumentParser(description='Analyze insider trading data')
    parser.add_argument('--db', default='insider_trading.db', help='Database file path')
    parser.add_argument('--ticker', help='Filter by ticker symbol')
    parser.add_argument('--insider', help='Filter by insider name')
    parser.add_argument('--type', choices=['Buy', 'Sell'], help='Filter by trade type')
    parser.add_argument('--flag', help='Filter by trade flag (M, D, DM, etc.)')
    parser.add_argument('--limit', type=int, default=50, help='Limit number of results')
    parser.add_argument('--top-insiders', action='store_true', help='Show top insiders by activity')
    parser.add_argument('--company-summary', help='Show summary for specific company')
    
    args = parser.parse_args()
    
    # Initialize database
    db = InsiderTradingDB(args.db)
    
    print("="*60)
    print("INSIDER TRADING DATA ANALYSIS")
    print("="*60)
    
    # Show basic stats
    stats = db.get_stats()
    print(f"Database: {args.db}")
    print(f"Total records: {stats['total_records']:,}")
    print(f"Unique companies: {stats['unique_companies']:,}")
    print(f"Unique insiders: {stats['unique_insiders']:,}")
    print(f"Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
    print()
    
    if args.top_insiders:
        print("TOP INSIDERS BY TRADING ACTIVITY:")
        print("-" * 50)
        top_insiders = db.get_top_insiders(10)
        print(top_insiders.to_string(index=False))
        print()
    
    elif args.company_summary:
        print(f"COMPANY SUMMARY FOR {args.company_summary.upper()}:")
        print("-" * 50)
        summary = db.get_company_summary(args.company_summary)
        if not summary.empty:
            print(summary.to_string(index=False))
        else:
            print(f"No data found for ticker: {args.company_summary}")
        print()
    
    else:
        print("RECENT INSIDER TRADES:")
        print("-" * 50)
        trades = db.query_trades(
            ticker=args.ticker,
            insider_name=args.insider,
            trade_type=args.type,
            trade_flag=args.flag,
            limit=args.limit
        )
        
        if not trades.empty:
            # Select key columns for display
            display_cols = ['trade_date', 'ticker', 'company_name', 'insider_name', 
                          'trade_type', 'trade_flag', 'price', 'qty', 'value']
            available_cols = [col for col in display_cols if col in trades.columns]
            
            print(trades[available_cols].to_string(index=False))
        else:
            print("No trades found matching the criteria.")
        print()

if __name__ == "__main__":
    main()
