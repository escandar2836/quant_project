from backtesting import Backtest
from backtesting.test import GOOG
import pandas as pd

from backtest.basic_stg import SmaCross


def test(item, strategy):
    price_df = pd.read_csv(f'../data/{item}.csv', index_col=0)
    price_df.index = pd.to_datetime(price_df.index)
    price_df = price_df.loc[:, ['Close', 'Open', 'High', 'Low', 'Volume']]
    price_df['Volume'] = price_df['Volume'].apply(lambda vol: 0 if vol == '-' else float(vol[:-1]) * 1000)
    for col in ['Close', 'Open', 'High', 'Low']:
        price_df[col] = price_df[col].apply(lambda val: float(val.replace(',', '')) if val != '-' else 0)
    price_df = price_df.sort_index(ascending=True)

    bt = Backtest(price_df, strategy, commission=.002)

    result = bt.run()
    trades = result._trades

    filename = f'{strategy}_{item}.html'

    bt.plot(filename=filename)


if __name__=='__main__':
    for item in ['bitcoin', 'cocoa', 'coffee', 'corn', 'dow', 'euro_dollar', 'gold', 'nasdaq', 'natural_gas', 'pork', 'wheat', 'wti_oil']:
        test(item, SmaCross)