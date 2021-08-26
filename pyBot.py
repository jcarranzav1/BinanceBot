import pyChart
import BinanceAPI as bnc
import Dates as dates
import Indicators as ta
from datetime import datetime
from datetime import date, timedelta


class pyBot:
    def __init__(self, symbol: str, time: str, account: bool = True, length: int = 26):
        self._symbol = symbol
        self._interval_time = time
        self._client, self._twn = bnc.Connection(account)
        self._times, self._opens, self._closes, self._highs, self._lows = [], [], [], [], []

        # Linear regression
        self._length = length
        self._reg_close = []

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

            self._times.append(self._time)
            self._opens.append(float(self._opening))
            self._closes.append(float(self._close))
            self._highs.append(float(self._high))
            self._lows.append(float(self._low))
            self._reg_close.append(ta.STREAM_LINEARREG(
                self._closes, self._length))

            #print(self._reg_close[len(self._reg_close)- self._length::])

    def get_historical_candle(self, start_date):
        return self._client.get_historical_klines(
            self._symbol, self._interval_time, start_date)

    def get_real_time_data(self):
        self._twn.start()
        self._twn.start_kline_socket(
            callback=self.close_ticks,
            symbol=self._symbol,
            interval=self._interval_time)
    
    def create_test_order(self, price, quantity, side:str):
        #side : 'SELL' or 'BUY'
        self._client.create_test_order(
            symbol = self._symbol,
            side = side,
            type = 'LIMIT',
            timeInForce  = 'GTC',
            price = price,
            quantity = quantity
        )
    
    def create_order(self, price, quantity, side:str):
        #side : 'SELL' or 'BUY'
        self._client.create_order(
            symbol = self._symbol,
            side = side,
            type = 'LIMIT',
            timeInForce  = 'GTC',
            price = price,
            quantity = quantity
        )

    def candle_values(self):
        return self._times, self._opens, self._highs, self._lows, self._closes

    def regression_values(self):
        return self._reg_close

    ##INNER CLASS
    class Trailing_Stop():
        def __init__(self, price, type, stopsize):
            self.price = price
            self.type = type
            self.stopsize = stopsize
            self.stoploss = self.initialize_stop()
        
        def initialize_stop(self):

            if self.type == "BUY":
                return (self.price + self.stopsize)

            elif self.type == "SELL":
                return (self.price - self.stopsize)

        def update_stop(self):
            if self.type == "SELL":
                if (self.price - self.stopsize) > self.stoploss:
                    self.stoploss = self.price - self.stopsize    
                    print("New high observed: Updating stop loss to %.8f" % self.stoploss)
                
                elif self.price <= self.stoploss:
                    #create_test_order()
                    print("Sell triggered | Price: %.8f | Stop loss: %.8f" % (self._price, self.stoploss))
            
            elif self.type == "BUY":

                if (self.price + self.stopsize) < self.stoploss:
                    self.stoploss = self.price + self.stopsize
                    print("New low observed: Updating stop loss to %.8f" % self.stoploss)

                elif self.price >= self.stoploss:
                    #create_test_order()
                    print("Buy triggered | Price: %.8f | Stop loss: %.8f" % (self.price, self.stoploss))


if __name__ == '__main__':

    start_date = datetime.today() - timedelta(days=1)
    start_date = start_date.strftime('%d %b, %Y')

    symbol = 'DOGEUSDT'
    candle_time = '5m'

    length_reg = 26

    pybot = pyBot(symbol, candle_time, account=True, length=26)
    pybot.historical_data(start_date)
    pybot.get_real_time_data()
    times, opens, highs, lows, closes = pybot.candle_values()
    reg_close = pybot.regression_values()
    print(reg_close[len(reg_close)- length_reg::])
