from data.fyers_client import get_fyers_client
from data.fetch_eod import fetch_ohlc
from data.fetch_options import fetch_option_chain
from data.storage import save_csv
from analysis.futures_oi import analyze_futures_oi
from analysis.market_state import classify_market_state
from analysis.option_oi import analyze_option_oi
from analysis.levels import define_levels
from analysis.signals import generate_signal
from models.stock_context import StockContext
import pandas as pd

SYMBOL = "NSE:M&M-EQ"

def run():
    fyers = get_fyers_client()

    # Spot EOD
    candles = fetch_ohlc(fyers, SYMBOL, days=30)
    df_candles = pd.DataFrame(candles, columns=["ts","o","h","l","c","v"])
    save_csv(df_candles, "storage/spot", f"{SYMBOL}.csv")

    # Futures OI (placeholder until API hooked)
    futures_oi_series = [1000000 + i*10000 for i in range(len(df_candles))]
    price_oi = analyze_futures_oi(candles, futures_oi_series)

    market_state = classify_market_state(price_oi)

    # Options
    option_df = fetch_option_chain(fyers, SYMBOL)
    save_csv(option_df, "storage/options", f"{SYMBOL}.csv")

    option_zones = analyze_option_oi(option_df)
    levels = define_levels(df_candles["c"].iloc[-1], option_zones)

    signal = generate_signal(market_state, price_oi, option_zones)

    stock = StockContext(SYMBOL)
    stock.update(market_state, price_oi, option_zones, levels, signal)

    print("STOCK:", SYMBOL)
    print("STATE:", stock.market_state)
    print("SIGNAL:", stock.signal)
    print("OPTION ZONES:", stock.option_zones)
    print("LEVELS:", stock.levels)

if __name__ == "__main__":
    run()
