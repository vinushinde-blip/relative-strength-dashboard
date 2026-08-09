import yfinance as yf
import pandas as pd
import json

# Define Sector Indices & Top Constituent Stocks (NSE Tickers)
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
BENCHMARK = "^NSEI" # Nifty 50

def get_rs(df, ticker, benchmark_ticker):
    rs_dict = {}
    for days in LOOKBACKS:
        try:
            asset_ret = (df[ticker].iloc[-1] / df[ticker].iloc[-days - 1]) - 1
            bench_ret = (df[benchmark_ticker].iloc[-1] / df[benchmark_ticker].iloc[-days - 1]) - 1
            rs_dict[f"{days}d"] = round((asset_ret - bench_ret) * 100, 2)
        except Exception:
            rs_dict[f"{days}d"] = None
    return rs_dict

# Gather all tickers
all_tickers = [BENCHMARK]
for sec in SECTORS.values():
    all_tickers.append(sec["index"])
    all_tickers.extend(sec["stocks"])

# Download 1-year historical data
data = yf.download(all_tickers, period="1y")["Close"]

result = []

for sec_name, sec_info in SECTORS.items():
    sec_ticker = sec_info["index"]
    sec_rs = get_rs(data, sec_ticker, BENCHMARK)
    
    stocks_data = []
    for st_ticker in sec_info["stocks"]:
        st_rs = get_rs(data, st_ticker, BENCHMARK)
        stocks_data.append({
            "ticker": st_ticker.replace(".NS", ""),
            "rs": st_rs
        })
    
    # Sort stocks by 20-day RS descending
    stocks_data.sort(key=lambda x: x["rs"].get("20d") or -999, reverse=True)
    
    result.append({
        "sector": sec_name,
        "sector_rs": sec_rs,
        "stocks": stocks_data
    })

with open("data.json", "w") as f:
    json.dump(result, f, indent=2)