import pandas as pd
import yfinance as yf
import argparse
from datetime import datetime, timedelta

def reshape_data_price(df):
    # データの成形
    # 列レベル名が未設定なら分かりやすくしておく
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=['field', 'ticker'])
    df.index.name = 'date'

    # Volume を除外 → 2段の列を stack して縦持ち化 → 列名整形
    out = (
        df.drop(columns='Volume', level=0)              # 'Volume' を除外
        .stack(level=['ticker', 'field'])             # 列の MultiIndex を行方向へ
        .rename_axis(index=['date', 'ticker', 'ohlc_type'])
        .reset_index(name='price')                    # 値列名を price に
    )

    # ohlc_type を小文字に（任意）
    out['ohlc_type'] = out['ohlc_type'].str.lower()

    # 結果: columns = ['date', 'ticker', 'ohlc_type', 'price']
    return out

def main():
    parser = argparse.ArgumentParser(description='Fetch daily stock data')
    parser.add_argument('--base_date', type=str, required=True, 
                       help='Base date in YYYY-MM-DD format')
    parser.add_argument('--ticker', nargs='+', required=False,
                       help='List of ticker symbols')
    
    args = parser.parse_args()
    
    # Convert string to date
    base_date = datetime.strptime(args.base_date, '%Y-%m-%d').date()
    
    # Set default ticker if not provided
    if args.ticker is None:
        # Read tickers from CSV file
        try:
            ticker_df = pd.read_csv('tickers.csv')
            ticker = ticker_df['ticker'].tolist()
        except Exception as e:
            print(f"Error reading CSV file: {e}. Using default tickers.")
            ticker = ["1655.T", "2413.T", "3283.T"]
    else:
        ticker = args.ticker
    
    start_date = base_date - timedelta(days=3)
    data_raw = yf.download(ticker, start=start_date, end=base_date)

    # データの成形
    price_data = reshape_data_price(data_raw)

    print(f"Downloaded data for tickers: {ticker}")
    print(f"Date range: {start_date} to {base_date}")
    print(price_data)

if __name__ == "__main__":
    main()
