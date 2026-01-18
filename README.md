# Institutional Futures & Options Market State Engine

This project implements an **institution-grade futures and options analysis engine**
designed to identify **big money behavior**, **risk transfer**, and **high-quality
directional trade opportunities** in Indian equity markets.

The system is explicitly designed for:
- Short-term to swing trading (3–7 days)
- Futures as the primary instrument
- Options as a risk and confirmation layer
- Low trade frequency, high signal quality

---

## 1. CORE PHILOSOPHY

This system is based on one guiding principle:

> Futures define the market regime.  
> Options define where and how risk is being transferred.

We explicitly separate:
- **Market State (slow, structural)**
- **Signals (fast, tactical)**

The engine avoids reacting to 1-day noise and instead focuses on
**consistent behavior over time**, exactly how professional desks operate.

---

## 2. DATA MODELS (AUTHORITATIVE)

### 2.1 Futures Data (`futures_df`)

Granularity: 1 row per trading day (EOD)

Columns:
- `date`   : trading date
- `open`   : futures open
- `high`   : futures high
- `low`    : futures low
- `close`  : futures close
- `volume` : traded volume
- `oi`     : futures open interest (daily snapshot)

Notes:
- Historical OI is built by **your own daily snapshots**
- FYERS provides only the current OI, not historical

---

### 2.2 Options Data (`option_df`)

Granularity: 1 row per strike, per option type, per expiry, per day

Columns:
- `date`
- `expiry`
- `strike`
- `type` (`CE` / `PE`)
- `oi`
- `oi_change`
- `volume`
- `bid`
- `ask`

Notes:
- Options are analyzed as **daily snapshots**
- Historical behavior is inferred by storing snapshots over time

---

## 3. MARKET STATE (FUTURES-BASED)

Market state is **structural** and uses a rolling lookback (default: 7 days).

Daily price–OI relationships are classified as:
- Price ↑ + OI ↑ → Accumulation
- Price ↑ + OI ↓ → Risk transfer
- Price ↓ + OI ↑ → Short build
- Price ↓ + OI ↓ → Unwind

The dominant behavior over the lookback defines the regime:
- `ACCUMULATION`
- `DISTRIBUTION`
- `RISK_TRANSFER`
- `NEUTRAL`

**Market state is slow to change and never flips on a single day.**

---

## 4. OPTIONS ANALYSIS (CONFIRMATION & RISK)

Options never define the regime.
They **confirm, delay, or invalidate** futures-based decisions.

### 4.1 Option Buckets

Strikes are bucketed dynamically using a relevance zone:
- Preferred: `spot ± 1 × ATR`
- Fallback: ATM ± 2 strikes

Buckets:
- PUT_ITM / PUT_ATM / PUT_OTM
- CALL_ITM / CALL_ATM / CALL_OTM

Illiquid strikes are filtered out.

---

### 4.2 Core Option Metrics

#### DPI — Downside Protection Index
Measures new downside protection:
DPI = PUT_ATM_oi_change + PUT_ITM_oi_change

r
Copy code

#### USI — Upside Supply Index
Measures upside supply (call writing):
USI = CALL_ATM_oi_change + CALL_OTM_oi_change

shell
Copy code

#### ORB — Option Risk Balance
Net risk bias:
ORB = DPI − USI

yaml
Copy code

Interpretation:
- ORB > 0 → risk absorbed (supportive)
- ORB < 0 → risk transferred (fragile / bearish)

---

## 5. BUCKET MIGRATION (KEY EDGE)

Static OI shows **where risk is**.
Migration shows **where risk is moving**.

Tracked daily:
- PUT_ATM weighted strike (support)
- CALL_ATM weighted strike (resistance)

Trends over lookback:
- PUT_ATM rising → accumulation strengthening
- CALL_ATM falling → distribution tightening

Migration modifies:
- HOLD vs LONG
- Exit timing
- Signal confidence

---

## 6. SIGNAL GENERATION (FINAL LOGIC)

Signals are produced in stages:

1. Futures define structural market state
2. Futures generate a raw directional intent
3. Options (DPI / USI / ORB) validate or delay
4. Bucket migration confirms consistency
5. Final signal is emitted:
  - LONG
  - SHORT
  - HOLD

**HOLD is a deliberate, intelligent state — not indecision.**

---

## 7. WHY THIS SYSTEM IS DIFFERENT

- No blind indicators
- No fixed strike assumptions
- No 1-day regime flips
- Explicit risk hierarchy
- Fully explainable decisions

This is how professional derivative desks actually reason about markets.

---

## 8. NEXT EXTENSIONS

- ORB trend normalization
- Expiry-aware futures stitching
- Interactive dashboards
- Portfolio-level risk aggregation
- Live paper trading

---

## FINAL NOTE

This system is designed to trade **less**, but trade **with institutions**,
not against them.

If a trade does not pass all layers, the correct action is HOLD.