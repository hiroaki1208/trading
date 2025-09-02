import pandas as pd
import yfinance as yf
import argparse
from datetime import datetime, timedelta
from google.cloud import storage
import os

def get_gcs_config(env):
    """環境に応じたGCS設定を返す"""
    if env == 'dev':
        return {
            'project_id': 'trading-dev-469206',
            'bucket_name': 'takotako-ikaika-trading-a1b2c3-dev'
        }
    elif env == 'prod':
        return {
            'project_id': 'trading-prod-468212',
            'bucket_name': 'takotako-ikaika-trading-a1b2c3-prod'
        }
    else:
        raise ValueError(f"Unsupported environment: {env}")

def upload_to_gcs(df, env, now_str):
    """DataFrameをCSV形式でGCSにアップロード"""
    try:
        config = get_gcs_config(env)
        client = storage.Client(project=config['project_id'])
        bucket = client.bucket(config['bucket_name'])
        
        # ファイル名作成（スペースとコロンを削除）
        timestamp = now_str.replace('-', '').replace(' ', '_').replace(':', '')
        filename = f"price_data/fetch_at_{timestamp}.csv"
        
        # DataFrameをCSV文字列に変換
        csv_string = df.to_csv(index=False)
        
        # GCSにアップロード
        blob = bucket.blob(filename)
        blob.upload_from_string(csv_string, content_type='text/csv')
        
        print(f"Successfully uploaded to GCS: gs://{config['bucket_name']}/{filename}")
        return True
        
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        return False

def reshape_data_price(df, fetch_time_str):
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

    # fetch_time_str を追加
    out['fetch_time_str'] = fetch_time_str
    # 結果: columns = ['date', 'ticker', 'ohlc_type', 'price', 'fetch_time_str']
    return out

def main():
    parser = argparse.ArgumentParser(description='Fetch daily stock data')
    parser.add_argument('--base_date', type=str, default=(datetime.now(datetime.timezone.utc) + timedelta(hours=9)).strftime('%Y-%m-%d'),
                       help='Base date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--ticker', nargs='+', required=False,
                       help='List of ticker symbols')
    parser.add_argument('--env', type=str, default='dev', choices=['dev', 'prod'],
                       help='Environment (dev or prod), default: dev')
    
    args = parser.parse_args()
    
    # Convert string to date
    base_date = datetime.strptime(args.base_date, '%Y-%m-%d').date()

    # 現在の日時（JST）
    # 明示的にUTCで取得した後、9時間加算してJSTに変換
    now_str = (datetime.now(datetime.timezone.utc) + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")

    # Set default ticker if not provided
    if args.ticker is None:
        # Read tickers from CSV file
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(script_dir, 'tickers.csv')
            ticker_df = pd.read_csv(csv_path)
            ticker = ticker_df['ticker'].tolist()
        except Exception as e:
            print(f"Error reading CSV file: {e}. Using default tickers.")
            ticker = ["1655.T", "2413.T", "3283.T"]
    else:
        ticker = args.ticker
    
    start_date = base_date - timedelta(days=2)
    end_date = base_date + timedelta(days=1)  # yfinanceのendは含まれないので1日追加
    data_raw = yf.download(ticker, start=start_date, end=end_date)

    # データの成形
    price_data = reshape_data_price(data_raw, now_str)

    # GCSにアップロード
    success = upload_to_gcs(price_data, args.env, now_str)
    if not success:
        print("Failed to upload to GCS. Exiting.")
        exit(1)
        
    print("Data processing and upload completed successfully.")

if __name__ == "__main__":
    main()
