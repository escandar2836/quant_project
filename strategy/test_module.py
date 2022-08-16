import util_modules
from indicators import Indicators
from strategy.basic_strategy import TradeStrategy, Direction

INITIAL_BALANCE = 100000
TEST_ITEM = 'gold'
TEST_TERM = 3600


def get_stop_loss_limit(indicators, position_info):
    atr = indicators.atr()

    stop_loss_price = position_info['entry_price']
    if position_info['direction'] == Direction.BUY:
        stop_loss_price -= 3 * atr
    else:
        stop_loss_price += 3 * atr

    return stop_loss_price


def check_position_entry_price(indicators):
    '''
    가격과 지표를 바탕으로
    진입 가능한 포지션 방향 및 가격을 리턴하는 메소드
    '''
    # TODO: 20일, 300일 이평선 조회
    # TODO: 이를 바탕으로 BUY, SELL 체크
    # TODO: Buy/Sell -> 20일 신고가/신저가 리턴

    moving_average_20 = indicators.moving_average(term=20)
    moving_average_300 = indicators.moving_average(term=300)
    donchian_info = indicators.donchian_band()

    possible_entry_position = Direction.BUY if moving_average_20 >= moving_average_300 else Direction.SELL
    buy_entry_price = donchian_info['high']
    sell_entry_price = donchian_info['low']

    result = {
        'direction': possible_entry_position,
        'entry_price': buy_entry_price if possible_entry_position == Direction.BUY else sell_entry_price
    }
    return result


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

    position_info_list = []

    price_history = util_modules.load_price_history_data(item=item, limit=data_load_term)
    sorted_price_data = sorted(price_history, key=lambda x: x['price_date'])
    indicators = Indicators(price_history=[])

    entry_info = None

    for index, price_data in enumerate(sorted_price_data):
        if entry_info:
            entry_direction = entry_info['direction']
            entry_price = entry_info['entry_price']
            if price_data['high'] >= entry_price >= price_data['low']:
                stop_loss_price = get_stop_loss_limit(indicators=indicators, position_info=entry_info)
                print(f'Date: {price_data["price_date"]} Enter Position. Direction: {entry_direction}, '
                      f'Enter Price: {entry_price}, Stop Loss: {stop_loss_price}')

                position_info = {
                    'direction': entry_direction,
                    'entry_price': entry_price,
                    'stop_loss_price': stop_loss_price,
                    'is_live': True,
                    'profit_and_loss': 0
                }
                position_info_list.append(position_info)

            if position_info_list:
                current_position = position_info_list[-1]
                if current_position['is_live']:
                    if current_position['direction'] == Direction.BUY and \
                            current_position['stop_loss_price'] >= price_data['low']:
                        current_position['is_live'] = False
                        current_position['profit_and_loss'] = current_position['stop_loss_price'] - current_position[
                            'entry_price']
                        INITIAL_BALANCE += current_position['profit_and_loss']
                        print(
                            f'Date: {price_data["price_date"]} '
                            f'Position Out. PnL: {current_position["profit_and_loss"]} '
                            f'Current Balance: {INITIAL_BALANCE}')

                    if current_position['direction'] == Direction.SELL and \
                            current_position['stop_loss_price'] <= price_data['high']:
                        current_position['is_live'] = False
                        current_position['profit_and_loss'] = current_position['entry_price'] - current_position[
                            'stop_loss_price']
                        INITIAL_BALANCE += current_position['profit_and_loss']
                        print(
                            f'Date: {price_data["price_date"]} '
                            f'Position Out. PnL: {current_position["profit_and_loss"]} '
                            f'Current Balance: {INITIAL_BALANCE}')

        indicators.update_price_history(price_data)
        if len(indicators.price_history) < 300:
            continue

        atr = indicators.atr()
        moving_average_20 = indicators.moving_average(term=20)
        moving_average_300 = indicators.moving_average(term=300)
        donchian_info = indicators.donchian_band()

        buy_stop_loss_price = donchian_info['high'] - 3 * atr
        sell_stop_loss_price = donchian_info['low'] - 3 * atr

        entry_info = check_position_entry_price(indicators)

        if position_info_list:
            current_position = position_info_list[-1]
            if not current_position['is_live']:
                continue
            current_stop_loss_price = current_position['stop_loss_price']
            current_position_direction = current_position['direction']

            if current_position_direction == Direction.BUY and current_stop_loss_price < buy_stop_loss_price:
                current_stop_loss_price = buy_stop_loss_price
            if current_position_direction == Direction.SELL and current_stop_loss_price > sell_stop_loss_price:
                current_stop_loss_price = sell_stop_loss_price

    if position_info_list:
        current_position = position_info_list[-1]
        if current_position['direction'] == Direction.BUY:
            current_position['is_live'] = False
            current_position['profit_and_loss'] = sorted_price_data[-1]['close'] - current_position['entry_price']
            INITIAL_BALANCE += current_position['profit_and_loss']
            print(
                f'Date: {sorted_price_data[-1]["price_date"]} '
                f'Position Out. PnL: {current_position["profit_and_loss"]} '
                f'Current Balance: {INITIAL_BALANCE}')

        if current_position['direction'] == Direction.SELL:
            current_position['is_live'] = False
            current_position['profit_and_loss'] = current_position['entry_price'] - sorted_price_data[-1]['close']
            INITIAL_BALANCE += current_position['profit_and_loss']
            print(
                f'Date: {sorted_price_data[-1]["price_date"]} '
                f'Position Out. PnL: {current_position["profit_and_loss"]} '
                f'Current Balance: {INITIAL_BALANCE}')
