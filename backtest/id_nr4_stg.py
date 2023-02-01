from backtesting import Strategy
from backtesting.lib import crossover, TrailingStrategy
from talib import SMA, ATR


class IdNr4Strategy(TrailingStrategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 4

    def init(self):
        super().init()
        self.set_trailing_sl(n_atr=3)
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close)

    def next(self):
        super().next()

        if len(self.orders):
            # 체결되지 않은 주문이 있다면 취소하고 새로 주문을 넣는다.
            # sl, tp 주문의 경우에는 contingent로 표시된다.
            for order in self.orders:
                if order.is_contingent:
                    continue
                order.cancel()

        if not self.position:
            position_size = self.calculate_position_size()
            if not position_size:
                return

            # Intraday + minimum atr -> buy if any price go
            # short trades, and buy the asset
            if min(self.atr[self.n1 * -1:]) != self.atr[-1]:
                return

            if self.data.High[-1] <= self.data.High[-2] and self.data.Low[-1] >= self.data.Low[-2]:
                self.buy(size=position_size, stop=self.data.High[-1], sl=min(self.data.Low[-1], self.data.High[-1] * 0.97))
                self.sell(size=position_size, stop=self.data.Low[-1], sl=max(self.data.High[-1], self.data.Low[-1] * 1.03))
                # self.buy(size=position_size, stop=self.data.High[-1])
                # self.sell(size=position_size, stop=self.data.Low[-1])

    def calculate_position_size(self):
        atr = self.atr[-1]
        equity = self.equity
        position = int(equity * 0.05 / (3 * atr))
        return position
