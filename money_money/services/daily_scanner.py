from datetime import timedelta
import datetime

from money_money.DALS.brokerHistoricalDAL import BrokerHistoricalDAL
from money_money.utils.constants import CandleIntervals

class DailyScanner:
    def __init__(self, stockSymbolToken, invokeTime):
        self.moving_avg_period = 20
        self.symbolToken = stockSymbolToken
        self.invokeTime = invokeTime
        self.historicalClient = BrokerHistoricalDAL()

    def get_percentage_change(self):
        yesterday = self.invokeTime - timedelta(days=1)

        today_date_9_28 = datetime.datetime.combine(self.invokeTime, datetime.time(9, 28))
        today_date_9_29 = datetime.datetime.combine(self.invokeTime, datetime.time(9, 29))

        
        # 9:29 CLOSE - last day CLOSE
        change = self.historicalClient.get_candle_data(self.symbolToken, CandleIntervals.ONE_MINUTE, today_date_9_28, today_date_9_29)[-1][4] - self.historicalClient.get_candle_data(self.symbolToken, CandleIntervals.ONE_DAY, yesterday, self.invokeTime)[-1][4]
        
        # ((9:29 CLOSE - last day CLOSE)/last day CLOSE)*100
        return (change/self.historicalClient.get_candle_data(self.symbolToken, CandleIntervals.ONE_DAY, yesterday, self.invokeTime)[-1][4])* 100
    
    def get_mm_factor(self):
        
        today_date_9_15 = datetime.datetime.combine(self.invokeTime, datetime.time(9, 15))
        today_date_9_30 = datetime.datetime.combine(self.invokeTime, datetime.time(9, 30))
        first_15_min_volume = self.historicalClient.get_candle_data(self.symbolToken, CandleIntervals.FIFTEEN_MINUTE, today_date_9_15, today_date_9_30)[-1][5]
        
        last_date_for_moving_avg = datetime.datetime.combine(self.invokeTime - timedelta(days = self.moving_avg_period*2), datetime.time(15, 28)) # *2 to overcome non trading days
        yesterday = datetime.datetime.combine(self.invokeTime - timedelta(days=1), datetime.time(15, 29))

        abc = self.historicalClient.get_candle_data(self.symbolToken, CandleIntervals.ONE_DAY, last_date_for_moving_avg, yesterday)[-self.moving_avg_period:] # last self.moving_avg_period days data
        last_volume_price_list = [i[5] for i in abc]
        
        return first_15_min_volume/(sum(last_volume_price_list)/len(last_volume_price_list))
    
    def money_money_value(self):
        percentage_change = self.get_percentage_change()
        money_money_factor = self.get_mm_factor()
        # self.historicalClient.log_out()
        return percentage_change * money_money_factor