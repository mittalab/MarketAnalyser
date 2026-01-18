from analysis.signal_engine import generate_final_signal
from analysis.signal_engine import classify_market_state_futures
from execution.instrument_selector import select_instrument
from execution.position_sizer import size_futures_position
from execution.execution_plan import build_execution_plan
from execution.order_model import Order
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
    print(f"Getting data for {SYMBOL_EQ}")
    derivatives_df = populate_derivatives_data(SYMBOL_EQ)
    futures_df = derivatives_df[0]
    options_df = derivatives_df[1]

    futures_df.set_index("date")
    futures_df.sort_values("date", inplace=True)
    futures_df.reset_index(drop=True, inplace=True)

    print(futures_df)
    # options_df.set_index("date")
    # options_df.sort_values("date", inplace=True)
    # options_df.reset_index(drop=True, inplace=True)

    futures_state = classify_market_state_futures(futures_df)
    print(futures_state)
    # # --------------------------------------------------
    # # 2️⃣ WALK-FORWARD ANALYSIS (NO LEAKAGE)
    # # --------------------------------------------------
    # state_series = {}
    # signal_series = {}
    #
    # option_metrics_series = {}
    # migration_series = {}
    #
    # migration_history = []
    #
    # for i in range(0, len(futures_df)):
    #     window = futures_df.iloc[: i + 1]
    #
    #     # Skip if OI not fully available yet
    #     if window["oi"].isna().any():
    #         continue
    #
    #     result = generate_final_signal(
    #         futures_df_window=window,
    #         option_df_today=options_df,
    #         migration_history=migration_history,
    #         atr=None  # ATR can be plugged in later
    #     )
    #
    #     current_date = window.iloc[-1]["date"]
    #
    #     state_series[current_date] = result["market_state"]
    #     signal_series[current_date] = result["final_signal"]
    #
    #     option_metrics_series[current_date] = result["option_metrics"]
    #     migration_series[current_date] = result["migration_today"]
    #
    # # --------------------------------------------------
    # # 5️⃣ PRINT LATEST ENGINE OUTPUT
    # # --------------------------------------------------
    # last_date = futures_df.iloc[-1]["date"]
    #
    # print("\n========== ENGINE OUTPUT ==========")
    # print("Symbol        :", SYMBOL_EQ)
    # print("Date          :", last_date.date())
    # print("Close Price   :", futures_df.iloc[-1]["close"])
    # print("Open Interest :", futures_df.iloc[-1]["oi"])
    # print("Market State  :", state_series.get(last_date))
    # print("Signal        :", signal_series.get(last_date))
    #
    # if last_date in option_metrics_series:
    #     print("Option Metrics:", option_metrics_series[last_date])

if __name__ == "__main__":
    SYMBOL = "JIOFIN"
    run(SYMBOL)