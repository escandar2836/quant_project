import datetime
from enum import Enum

import util_modules
from indicators import Indicators
from item_tick_info import ITEM_TICK_INFO

logger = util_modules.get_logger()


class Direction(Enum):
    BUY = 1
    SELL = 2


class Position:
    def __init__(self, open_price, stop_loss_price, position_side):
        '''
        param
        - open_price : 포지션 진입한 가격
        - open_date  : 포지션을 생성한 시간
        - stop_loss_price : 손절 가격
        - position_side   : buy, sell
        '''
        self.open_price: float = open_price
        self.open_date: float = datetime.datetime.now().timestamp()
        self.stop_loss_price: float = stop_loss_price
        self.position_side: Direction = position_side

    def update_stop_loss_price(self, close_price, stop_loss):
        '''
        현재 포지션의 stop_loss_price를 업데이트하는 메소드.

        params
        - close_price : 오늘 종가
        - stop_loss   : 3ATR 같은 값이 들어간다.

        오늘 종가 기준으로 stop_loss를 계산해보고,
        포지션에 따라서 필요 여부를 확인하고 업데이트를 진행한다.
        '''
        stop_loss_value = stop_loss * -1 if self.position_side == Direction.BUY else stop_loss
        new_stop_loss_price = close_price + stop_loss_value

        if self.position_side == Direction.BUY:
            if new_stop_loss_price > self.stop_loss_price:
                logger.debug(f'stop loss price is updated from {self.stop_loss_price} to {new_stop_loss_price}')
                self.stop_loss_price = new_stop_loss_price
        else:
            if new_stop_loss_price < self.stop_loss_price:
                logger.debug(f'stop loss price is updated from {self.stop_loss_price} to {new_stop_loss_price}')
                self.stop_loss_price = new_stop_loss_price


def _check_availability(possible_position_size):
    '''
    possible_position_size 가 0이라면 현재 자금으로 거래가 불가능하다는 결과 리턴
    '''
    if possible_position_size == 0:
        return False
    return True


class TradeStrategy:
    '''
    전략 클래스.

    params
    - balance       : 잔고
    - item          : 거래하는 아이템  ex) gold, nasdaq
    - tick_size     : 틱 사이즈
    - tick_value    : 틱 가격
    - risk          : 한번 거래에서 감당할 리스크 %
    '''

    def __init__(self, balance, item, tick_size, tick_value, risk=0.5):
        self.balance = balance
        self.item = item
        tick_info = ITEM_TICK_INFO[self.item]
        self.tick_size = tick_info.tick_size
        self.tick_value = tick_info.tick_value
        self.risk = risk
        self.position: Position = None
        self.indicators = None

    def calculate_size(self):
        '''
        매수 가능한 거래 개수를 체크하는 함수.
        3 ATR의 가격 만큼을 리스크로 감당할 때, 예상한 최대 리스크 내에서 거래 가능한지 체크한다.
        '''
        atr = self.indicators.atr()
        max_tick_size = atr * 3 / self.tick_size
        stop_loss_per_position = max_tick_size * self.tick_value

        max_risk_amount = self.balance * self.risk
        possible_position_count = max_risk_amount // stop_loss_per_position
        return possible_position_count

    def get_stop_loss_limit(self):
        '''
        각 포지션에 대해서 몇 tick 에 대해서
        손절을 진행할 것인지 계산하는 메소드.
        '''
        # 현재 가격 정보를 기준으로 3ATR 계산
        atr = self.indicators.atr()
        return 3 * atr

    def update_position_stop_loss_price(self):
        '''
        현재 포지션이 있을때,
        종가를 기준으로 stop loss price를 업데이트하는 함수.
        '''
        if not self.position:
            return

        price_dict = util_modules.load_price_history_data(item=self.item, limit=20)
        close_price = price_dict['close']

        stop_loss = self.get_stop_loss_limit()

        self.position.update_stop_loss_price(close_price=close_price, stop_loss=stop_loss)

    def check_position_entry_price(self):
        '''
        가격과 지표를 바탕으로
        진입 가능한 포지션 방향 및 가격을 리턴하는 메소드
        '''

        # TODO: 20일, 300일 이평선 조회
        # TODO: 이를 바탕으로 BUY, SELL 체크
        # TODO: Buy/Sell -> 20일 신고가/신저가 리턴
        price_history = util_modules.load_price_history_data(item=self.item, limit=300)

        moving_average_20 = self.indicators.moving_average(term=20)
        moving_average_300 = self.indicators.moving_average(term=300)

        possible_entry_position = Direction.BUY if moving_average_20 >= moving_average_300 else Direction.SELL
        buy_entry_price = max([price_data['high'] for price_data in price_history[:20]])
        sell_entry_price = max([price_data['low'] for price_data in price_history[:20]])

        result = {
            'direction': possible_entry_position,
            'entry_price': buy_entry_price if possible_entry_position == Direction.BUY else sell_entry_price
        }
        return result

    def daily_update(self):
        '''
        가격 정보가 업데이트 될때마다 이에 맞춰서 지표 및 가격 정보를 업데이트하는 메소드
        기본적으로 csv에 가격이 업데이트 됐다고 가정하고
        이를 로딩해서 사용한다.
        '''
        price_history = util_modules.load_price_history_data(item=self.item, limit=300)
        self.indicators = Indicators(price_history=price_history)

        if self.position:
            self.update_position_stop_loss_price()
        else:
            possible_position_size = self.calculate_size()
            if _check_availability(possible_position_size=possible_position_size):
                entry_info_dict = self.check_position_entry_price()
