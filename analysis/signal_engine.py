from analysis.market_state import classify_market_state_futures
from analysis.option_buckets import build_option_buckets
from analysis.option_metrics import compute_option_metrics
from analysis.orb_momentum import compute_orb_momentum
from analysis.orb_momentum import apply_orb_momentum
from debug.confidence import compute_confidence
from debug.reason_engine import build_reason
from analysis.option_migration import (
    compute_daily_migration,
    compute_migration_trend
)
from analysis.option_rules import (
    apply_option_rules,
    apply_migration_rules
)


def generate_final_signal(
        SYMBOL,
        futures_df_window,
        option_df_today,
        migration_history,
        orb_history,
        totalStrike=2,
        atr=None
):
    """
    This is the ONLY place where signals are finalized.
    """

    # --------------------------------------------------
    # 1. Structural futures state
    # --------------------------------------------------
    futures_state = classify_market_state_futures(futures_df_window)

    # --------------------------------------------------
    # 2. Raw futures intent (directional bias)
    # --------------------------------------------------
    # Simple example — replace with your own logic if needed
    last_close = futures_df_window.iloc[-1]["close"]
    prev_close = futures_df_window.iloc[-2]["close"]

    if last_close > prev_close:
        futures_signal = "LONG"
    elif last_close < prev_close:
        futures_signal = "SHORT"
    else:
        futures_signal = "HOLD"

    # --------------------------------------------------
    # 3. Option buckets
    # --------------------------------------------------
    spot = futures_df_window.iloc[-1]["spot_close"]

    buckets, atm_strike = build_option_buckets(
        option_df_today,
        spot_price=spot,
        totalStrike=totalStrike,
        atr=atr
    )

    # --------------------------------------------------
    # 4. Option metrics (DPI / USI / ORB)
    # --------------------------------------------------
    option_metrics = compute_option_metrics(buckets)

    # --------------------------------------------------
    # 5. Daily migration snapshot
    # --------------------------------------------------
    migration_today = compute_daily_migration(buckets)
    migration_history.append(migration_today)

    # --------------------------------------------------
    # 6. Migration trend
    # --------------------------------------------------
    migration_trend = compute_migration_trend(migration_history)

    # --------------------------------------------------
    # 7. Apply option risk rules
    # --------------------------------------------------
    signal_after_options = apply_option_rules(
        futures_state=futures_state,
        futures_signal=futures_signal,
        option_metrics=option_metrics
    )

    # --------------------------------------------------
    # 8. Apply ORB momentum
    # --------------------------------------------------
    latest_row = futures_df_window.iloc[-1]
    date = latest_row["date"]          # or epoch → convert once
    orb = option_metrics["ORB"]

    # Append to history
    orb_history.append({
        "date": date,
        "ORB": orb
    })
    # Compute momentum
    orb_momentum = compute_orb_momentum(orb_history)
    signal_after_orb_momentum = apply_orb_momentum(
        market_state=futures_state,
        current_signal=signal_after_options,
        orb=orb,
        orb_momentum=orb_momentum
    )

    # --------------------------------------------------
    # 9. Apply migration rules
    # --------------------------------------------------
    final_signal = apply_migration_rules(
        futures_state=futures_state,
        current_signal=signal_after_orb_momentum,
        migration_trend=migration_trend
    )

    print(
        futures_state,
        futures_signal,
        option_metrics,
        migration_trend,
        final_signal
    )

    close = latest_row["close"]
    oi = latest_row["oi"]
    oi_change = latest_row["oi_change"]
    dpi = option_metrics["DPI"]
    usi = option_metrics["USI"]
    raw_signal = futures_signal
    put_atm_strike = migration_today["put_atm_strike"]
    call_atm_strike = migration_today["call_atm_strike"]

    put_trend = migration_trend["put_trend"]    # -1, 0, +1
    call_trend = migration_trend["call_trend"]  # -1, 0, +1

    decision_snapshot = {
        "date": date,
        "SYMBOL": SYMBOL,
        # Futures
        "futures_close": close,
        "futures_oi": oi,
        "futures_oi_chg": oi_change,
        "market_state": futures_state,
        "raw_signal": raw_signal,

        # Option flow
        "DPI": dpi,
        "USI": usi,
        "ORB": orb,
        "ORB_momentum": orb_momentum,

        # Migration
        "put_atm_strike": put_atm_strike,
        "call_atm_strike": call_atm_strike,
        "put_trend": put_trend,
        "call_trend": call_trend,

        # Final outcome (temporary placeholders)
        "final_signal": final_signal,
        "confidence": 0.0,
        "reason": "",

        # Drill-down
        "option_chain": option_df_today
    }
    decision_snapshot["reason"] = build_reason(decision_snapshot)
    decision_snapshot["confidence"] = compute_confidence(decision_snapshot)


    return {
        "market_state": futures_state,
        "raw_signal": futures_signal,
        "final_signal": final_signal,
        "option_metrics": option_metrics,
        "migration_today": migration_today,
        "migration_trend": migration_trend,
        "decision": decision_snapshot,
    }