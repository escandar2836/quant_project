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

    def obv(self, prev_value):
        result = prev_value
        if self.price_history[0].close > self.price_history[1].close:
            result += self.price_history[0].volume
        elif self.price_history[0].close < self.price_history[1].close:
            result -= self.price_history[0].volume
        return result

    def macd(self, diff_list, short_term, long_term, index_term):
        short_mv = self.moving_average(term=short_term)
        long_mv = self.moving_average(term=long_term)

        diff_value = short_mv - long_mv
        diff_list = diff_list[1:]
        diff_list.append(diff_value)

        index_value = sum(diff_list[-index_term:]) / index_term
        return index_value

    def rsi(self, term):
        down_list = []
        up_list = []
        for i in range(term):
            diff = self.price_history[i] > self.price_history[i + 1]
            if diff > 0:
                up_list.append(diff)
            elif diff < 0:
                down_list.append(diff)
        avg_up = sum(up_list) / len(up_list)
        avg_down = sum(down_list) / len(down_list)

        rsi_index = 100 - (100 / (1 + avg_up / avg_down))
        return rsi_index
   