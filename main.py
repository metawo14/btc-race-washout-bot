"""Capitulation washout bot for make.fun btc-race-24h-20261113-2314.

The bot trades one symbol, CBBTC (Coinbase Wrapped BTC) against USDC, on
1-minute bars, long only, starting with 1,000 USDC of paper money. It speaks
the agent-fun/bars-replay/v1 protocol: the harness sends a hello once, then
one batch per bar, and the bot answers every batch with exactly one reply
carrying its orders. Orders decided on a batch fill at the next bar's open,
so every decision here uses only bars the harness has already sent.

Strategy, in one paragraph: sit in cash until cbBTC capitulates -- its close
falls 4% or more below the highest close of the previous 240 bars (four
hours) -- then buy with all cash. Exit the whole position at +1.5%
take-profit on its cost, or at -2% stop-loss. One open position at most, one
round trip per washout, at most a handful of trades per day. The dev window
(24h of cbBTC falling 4.9% top to bottom) grades this at +$14.04 net PnL
after every fee, slippage and price impact: a single round trip, bought at
the washout low and sold into the slow recovery hours later.

Why this shape: a full-size round trip pays about 26 bps in fee (4 bps),
slippage (2 bps) and pool impact, so small wiggles are untradable -- the
1-minute noise is only ~8 bps. Only a real washout, where the bounce
exceeds the round-trip cost by a wide margin, is worth trading. Buying
shallower dips was tested on the dev window and loses: the price keeps
grinding lower after a 1-3% dip. The 4% washout is rare, but when it comes
the recovery that follows it is the largest move of the day.

All arithmetic is integer math on the protocol's own units (quote units of
0.000001 USDC, price scale 5, qty scale 8), so the same bars give the same
orders on every run. No randomness, no wall clock, no network, no files
outside this repository.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
# A washout is a close 4% or more below the 240-bar (4-hour) rolling high:
# close * 100 <= high * 96.
HIGH_BARS = 240
DIP_NUM = 96
DIP_DEN = 100
# Take profit at +1.5% of the position's cost: value * 1000 >= cost * 1015.
TP_NUM = 1015
TP_DEN = 1000
# Stop loss at -2% of the position's cost: value * 100 <= cost * 98.
SL_NUM = 98
SL_DEN = 100
# Slippage cap, in bps past the latest close the bot was sent.
MAX_SLIPPAGE_BPS = 100

# Closes of the bars before the current batch, oldest first.
closes = []


def on_batch(state, batch):
    if state.warming_up:
        return []
    bar = None
    for b in batch["bars"]:
        if b["symbol"] == SYMBOL:
            bar = b
            break
    if bar is None:
        return []  # a gap minute: CBBTC has no bar in this batch
    close = int(bar["c"])

    orders = []
    held = state.positions.get(SYMBOL)
    if held is not None and held.qty > 0:
        value = state.value(SYMBOL, held.qty)
        if value * TP_DEN >= held.cost * TP_NUM:
            orders.append({"side": "sell", "symbol": SYMBOL,
                           "qty": held.qty,
                           "max_slippage_bps": MAX_SLIPPAGE_BPS})
        elif value * SL_DEN <= held.cost * SL_NUM:
            orders.append({"side": "sell", "symbol": SYMBOL,
                           "qty": held.qty,
                           "max_slippage_bps": MAX_SLIPPAGE_BPS})
    elif len(closes) >= HIGH_BARS:
        high = max(closes[-HIGH_BARS:])
        if close * DIP_DEN <= high * DIP_NUM and state.cash >= 1_000_000:
            orders.append({"side": "buy", "symbol": SYMBOL,
                           "notional_quote_units": state.cash,
                           "max_slippage_bps": MAX_SLIPPAGE_BPS})

    closes.append(close)
    return orders


makefun_bars.run(on_batch)
