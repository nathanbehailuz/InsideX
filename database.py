import sqlite3
import pandas as pd
from datetime import datetime
import logging

class InsiderTradingDB:
    def __init__(self, db_path="insider_trading.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the insider trading table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create the insider_trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insider_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_flag TEXT,
                    filing_date TEXT,
                    trade_date TEXT,
                    ticker TEXT,
                    company_name TEXT,
                    insider_name TEXT,
                    title TEXT,
                    trade_type TEXT,
                    price REAL,
                    qty INTEGER,
                    owned INTEGER,
                    delta_own INTEGER,
                    value REAL,
                    performance_1d REAL,
                    performance_1w REAL,
                    performance_1m REAL,
                    performance_6m REAL,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(trade_flag, filing_date, trade_date, ticker, company_name, insider_name, title, trade_type, price, qty, owned, delta_own, value, performance_1d, performance_1w, performance_1m, performance_6m)
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker ON insider_trades(ticker)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_filing_date ON insider_trades(filing_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_date ON insider_trades(trade_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_insider_name ON insider_trades(insider_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_type ON insider_trades(trade_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_flag ON insider_trades(trade_flag)')
            
            conn.commit()
    
    def clean_data(self, df):
        """Clean and standardize the DataFrame data"""
        if df.empty:
            return df
        
        # Create a copy to avoid modifying the original
        df_clean = df.copy()
        
        # Clean column names (remove non-breaking spaces and special characters)
        df_clean.columns = df_clean.columns.str.replace('\xa0', ' ').str.strip()
        
        # Rename columns to match database schema
        column_mapping = {
            'X': 'trade_flag',
            'Filing Date': 'filing_date',
            'Trade Date': 'trade_date', 
            'Ticker': 'ticker',
            'Company Name': 'company_name',
            'Insider Name': 'insider_name',
            'Title': 'title',
            'Trade Type': 'trade_type',
            'Price': 'price',
            'Qty': 'qty',
            'Owned': 'owned',
            'ΔOwn': 'delta_own',
            'Value': 'value',
            '1d': 'performance_1d',
            '1w': 'performance_1w',
            '1m': 'performance_1m',
            '6m': 'performance_6m'
        }
        
        df_clean = df_clean.rename(columns=column_mapping)
        
        # Clean numeric columns
        numeric_columns = ['price', 'qty', 'owned', 'delta_own', 'value', 
                          'performance_1d', 'performance_1w', 'performance_1m', 'performance_6m']
        
        for col in numeric_columns:
            if col in df_clean.columns:
                # Remove commas and convert to numeric
                df_clean[col] = df_clean[col].astype(str).str.replace(',', '').str.replace('$', '')
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Clean text columns
        text_columns = ['trade_flag', 'filing_date', 'trade_date', 'ticker', 'company_name', 
                       'insider_name', 'title', 'trade_type']
        
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
        
        return df_clean
    
    def insert_data(self, df):
        """Insert DataFrame data into the database"""
        if df.empty:
            return 0
        
        df_clean = self.clean_data(df)
        
        with sqlite3.connect(self.db_path) as conn:
            try:
                # Create a temporary table and use INSERT OR IGNORE
                temp_table = 'temp_insider_trades'
                df_clean.to_sql(temp_table, conn, if_exists='replace', index=False)
                
                # Insert from temp table using INSERT OR IGNORE
                # Explicitly specify columns to avoid column count mismatch
                cursor = conn.cursor()
                cursor.execute(f'''
                    INSERT OR IGNORE INTO insider_trades 
                    (trade_flag, filing_date, trade_date, ticker, company_name, insider_name, title, trade_type, price, qty, owned, delta_own, value, performance_1d, performance_1w, performance_1m, performance_6m)
                    SELECT trade_flag, filing_date, trade_date, ticker, company_name, insider_name, title, trade_type, price, qty, owned, delta_own, value, performance_1d, performance_1w, performance_1m, performance_6m
                    FROM {temp_table}
                ''')
                
                # Get the number of actually inserted rows
                inserted_count = cursor.rowcount
                
                # Log duplicates if any
                skipped_count = len(df_clean) - inserted_count
                if skipped_count > 0:
                    logging.info(f"Skipped {skipped_count} duplicate records")
                
                # Drop the temporary table
                cursor.execute(f'DROP TABLE {temp_table}')
                
                conn.commit()
                return inserted_count
            except Exception as e:
                logging.error(f"Error inserting data: {e}")
                conn.rollback()
                return 0
    
    def get_stats(self):
        """Get basic statistics about the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total records
            cursor.execute('SELECT COUNT(*) FROM insider_trades')
            total_records = cursor.fetchone()[0]
            
            # Date range
            cursor.execute('SELECT MIN(filing_date), MAX(filing_date) FROM insider_trades')
            date_range = cursor.fetchone()
            
            # Unique companies
            cursor.execute('SELECT COUNT(DISTINCT ticker) FROM insider_trades')
            unique_companies = cursor.fetchone()[0]
            
            # Unique insiders
            cursor.execute('SELECT COUNT(DISTINCT insider_name) FROM insider_trades')
            unique_insiders = cursor.fetchone()[0]
            
            return {
                'total_records': total_records,
                'date_range': date_range,
                'unique_companies': unique_companies,
                'unique_insiders': unique_insiders
            }
    
    def query_trades(self, ticker=None, insider_name=None, trade_type=None, 
                    trade_flag=None, start_date=None, end_date=None, limit=100):
        """Query insider trades with filters"""
        with sqlite3.connect(self.db_path) as conn:
            query = 'SELECT * FROM insider_trades WHERE 1=1'
            params = []
            
            if ticker:
                query += ' AND ticker = ?'
                params.append(ticker)
            
            if insider_name:
                query += ' AND insider_name LIKE ?'
                params.append(f'%{insider_name}%')
            
            if trade_type:
                query += ' AND trade_type = ?'
                params.append(trade_type)
            
            if trade_flag:
                query += ' AND trade_flag = ?'
                params.append(trade_flag)
            
            if start_date:
                query += ' AND trade_date >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND trade_date <= ?'
                params.append(end_date)
            
            query += ' ORDER BY trade_date DESC LIMIT ?'
            params.append(limit)
            
            return pd.read_sql_query(query, conn, params=params)
    
    def get_top_insiders(self, limit=10):
        """Get insiders with most trading activity"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT insider_name, COUNT(*) as trade_count, 
                       SUM(CASE WHEN trade_type = 'Buy' THEN qty ELSE 0 END) as total_bought,
                       SUM(CASE WHEN trade_type = 'Sell' THEN qty ELSE 0 END) as total_sold
                FROM insider_trades 
                GROUP BY insider_name 
                ORDER BY trade_count DESC 
                LIMIT ?
            '''
            return pd.read_sql_query(query, conn, params=[limit])
    
    def get_company_summary(self, ticker):
        """Get trading summary for a specific company"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN trade_type = 'Buy' THEN qty ELSE 0 END) as total_bought,
                    SUM(CASE WHEN trade_type = 'Sell' THEN qty ELSE 0 END) as total_sold,
                    AVG(CASE WHEN trade_type = 'Buy' THEN price END) as avg_buy_price,
                    AVG(CASE WHEN trade_type = 'Sell' THEN price END) as avg_sell_price
                FROM insider_trades 
                WHERE ticker = ?
            '''
            return pd.read_sql_query(query, conn, params=[ticker])
    
    def check_if_exists(self, row):
        """Check if a specific trade record already exists in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check using all fields from the unique constraint
            query = '''
                SELECT COUNT(*) FROM insider_trades 
                WHERE trade_flag = ? AND filing_date = ? AND trade_date = ? AND ticker = ? 
                AND company_name = ? AND insider_name = ? AND title = ? AND trade_type = ? 
                AND price = ? AND qty = ? AND owned = ? AND delta_own = ? AND value = ? 
                AND performance_1d = ? AND performance_1w = ? AND performance_1m = ? AND performance_6m = ?
            '''
            
            params = (
                str(row.get('X', '')),
                str(row.get('Filing Date', '')),
                str(row.get('Trade Date', '')),
                str(row.get('Ticker', '')),
                str(row.get('Company Name', '')),
                str(row.get('Insider Name', '')),
                str(row.get('Title', '')),
                str(row.get('Trade Type', '')),
                row.get('Price', 0),
                row.get('Qty', 0),
                row.get('Owned', 0),
                row.get('ΔOwn', 0),
                row.get('Value', 0),
                row.get('1d', 0),
                row.get('1w', 0),
                row.get('1m', 0),
                row.get('6m', 0)
            )
            
            cursor.execute(query, params)
            return cursor.fetchone()[0] > 0
