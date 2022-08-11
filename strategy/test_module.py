import util_modules
from indicators import Indicators
from strategy.basic_strategy import TradeStrategy

INITIAL_BALANCE = 100000
TEST_ITEM = 'gold'
TEST_TERM = 3600


def setup_strategy():
    '''
    - balance       : 잔고
    - item          : 거래하는 아이템  ex) gold, nasdaq
    - risk          : 한번 거래에서 감당할 리스크 %
    '''
    price_history = util_modules.load_price_history_data(item=TEST_ITEM, limit=TEST_TERM)
    target_strategy = TradeStrategy(balance=INITIAL_BALANCE, item=TEST_ITEM)


if __name__ == '__main__':
    item = 'gold'
    data_load_term = 3600

    price_history = util_modules.load_price_history_data(item=item, limit=data_load_term)
    sorted_price_data = sorted(price_history, key=lambda x: x['price_date'])
    indicators = Indicators(price_history=[])

    for index, price_data in enumerate(sorted_price_data):
        indicators.update_price_history(price_data)
        if len(indicators.price_history) < 300:
            continue

        atr = indicators.atr()
        moving_average_20 = indicators.moving_average(term=20)
        moving_average_300 = indicators.moving_average(term=300)
        donchian_info = indicators.donchian_band()
