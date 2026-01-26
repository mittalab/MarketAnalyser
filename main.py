import logging
from datetime import datetime
from config.logging_config import setup_logging
from config.settings import LOGGING_ENABLED

if LOGGING_ENABLED:
    setup_logging(level=logging.DEBUG) # Explicitly setting level here
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # Ensuring the main logger itself is INFO

from analysis.signal_engine import generate_final_signal
from analysis.signal_engine import classify_market_state_futures
from execution.instrument_selector import select_instrument
from execution.position_sizer import size_futures_position
from execution.execution_plan import build_execution_plan
from execution.order_model import Order
from utils.expiry import get_expiry_YYMMM
from data.analysis_derivative_data import populate_derivatives_data


CAPITAL = 1_000_000
RISK_PCT = 0.05

def plan_trade(stock_context, futures_bid, futures_ask):
    # Instrument decision
    spread_pct = (futures_ask - futures_bid) / ((futures_bid + futures_ask)/2)
    instrument_decision = select_instrument(spread_pct)

    # Build execution plan
    plan = build_execution_plan(
        stock_context.signal,
        stock_context.levels,
        stock_context.price_oi["price_change"],  # proxy
        instrument_decision["instrument"]
    )

    if not plan:
        return None

    # Size position (futures example)
    qty = size_futures_position(
        CAPITAL,
        RISK_PCT,
        entry=plan["pullback_entry"]["price"],
        stop=stock_context.levels["support_zone"]
    )

    order = Order(
        symbol=stock_context.symbol,
        side=stock_context.signal,
        quantity=qty,
        price=plan["pullback_entry"]["price"],
        order_type="LIMIT"
    )

    return order

def run(SYMBOL_EQ):

    # --------------------------------------------------
    # 1️⃣ LOAD DERIVATIVES DATA DATA
    # --------------------------------------------------
    logger.info(f"Getting data for {SYMBOL_EQ}")
    today_datetime = datetime.now()
    ExpDate = get_expiry_YYMMM(today_datetime)

    futures_df, options_df = populate_derivatives_data(SYMBOL_EQ, ExpDate)

    futures_df.set_index("date")
    futures_df.sort_values("date", inplace=True)
    futures_df.reset_index(drop=True, inplace=True)

    options_df.set_index("date")
    options_df.sort_values("date", inplace=True)
    options_df.reset_index(drop=True, inplace=True)

    futures_state = classify_market_state_futures(futures_df)
    logger.info(f"FUT market state for stock: {SYMBOL_EQ} is {futures_state}")
    # --------------------------------------------------
    # 2️⃣ WALK-FORWARD ANALYSIS (NO LEAKAGE)
    # --------------------------------------------------
    state_series = {}
    signal_series = {}

    option_metrics_series = {}
    migration_series = {}

    migration_history = []

    for i in range(0, len(futures_df)):
        window = futures_df.iloc[: i + 1]

        # Skip if OI not fully available yet
        if window["oi"].isna().any():
            continue

        # Get the same day options_df as that of future df
        option_df = next(
            (df for df in options_df if (df["date"] == window["date"]).any()),
            None
        )
        if option_df == None:
            continue

        result = generate_final_signal(
            futures_df_window=window,
            option_df_today=option_df,
            migration_history=migration_history,
            atr=None  # TODO: ATR can be plugged in later
        )

        current_date = window.iloc[-1]["date"]

        state_series[current_date] = result["market_state"]
        signal_series[current_date] = result["final_signal"]

        option_metrics_series[current_date] = result["option_metrics"]
        migration_series[current_date] = result["migration_today"]

    # --------------------------------------------------
    # 5️⃣ PRINT LATEST ENGINE OUTPUT
    # --------------------------------------------------
    last_date = futures_df.iloc[-1]["date"]

    logger.info("\n========== ENGINE OUTPUT ==========")
    logger.info("Symbol        :", SYMBOL_EQ)
    logger.info("Date          :", last_date.date())
    logger.info("Close Price   :", futures_df.iloc[-1]["close"])
    logger.info("Open Interest :", futures_df.iloc[-1]["oi"])
    logger.info("Market State  :", state_series.get(last_date))
    logger.info("Signal        :", signal_series.get(last_date))

    if last_date in option_metrics_series:
        logger.info("Option Metrics:", option_metrics_series[last_date])

def get_all_data(file):
    with open(file) as f:
        for line in f:
            line = line.strip()   # removes \n, spaces, tabs
            run(line)


if __name__ == "__main__":
    file = "storage/tmp_stocks.txt"
    get_all_data(file)