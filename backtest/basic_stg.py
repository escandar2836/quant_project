from backtesting import Strategy
from backtesting.lib import crossover, TrailingStrategy
from talib import SMA, ATR


class BasicSmaStrategy(TrailingStrategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 60
    n2 = 200

    def init(self):
        super().init()
        self.set_trailing_sl(n_atr=3)
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close)

    def next(self):
        super().next()

        if not self.position:
            if len(self.orders):
                # 체결되지 않은 주문이 있다면 취소하고 새로 주문을 넣는다.
                self.orders[0].cancel()

            position_size = self.calculate_position_size()
            # If sma1 crosses above sma2, close any existing
            # short trades, and buy the asset
            if self.sma1[-1] > self.sma2[-1]:
                price = max(self.data.High[-21:])
                if price < self.sma1[-1]:
                    return
                # 여기서 주문은 무조건 limit order. 즉, 주문 가격이 현재 bar의 low보다 높으면 체결된다.
                # 여기선 다른 방식으로 동작해야 하기에 수정이 필요하다.
                self.buy(size=position_size, stop=price)

            # Else, if sma1 crosses below sma2, close any existing
            # long trades, and sell the asset
            elif self.sma2[-1] > self.sma1[-1]:
                price = min(self.data.Low[-21:])
                if price > self.sma1[-1]:
                    return
                # self.sell(size=position_size * -1, limit=price, sl=price + self.atr[-1] * 3)
                self.sell(size=position_size, stop=price)

    def calculate_position_size(self):
        atr = self.atr[-1]
        equity = self.equity
        position = int(equity * 0.05 / (3 * atr))
        return position
