from datetime import timedelta
import datetime

from money_money.DALS.brokerHistoricalDAL import BrokerHistoricalDAL
from money_money.utils.constants import CandleIntervals

class DailyScanner:
    def __init__(self, invokeTime):
        self.moving_avg_period = 20
        # symbolToken = stockSymbolToken
        self.invokeTime = invokeTime
        self.historicalClient = BrokerHistoricalDAL()

        self.dailyData = {}

    def get_percentage_change(self, symbolToken):
        # yesterday = self.invokeTime - timedelta(days=1)

        today_date_9_28 = datetime.datetime.combine(self.invokeTime, datetime.time(9, 28))
        today_date_9_29 = datetime.datetime.combine(self.invokeTime, datetime.time(9, 29))

        # last_day_close = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_DAY, yesterday, self.invokeTime)[-1][4]
        last_day_close = self.dailyData[symbolToken].last_day_close

        # 9:29 CLOSE - last day CLOSE
        change = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_MINUTE, today_date_9_28, today_date_9_29)[-1][4] - last_day_close
        
        # ((9:29 CLOSE - last day CLOSE)/last day CLOSE)*100
        return (change/last_day_close)* 100
    
    def get_mm_factor(self, symbolToken):
        
        today_date_9_15 = datetime.datetime.combine(self.invokeTime, datetime.time(9, 15))
        today_date_9_30 = datetime.datetime.combine(self.invokeTime, datetime.time(9, 30))
        first_15_min_volume = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.FIFTEEN_MINUTE, today_date_9_15, today_date_9_30)[-1][5]
        
        # last_date_for_moving_avg = datetime.datetime.combine(self.invokeTime - timedelta(days = self.moving_avg_period*2), datetime.time(15, 28)) # *2 to overcome non trading days
        # yesterday = datetime.datetime.combine(self.invokeTime - timedelta(days=1), datetime.time(15, 29))

        # abc = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_DAY, last_date_for_moving_avg, yesterday)[-self.moving_avg_period:] # last self.moving_avg_period days data
        # last_volume_list = [i[5] for i in abc]
        # volume_moving_avg = sum(last_volume_list)/len(last_volume_list)
        volume_moving_avg = self.dailyData[symbolToken].volume_moving_avg

        return first_15_min_volume/volume_moving_avg
    
    def money_money_value(self, symbolToken):
        percentage_change = self.get_percentage_change(symbolToken)
        money_money_factor = self.get_mm_factor(symbolToken)
        # self.historicalClient.log_out()
        return percentage_change * money_money_factor
    
    def calculate_old_details(self, symbolToken):
        try:
            last_date_for_moving_avg = datetime.datetime.combine(self.invokeTime - timedelta(days = self.moving_avg_period*2), datetime.time(15, 28)) # *2 to overcome non trading days
            yesterday = datetime.datetime.combine(self.invokeTime - timedelta(days=1), datetime.time(15, 29))

            abc = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_DAY, last_date_for_moving_avg, yesterday)[-self.moving_avg_period:] # last self.moving_avg_period days data
            last_volume_list = [i[5] for i in abc]

            mm_data = MM_data()
            mm_data.last_day_close = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_DAY, yesterday, self.invokeTime)[-1][4]
            mm_data.volume_moving_avg = sum(last_volume_list)/len(last_volume_list)

            self.dailyData[symbolToken] = mm_data
        except Exception as ex:
            print(ex)
  



class MM_data():
    last_day_close : float
    volume_moving_avg  : float

