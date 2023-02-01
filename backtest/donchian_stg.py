import traceback

import numpy as np
import pandas as pd
from backtesting.lib import SignalStrategy, TrailingStrategy
from talib import SMA, ATR


class DonchianStrategy(SignalStrategy):
    risk = 1
    n1 = 20
    # n2 = 55
    checked_closed_trade_idx = 0
    skip_breakout = False
    breakout_skipped = False

    def init(self):
        # In init() and in next() it is important to call the
        # super method to properly initialize the parent classes
        super().init()

        # Precompute the atr
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close)

        signal = [0] * len(self.data.High)
        self.set_signal(entry_size=signal)

        # Set trailing stop-loss to 2x ATR using
        # the method provided by `TrailingStrategy`
        # self.set_trailing_sl(2)

    def next(self):
        super().next()

        if len(self.data.High) < self.n1:
            return

        breakout_price_dict = self.check_breakout_price()

        for order in self.orders:
            if order.is_contingent:
                continue
            order.cancel()

        position_size = self.calculate_position_size()
        if not position_size:
            return

        if not self.position:
            self.buy(size=position_size, stop=breakout_price_dict['buy_breakout'])
            self.sell(size=position_size, stop=breakout_price_dict['sell_breakout'])
        else:
            if self.trades[0].is_long:
                self.trades[0].sl = breakout_price_dict['sell_breakout']
            else:
                self.trades[0].sl = breakout_price_dict['buy_breakout']

    def check_breakout_price(self):
        return {
            'buy_breakout': max(self.data.High[-1 - self.n1:-1]),
            'sell_breakout': min(self.data.Low[-1 - self.n1:-1]),
        }

    def calculate_position_size(self):
        position = self.equity * (self.risk / 100) // (2 * self.atr[-1])
        return position
