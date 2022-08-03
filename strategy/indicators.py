from functools import reduce


class Indicators:
    def __init__(self, price_history):
        self.price_history = price_history

    def moving_average(self, term=20):
        target_price_history = self.price_history[:term]
        closed_price_sum = reduce(lambda acc, history: acc + history['close'], target_price_history, 0)
        return closed_price_sum / term

    def atr(self, term=20):
        target_price_history = self.price_history[:term]
        volatility_sum = reduce(lambda acc, history: acc + history['high'] - history['low'], target_price_history, 0)
        atr = volatility_sum / term
        return atr
