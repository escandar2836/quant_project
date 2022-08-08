import csv
import logging
import re

from strategy.indicators import Indicators

BASE_PATH = "/Users/mingihong/Documents/GitHub/quant_project/data"
ITEM_LIST = [
    "cocoa",
    "bitcoin",
    "coffee",
    "corn",
    "dow",
    "euro_dollar",
    "gold",
    "nasdaq",
    "natural_gas",
    "pork",
    "wheat",
    "wti_oil",
]


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # file_handler = logging.FileHandler('my.log')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    return logger


logger = get_logger()


def _update_date(target_date):
    result = target_date[:]
    result = re.sub("['년','월']", "-", result)
    result = re.sub("['일',' ']", "", result)
    return result


def _update_price(target_price):
    result = target_price.replace(",", "")
    return float(result)


def _parse_history_data(data):
    if len(data) == 7:
        # ['날짜', '종가', '오픈', '고가', '저가', '거래량', '변동 %']
        result = {
            "price_date": _update_date(data[0]),
            "close": _update_price(data[1]),
            "open": _update_price(data[2]),
            "high": _update_price(data[3]),
            "low": _update_price(data[4]),
            "vol": data[5],
            "volatility": data[6],
        }
    else:
        result = {
            "price_date": _update_date(data[0]),
            "close": _update_price(data[1]),
            "open": _update_price(data[2]),
            "high": _update_price(data[3]),
            "low": _update_price(data[4]),
            "volatility": data[5],
        }
    return result


def open_file(path):
    with open(path, "r", encoding="utf-8") as f:
        rdr = csv.reader(f)
        for line in rdr:
            print(line)


def write_file(path, contents):
    with open(path, "a", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(contents)


def load_price_history_data(item, base_date=None, limit=20):
    """
    아이템의 가격 정보를 가져오는 함수.
    base_date 기준으로 과거 데이터를 조회한다.

    input:
        item: 조회하는 아이템
        base_date: 조회 기준일
        limit: 조회할 데이터 개수

    output:
        [
            {'price_date': '2022-07-15', 'close': 1703.6,
             'open': 1708.2, 'high': 1714.2, 'low': 1696.6,
             'vol': '-', 'volatility': '-0.13%'},
        ]
    """
    result_list = []
    append_flag = False

    if item not in ITEM_LIST:
        logger.error("item not exist")
        return

    path = f"{BASE_PATH}/{item}.csv"
    with open(path, "r", encoding="utf-8") as f:
        rdr = csv.reader(f)
        ind = 0
        for line in rdr:
            # ind += 1
            price_date = _update_date(line[0])
            if not base_date:
                base_date = price_date
            if base_date >= price_date:
                append_flag = True
            if append_flag:
                history_data = _parse_history_data(line)
                result_list.append(history_data)
                ind += 1

            if ind == limit:
                break

    return result_list


def write_transaction_log(data):
    """
    거래 로그를 작성하는 함수.
    거래한 아이템과 현재 거래 상태, 진입 청산가 등등의 정보를 관리.

    input:
        data = {
            'item': 'gold',
            'status': 'open',
            'open': 12,
            'close': 15,
            'start': '2022-07-01',
            'end': '2022-07-01',
        }
    """
    item = data["item"]
    status = data["status"]
    open_price = data["open"]
    close_price = data["close"]
    open_time = data["start"]
    end_time = data["end"]
    profit_and_lose = close_price - open_price
    # TODO: Tick size, Tick Value는 따로 설정으로 관리해주자.
    tick_size = 0.5
    tick_value = 25

    contents = [
        status,
        open_time,
        end_time,
        open_price,
        close_price,
        profit_and_lose,
        tick_size,
        tick_value,
    ]

    transaction_log_file = f"{BASE_PATH}/{item}_transaction_log.csv"
    write_file(path=transaction_log_file, contents=contents)


def update_indicator_data(item_name, start_date=None, size=20):
    price_history = load_price_history_data(item=item_name, base_date=start_date, limit=size)
    indicator = Indicators(item_name=item_name, price_history=price_history)

    # RSI 업데이트
    rsi_path = f"{BASE_PATH}/{item_name}_rsi.csv"
    for index in range(size - 1 - 14):
        rsi_index = indicator.rsi(index=index)
        write_file(path=rsi_path, contents=[price_history[index]['price_date'], rsi_index])

    # atr 업데이트
    atr_path = f"{BASE_PATH}/{item_name}_atr.csv"
    for index in range(size - 1 - 20):
        atr_index = indicator.atr(index=index)
        write_file(path=atr_path, contents=[price_history[index]['price_date'], atr_index])

    # moving average 업데이트
    mvg_path_50 = f"{BASE_PATH}/{item_name}_moving_average_50.csv"
    for index in range(size - 1 - 50):
        mvg = indicator.moving_average(index=index, term=50)
        write_file(path=mvg_path_50, contents=[price_history[index]['price_date'], mvg])

    # moving average 업데이트
    mvg_path_200 = f"{BASE_PATH}/{item_name}_moving_average_200.csv"
    for index in range(size - 1 - 200):
        mvg = indicator.moving_average(index=index, term=200)
        write_file(path=mvg_path_200, contents=[price_history[index]['price_date'], mvg])

    # obv 업데이트
    # obv_path = f"{BASE_PATH}/{item_name}_obv.csv"
    # prev_value = 0
    # for index in range(size - 2, 1, -1):
    #     prev_value = indicator.obv(index=index, prev_value=prev_value)
    #     write_file(path=obv_path, contents=[price_history[index]['price_date'], prev_value])

    # macd 업데이트
    macd_path = f"{BASE_PATH}/{item_name}_macd.csv"
    macd_list = []
    for index in range(size - 26, 0, -1):
        macd_index = indicator.macd(diff_list=macd_list, index=index)
        write_file(path=macd_path, contents=[price_history[index]['price_date'], macd_index])


if __name__ == "__main__":
    rr = _update_date("2022년 7월 3일")
    print(rr)

    res = load_price_history_data("gold", "2022-05-15", 5)
    print(res)

    res = load_price_history_data("gold", limit=5)
    print(res)

    test_data = {
        "item": "gold",
        "status": "open",
        "open": 12,
        "close": 15,
        "start": "2022-07-01",
        "end": "2022-07-01",
    }

    write_transaction_log(test_data)
