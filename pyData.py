import pyChart
import BinanceAPI as bnc
import Dates as dates
import Indicators as ta
from datetime import datetime
from datetime import date, timedelta


class pyData:
    def __init__(self, symbol: str, time: str, account: bool = True, length: int = 26):
        self._symbol = symbol
        self._interval_time = time
        self._client, self._twn = bnc.Connection(account)

        self._times, self._opens, self._closes, self._highs, self._lows = [], [], [], [], []
        # step, lo uso para cambiar el último valor de los array candle a tiempo real. Literal cambian casa segundo.
        self._step = True
        # Linear regression
        self._length = length
        self._reg_close = []

    def get_historical_candle(self, start_date):
        return self._client.get_historical_klines(
            self._symbol, self._interval_time, start_date)

    def pre_processing_historical_data(self, candle):

        self._times = [candle[x][0]
                       for x in range(len(candle) - 1)]

        self._opens = [float(candle[x][1])
                       for x in range(len(candle) - 1)]
        self._highs = [float(candle[x][2])
                       for x in range(len(candle) - 1)]
        self._lows = [float(candle[x][3])
                      for x in range(len(candle) - 1)]
        self._closes = [float(candle[x][4])
                        for x in range(len(candle) - 1)]

        self._times = [dates.unix_to_date(x) for x in self._times]

        self._reg_close = ta.LINEARREG(self._closes, self._length)

    def historical_data(self, start_date):
        self._candle = self.get_historical_candle(start_date)
        self.pre_processing_historical_data(self._candle)

    def get_real_time_data(self):

        self._twn.start()
        self._twn.start_kline_socket(
            callback=self.close_ticks,
            symbol=self._symbol,
            interval=self._interval_time)

    def close_ticks(self, msg):
        self._candle_rt = msg['k']
        self._time = self._candle_rt['t']
        self._time = dates.unix_to_date(self._time)
        self._opening = self._candle_rt['o']
        self._close = self._candle_rt['c']
        self._high = self._candle_rt['h']
        self._low = self._candle_rt['l']
        self._is_candle_closed = self._candle_rt['x']

        if self._is_candle_closed:
            self._times[-1] = self._time
            self._opens[-1] = float(self._opening)
            self._closes[-1] = float(self._close)
            self._highs[-1] = float(self._high)
            self._lows[-1] = float(self._low)

            self._reg_close[-1] = ta.STREAM_LINEARREG(
                self._closes, self._length)

            self._step = True
        else:
            if self._step:
                self._times.append(self._time)
                self._opens.append(float(self._opening))
                self._closes.append(float(self._close))
                self._highs.append(float(self._high))
                self._lows.append(float(self._low))

                self._reg_close.append(ta.STREAM_LINEARREG(
                    self._closes, self._length))
                self._step = False
            else:
                self._times[-1] = self._time
                self._opens[-1] = float(self._opening)
                self._closes[-1] = float(self._close)
                self._highs[-1] = float(self._high)
                self._lows[-1] = float(self._low)

                self._reg_close[-1] = ta.STREAM_LINEARREG(
                    self._closes, self._length)

    def candle_values(self):
        return self._times, self._opens, self._highs, self._lows, self._closes

    def regression_values(self):
        return self._reg_close


if __name__ == '__main__':

    start_date = datetime.today() - timedelta(days=1)
    start_date = start_date.strftime('%d %b, %Y')

    symbol = 'MATICUSDT'
    candle_time = '15m'

    length_reg = 26

    pydata = pyData(symbol, candle_time, account=True, length=26)
    pydata.historical_data(start_date)
    pydata.get_real_time_data()

    times, opens, highs, lows, closes = pydata.candle_values()
    reg_close = pydata.regression_values()
    pyChart.plot(symbol, candle_time, 'candle',
                 times, closes, opens, highs, lows)

    #print(len(closes), len(reg_close))
    #pyChart.plot(symbol, candle_time, 'lr', times, closes, reg_close=reg_close)
