import requests
from bs4 import BeautifulSoup
import time
import random
import csv
from time import sleep
import pandas as pd
import warnings
from database import InsiderTradingDB
import argparse
import logging
import os


URL = "http://openinsider.com"
DB_PATH = 'insider_trading.db'


warnings.filterwarnings("ignore")

# Ensure logs directory exists
if not os.path.exists('./logs'):
    os.makedirs('./logs')

# Clear existing log file and set up logging
log_file = './logs/scrape.log'
if os.path.exists(log_file):
    os.remove(log_file)

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w')

def scraper(s_type):
    columns = ['X', 'Filing\xa0Date', 'Trade\xa0Date', 'Ticker', 'Company\xa0Name', 'Insider\xa0Name', 'Title', 'Trade\xa0Type', 'Price', 'Qty', 'Owned', 'ΔOwn', 'Value', '1d', '1w', '1m', '6m']

    if s_type == 'all':
        os.remove(DB_PATH)

    # Initialize database
    db = InsiderTradingDB(DB_PATH)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })

    try:
        response = session.get(URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        page = 1


        while True:
            sleep(random.uniform(1, 2))
            form_data = {
                'fd': '0',  # All dates for filing date
                'td': '0',  # All dates for trade date  
                'cnt': '1000',  # Max results
                'page': page    # Page number
            }
            
            screener_response = session.get(URL + "/screener", params=form_data)
            screener_response.raise_for_status()
            
            # Parse the results page
            results_soup = BeautifulSoup(screener_response.text, "html.parser")
            
            # Find the results table
            results_table = results_soup.find("table", class_="tinytable")
            
            if results_table:
                # Extract table rows
                try:
                    tables = pd.read_html(results_table.prettify())
                except Exception as e:
                    logging.info(f"Error parsing HTML table on page {page}: {e}")
                    break

                if tables: 
                    page_data = tables[0]

                    if s_type == 'all':
                        # Insert data into database
                        inserted_count = db.insert_data(page_data)
                    
                    elif s_type == 'update':
                        new_records = []
                        for index, row in page_data.iterrows():
                            if not db.check_if_exists(row):
                                new_records.append(row)
                            else:
                                # Stop when we hit existing records
                                break
                        
                        if new_records:
                            new_df = pd.DataFrame(new_records)
                            inserted_count = db.insert_data(new_df)
                        else:
                            break
                    logging.info(f"Inserted {inserted_count} new records from page {page}")
                    page += 1
                    
                else:
                    logging.info("No tables found on this page, stopping...")
                    break
            else:
                logging.info("No more tables found, stopping...")
                break

    except requests.RequestException as e:
        logging.info(f"Request error: {e}")
    except Exception as e:
        logging.info(f"Error: {e}")

    finally:
        # Show database statistics
        stats = db.get_stats()
        logging.info("\n" + "="*50)
        logging.info("SCRAPING COMPLETE - DATABASE STATISTICS")
        logging.info("="*50)
        logging.info(f"Total records in database: {stats['total_records']:,}")
        logging.info(f"Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
        logging.info(f"Unique companies: {stats['unique_companies']:,}")
        logging.info(f"Unique insiders: {stats['unique_insiders']:,}")
        logging.info(f"Database file: {DB_PATH}")
        logging.info("="*50)
        
        session.close()


def main(*args):
    parser = argparse.ArgumentParser(description='Scrape insider trading data')
    parser.add_argument('--s_type', default='all', choices=['all', 'update'], help='all: scarpe all existing data, update: add new data')
    args = parser.parse_args()
    scraper(args.s_type)
    
if __name__ == "__main__":
    main()