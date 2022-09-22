from backtesting import Backtest
from backtesting.test import GOOG

from backtest.sma_crossover_stg import SmaCross
from backtest.basic_stg import SmaCross

bt = Backtest(GOOG, SmaCross, commission=.002)

result = bt.run()
trades = result._trades
bt.plot()
