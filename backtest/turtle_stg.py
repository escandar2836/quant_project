import traceback

import numpy as np
import pandas as pd
from backtesting.lib import SignalStrategy, TrailingStrategy
from talib import SMA, ATR


class TurtleStrategy(SignalStrategy):
    risk = 1
    n1 = 20
    n2 = 55
    last_profit = 0
    closed_trades_count = 0
    skip_breakout = False

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

        for order in self.orders:
            order.cancel()

        # if self.closed_trades and len(self.closed_trades) != self.closed_trades_count:
        #     self.closed_trades_count = len(self.closed_trades)
        #     print(1)
        breakout_price_dict = self.check_breakout_price()

        # position이 있다면
        if self.position:
            # 걸려있던 주문 취소하고 2주 돌파값으로 반대방향 주문
            if self.position.is_long:
                self.sell(size=self.position.size, stop=breakout_price_dict['buy_sl'])
            else:
                self.buy(size=self.position.size, stop=breakout_price_dict['sell_sl'])
        # position이 없다면
        else:
            position_size = self.calculate_position_size()
            if not position_size:
                return
            # 걸려있던 주문 취소하고 4주 돌파값으로 주문
            self.buy(size=position_size, stop=breakout_price_dict['buy_breakout'], sl=breakout_price_dict['buy_breakout'] - 2*self.atr[-1])
            self.sell(size=position_size, stop=breakout_price_dict['sell_breakout'], sl=breakout_price_dict['sell_breakout'] + 2*self.atr[-1])

    def check_breakout_price(self):
        return {
            'buy_breakout': max(self.data.High[max(0, -1 - self.n1):-1]),
            'sell_breakout': min(self.data.Low[max(0, -1 - self.n1):-1]),
            'buy_sl': max(self.data.Low[max(0, -1 - self.n1 // 2):-1]),
            'sell_sl': min(self.data.High[max(0, -1 - self.n1 // 2):-1])
        }

    def calculate_position_size(self):
        # if self.last_profit > 0 and self.skip_breakout:
        #     self.skip_breakout = False
        #     return 0
        position = self.equity * (self.risk / 100) // (2 * self.atr[-1])
        return position
