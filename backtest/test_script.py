import os

import pandas as pd

from backtest.basic_stg import BasicSmaStrategy
# from backtest.swing_stg import SwingStrategy
from backtest.donchian_stg import DonchianStrategy
from backtest.turtle_stg import TurtleStrategy
from backtesting import Backtest


def test(item, strategy, dir_path='./'):
    price_df = pd.read_csv(f'../data/{item}.csv', index_col=0)
    price_df.index = pd.to_datetime(price_df.index)
    price_df = price_df.loc[:, ['Close', 'Open', 'High', 'Low', 'Volume']]
    price_df['Volume'] = price_df['Volume'].apply(lambda vol: 0 if vol == '-' else float(vol[:-1]) * 1000)
    for col in ['Close', 'Open', 'High', 'Low']:
        if price_df[col].dtype.name != 'float64':
            price_df[col] = price_df[col].apply(lambda val: float(val.replace(',', '')) if val != '-' else 0)
    price_df = price_df.sort_index(ascending=True)

    price_df = price_df.iloc[365 * 10 * -1:]

    bt = Backtest(price_df, strategy, commission=.002, cash=10**10)

    result = bt.run()
    trades = result._trades

    filename = f'{dir_path}/{item}.html'
    if not os.path.exists(f'{dir_path}'):
        os.makedirs(f'{dir_path}')

    bt.plot(filename=filename)
    print(trades)


if __name__=='__main__':
    # test('nasdaq', DonchianStrategy, dir_path='./turtle_stg_s1')

    # print(1)
    for item in ['bitcoin', 'cocoa', 'coffee', 'corn', 'dow', 'gold', 'nasdaq', 'natural_gas', 'pork', 'wti_oil']:
        test(item, DonchianStrategy, dir_path='./donchian_stg')
