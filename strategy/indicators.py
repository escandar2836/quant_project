from functools import reduce


class Indicators:
    def __init__(self, price_history, item_name):
        self.price_history = price_history
        self.item_name = item_name

    def moving_average(self, index=0, term=20):
        target_price_history = self.price_history[index:index + term]
        closed_price_sum = reduce(lambda acc, history: acc + history['close'], target_price_history, 0)
        return closed_price_sum / term

    def atr(self, index=0, term=20):
        target_price_history = self.price_history[index:index + term]
        volatility_sum = reduce(lambda acc, history: acc + history['high'] - history['low'], target_price_history, 0)
        atr = volatility_sum / term
        return atr

    def obv(self, prev_value, index=0):
        result = prev_value
        if self.price_history[index]['close'] > self.price_history[index + 1]['close']:
            result += self.price_history[index]['vol']
        elif self.price_history[index]['close'] < self.price_history[index + 1]['close']:
            result -= self.price_history[index]['vol']
        return result

    def macd(self, diff_list, short_term=12, long_term=26, index_term=9, index=0):
        short_mv = self.moving_average(term=short_term, index=index)
        long_mv = self.moving_average(term=long_term, index=index)

        diff_value = short_mv - long_mv
        diff_list.append(diff_value)
        if len(diff_list) < index_term:
            return 0

        if len(diff_list) > index_term:
            diff_list = diff_list[-index_term:]

        index_value = sum(diff_list) / index_term
        return index_value

    def rsi(self, term=14, index=0):
        down_list = []
        up_list = []
        for i in range(term):
            diff = self.price_history[index + i]['close'] - self.price_history[index + i + 1]['close']
            if diff > 0:
                up_list.append(diff)
            elif diff < 0:
                down_list.append(diff)
        avg_up = sum(up_list) / len(up_list) if len(up_list) > 0 else 0
        avg_down = sum(down_list) / len(down_list) * -1 if len(down_list) > 0 else 0

        if avg_up == 0:
            rsi_index = 100
        elif avg_down == 0:
            rsi_index = 0
        else:
            rsi_index = 100 - (100 / (1 + avg_up / avg_down))
        return rsi_index
