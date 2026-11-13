# Capitulation Washout BTC Bot

Entry for make.fun `btc-race-24h-20261113-2314` — race a BTC trading bot live
for 24 hours. Paper money only; nothing is traded for real.

## Strategy

Long-only cbBTC/USDC on 1-minute bars, $1,000 paper start.

- **Entry:** sit in cash until the close falls **4% or more below the highest
  close of the previous 240 bars** (4 hours) — a capitulation washout — then
  buy with all cash.
- **Exit:** sell the whole position at **+1.5% take-profit** on its cost, or
  at **-2% stop-loss**. After a stop-loss, wait 30 bars before re-entering.
- At most one open position; one round trip per washout.

## Why

A full-size round trip pays ~26 bps in fee (4 bps), slippage (2 bps) and
pool price impact, while 1-minute noise is only ~8 bps — so small wiggles
are untradable. Only a real washout, whose recovery exceeds the round-trip
cost by a wide margin, is worth trading. Shallower dips (1–3%) were tested
on the dev window and lose: the price keeps grinding lower after them.

## Dev-window result (graded locally, exact engine replica)

- **Net PnL +$14.04** after every fee, slippage and impact (gate: > $0)
- 1 round trip: buy bar 403 at $68,238.76, sell bar 658 at $69,252.45
- Max drawdown 1.1% (guardrail: 25%)

Validation: the local backtest was checked against the kit's own grader on
the house `ema-cross` baseline — official grade-local dev PnL
-$109.380836 vs backtest -$109.38 — and the bot was driven through the real
`agent-fun/bars-replay/v1` protocol on the dev window, reproducing the
backtest's trades exactly.

## Files

- `main.py` — the bot (Python 3.13, standard library only)
- `vendor/makefun_bars.py` — byte-identical copy of the kit's Python SDK shim
- `LICENSE` — MIT
