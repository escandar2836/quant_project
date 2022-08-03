import datetime
from enum import Enum

import util_modules
from indicators import Indicators

logger = util_modules.get_logger()


class Direction(Enum):
    BUY = 1
    SELL = 2


class Position:
    def __init__(self, open_price, stop_loss_price, position):
        self.open_price: float = open_price
        self.open_date: float = datetime.datetime.now().timestamp()
        self.stop_loss_price: float = stop_loss_price
        self.position: Direction = position

    def update_stop_loss_price(self, close_price, stop_loss):
        stop_loss_value = stop_loss * -1 if self.position == Direction.BUY else stop_loss
        new_stop_loss_price = close_price + stop_loss_value

        if self.position == Direction.BUY:
            if new_stop_loss_price > self.stop_loss_price:
                logger.debug(f'stop loss price is updated from {self.stop_loss_price} to {new_stop_loss_price}')
                self.stop_loss_price = new_stop_loss_price
        else:
            if new_stop_loss_price < self.stop_loss_price:
                logger.debug(f'stop loss price is updated from {self.stop_loss_price} to {new_stop_loss_price}')
                self.stop_loss_price = new_stop_loss_price


def _check_availability(possible_position_size):
    if possible_position_size == 0:
        return False
    return True


class TradeStrategy:
    def __init__(self, balance, item, tick_size, tick_value, risk=0.5):
        self.balance = balance
        self.item = item
        self.tick_size = tick_size
        self.tick_value = tick_value
        self.risk = risk
        self.position = None
        self.indicators = None

    def calculate_size(self, atr):
        max_tick_size = atr * 3 / self.tick_size
        stop_loss_per_position = max_tick_size * self.tick_value

        max_risk_amount = self.balance * self.risk
        possible_position_count = max_risk_amount // stop_loss_per_position
        return possible_position_count

    def calculate_stop_loss_price(self):
        if not self.position:
            return

        price_dict = util_modules.load_price_history_data(item=self.item, limit=20)
        close_price = price_dict['close']

        # stop_loss =

        self.position.update_stop_loss_price(close_price=close_price)

    def check_position_entry_price(self, price_history):
        pass

    def daily_update(self):
        price_history = util_modules.load_price_history_data(item=self.item, limit=300)
        self.indicators = Indicators(price_history=price_history)

        latest_close_price = price_history[0]['close']
        atr = self.indicators.atr()

        moving_average_20 = self.indicators.moving_average(term=20)
        moving_average_300 = self.indicators.moving_average(term=300)

        possible_entry_position = Direction.BUY if moving_average_20 >= moving_average_300 else Direction.SELL
