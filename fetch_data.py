import yfinance as yf
import pandas as pd
import json
import math

# Updated Sector Ticker Mapping (Using NSE index symbols or sector ETF fallbacks)
SECTORS = {
    "NIFTY IT": {
        "index": "^CNXIT",
        "stocks": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"]
    },
    "NIFTY BANK": {
        "index": "^NSEBANK",
        "stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"]
    },
    "NIFTY AUTO": {
        "index": "^CNXAUTO",
        "stocks": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"]
    },
    "NIFTY PHARMA": {
        "index": "^CNXPHARMA",
        "stocks": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "LUPIN.NS"]
    },
    "NIFTY FMCG": {
        "index": "^CNXFMCG",
        "stocks": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "TATACONSUM.NS", "BRITANNIA.NS"]
    }
}

LOOKBACKS = [10, 20, 50, 70, 90, 100, 150, 200]
BENCHMARK = "^NSEI"

all_tickers = [BENCHMARK]
for sec in SECTORS.values():
    all_tickers.append(sec["index"])
    all_tickers.extend(sec["stocks"])

# Download ticker data
try:
    df = yf.download(all_tickers, period="1y", progress=False)["Close"]
except Exception as e:
    print(f"Error downloading data: {e}")
    df = pd.DataFrame()

def calculate_rs(ticker, bench_ticker):
    rs_dict = {}
    
    if df.empty or ticker not in df.columns or bench_ticker not in df.columns:
        return {f"{d}d": 0.0 for d in LOOKBACKS}

    s_series = df[ticker].dropna()
    b_series = df[bench_ticker].dropna()

    for days in LOOKBACKS:
        try:
            if len(s_series) > days and len(b_series) > days:
                asset_ret = (s_series.iloc[-1] / s_series.iloc[-days - 1]) - 1
                bench_ret = (b_series.iloc[-1] / b_series.iloc[-days - 1]) - 1
                val = round((asset_ret - bench_ret) * 100, 2)
                # Ensure NaN or Inf values are converted to 0.0
                rs_dict[f"{days}d"] = 0.0 if math.isnan(val) or math.isinf(val) else val
            else:
                rs_dict[f"{days}d"] = 0.0
        except Exception:
            rs_dict[f"{days}d"] = 0.0
            
    return rs_dict

output_data = []

for sec_name, sec_info in SECTORS.items():
    sec_rs = calculate_rs(sec_info["index"], BENCHMARK)
    stocks_data = []

    for st_ticker in sec_info["stocks"]:
        st_rs = calculate_rs(st_ticker, BENCHMARK)
        stocks_data.append({
            "ticker": st_ticker.replace(".NS", ""),
            "rs": st_rs
        })

    stocks_data.sort(key=lambda x: x["rs"].get("20d", 0), reverse=True)

    output_data.append({
        "sector": sec_name,
        "sector_rs": sec_rs,
        "stocks": stocks_data
    })

# Save JSON file
with open("data.json", "w") as f:
    json.dump(output_data, f, indent=2)

print("data.json generated successfully without NaN!")