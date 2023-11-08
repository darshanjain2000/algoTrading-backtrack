from datetime import timedelta
import datetime

from money_money.DALS.brokerHistoricalDAL import BrokerHistoricalDAL
from money_money.utils.constants import CandleIntervals

class DailyScanner:
    def __init__(self, stockSymbolToken):
        self.moving_avg_period = 20
        self.symbolToken = stockSymbolToken

    def get_percentage_change(self):
        yesterday = datetime.date.today() - timedelta(days=1)

        today_date_9_28 = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 28))
        today_date_9_29 = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 29))

        historicalClient = BrokerHistoricalDAL()
        # 9:29 CLOSE - last day CLOSE
        change = historicalClient.get_candle_data(self.symbolToken, CandleIntervals.ONE_MINUTE, today_date_9_28, today_date_9_29)[4] - historicalClient.get_candle_data(self.symbolToken, CandleIntervals.ONE_DAY, datetime.date.today(), yesterday)[4]
        
        # ((9:29 CLOSE - last day CLOSE)/last day CLOSE)*100
        return (change/historicalClient.get_candle_data(self.symbolToken, CandleIntervals.ONE_DAY, datetime.date.today(), yesterday)[4])* 100
    
    def get_mm_factor(self):
        historicalClient = BrokerHistoricalDAL()

        today_date_9_15 = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 15))
        today_date_9_30 = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 30))
        first_15_min_volume = historicalClient.get_candle_data(self.symbolToken, CandleIntervals.FIFTEEN_MINUTE, today_date_9_15, today_date_9_30)[5]
        
        last_date_for_moving_avg = datetime.date.today() - timedelta(days = self.moving_avg_period)
        yesterday = datetime.date.today() - timedelta(days=1)
        last_close_price_list = historicalClient.get_candle_data(self.symbolToken, CandleIntervals.ONE_DAY, last_date_for_moving_avg, yesterday)[4]
        
        return first_15_min_volume/last_close_price_list.mean()
    
    def money_money_value(self):
        return self.get_percentage_change() * self.get_mm_factor()