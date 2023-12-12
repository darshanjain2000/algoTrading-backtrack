from datetime import timedelta
import datetime
import time
from money_money.DALS.brokerHistoricalDAL import BrokerHistoricalDAL
from money_money.DALS.brokerHistoricalDAL2 import BrokerHistoricalDAL2
from money_money.DALS.brokerHistoricalDAL3 import BrokerHistoricalDAL3
from money_money.utils.constants import CandleIntervals

class DailyScanner:
    def __init__(self, invokeTime):
        self.moving_avg_period = 20
        # symbolToken = stockSymbolToken
        self.invokeDate = invokeTime

        self.historicalClient = BrokerHistoricalDAL()
        time.sleep(1)
        self.historicalClient2 = BrokerHistoricalDAL2()
        time.sleep(1)
        self.historicalClient3 = BrokerHistoricalDAL3()

        self.dailyData = {}

    def get_percentage_change(self, symbolToken, clientCode):
        # yesterday = self.invokeTime - timedelta(days=1)

        today_date_9_28 = datetime.datetime.combine(self.invokeDate, datetime.time(9, 28))
        today_date_9_29 = datetime.datetime.combine(self.invokeDate, datetime.time(9, 29))

        # last_day_close = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_DAY, yesterday, self.invokeTime)[-1][4]
        last_day_close = self.dailyData[symbolToken].last_day_close

        # 9:29 CLOSE - last day CLOSE
        if(clientCode == 1):
            change = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_MINUTE, today_date_9_28, today_date_9_29)[-1][4] - last_day_close
        elif(clientCode == 2):
            change = self.historicalClient2.get_candle_data(symbolToken, CandleIntervals.ONE_MINUTE, today_date_9_28, today_date_9_29)[-1][4] - last_day_close
        elif(clientCode == 3):
            change = self.historicalClient3.get_candle_data(symbolToken, CandleIntervals.ONE_MINUTE, today_date_9_28, today_date_9_29)[-1][4] - last_day_close
        
        # ((9:29 CLOSE - last day CLOSE)/last day CLOSE)*100
        return (change/last_day_close)* 100
    
    def get_mm_factor(self, symbolToken, clientCode):
        
        today_date_9_15 = datetime.datetime.combine(self.invokeDate, datetime.time(9, 15))
        today_date_9_30 = datetime.datetime.combine(self.invokeDate, datetime.time(9, 30))
        if(clientCode == 1):
            first_15_min_volume = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.FIFTEEN_MINUTE, today_date_9_15, today_date_9_30)[-1][5]
        elif(clientCode == 2):
            first_15_min_volume = self.historicalClient2.get_candle_data(symbolToken, CandleIntervals.FIFTEEN_MINUTE, today_date_9_15, today_date_9_30)[-1][5]
        elif(clientCode == 3):
            first_15_min_volume = self.historicalClient3.get_candle_data(symbolToken, CandleIntervals.FIFTEEN_MINUTE, today_date_9_15, today_date_9_30)[-1][5]
        
        # last_date_for_moving_avg = datetime.datetime.combine(self.invokeTime - timedelta(days = self.moving_avg_period*2), datetime.time(15, 28)) # *2 to overcome non trading days
        # yesterday = datetime.datetime.combine(self.invokeTime - timedelta(days=1), datetime.time(15, 29))

        # abc = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_DAY, last_date_for_moving_avg, yesterday)[-self.moving_avg_period:] # last self.moving_avg_period days data
        # last_volume_list = [i[5] for i in abc]
        # volume_moving_avg = sum(last_volume_list)/len(last_volume_list)
        volume_moving_avg = self.dailyData[symbolToken].volume_moving_avg

        return first_15_min_volume/volume_moving_avg
    
    def money_money_value(self, symbolToken, clientCode):
        percentage_change = self.get_percentage_change(symbolToken, clientCode)
        money_money_factor = self.get_mm_factor(symbolToken, clientCode)
        # self.historicalClient.log_out()
        return (percentage_change * money_money_factor[0])
     
    def calculate_old_details(self, symbolToken):
        try:
            last_date_for_moving_avg = datetime.datetime.combine(self.invokeDate - timedelta(days = self.moving_avg_period*2), datetime.time(15, 28)) # *2 to overcome non trading days
            yesterday = datetime.datetime.combine(self.invokeDate - timedelta(days=1), datetime.time(15, 29))

            abc = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_DAY, last_date_for_moving_avg, yesterday)[-self.moving_avg_period:] # last self.moving_avg_period days data
            last_volume_list = [i[5] for i in abc]

            mm_data = MM_data()
            mm_data.last_day_close = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_DAY, yesterday, self.invokeDate)[-1][4]
            mm_data.volume_moving_avg = sum(last_volume_list)/len(last_volume_list)

            self.dailyData[symbolToken] = mm_data
        except Exception as ex:
            print(ex)
  

















    def get_percentage_change2(self, symbolToken, fifteen_min_data):

        last_day_close = self.dailyData[symbolToken].last_day_close
        # 9:29 CLOSE - last day CLOSE
        change = fifteen_min_data[-2][4] - last_day_close
        # ((9:29 CLOSE - last day CLOSE)/last day CLOSE)*100
        return (change/last_day_close)* 100
    
    def get_mm_factor2(self, symbolToken, fifteen_min_data):
        
        first_15_min_volume = sum([i[5] for i in fifteen_min_data[:-1]])
        volume_moving_avg = self.dailyData[symbolToken].volume_moving_avg

        return first_15_min_volume/volume_moving_avg
    
    def money_money_value2(self, symbolToken, clientCode):
        today_date_9_15 = datetime.datetime.combine(self.invokeDate, datetime.time(9, 15))
        today_date_9_30 = datetime.datetime.combine(self.invokeDate, datetime.time(9, 30))

        if(clientCode == 1):
            first_15_min = self.historicalClient.get_candle_data(symbolToken, CandleIntervals.ONE_MINUTE, today_date_9_15, today_date_9_30)
        elif(clientCode == 2):
            first_15_min = self.historicalClient2.get_candle_data(symbolToken, CandleIntervals.ONE_MINUTE, today_date_9_15, today_date_9_30)
        elif(clientCode == 3):
            first_15_min = self.historicalClient3.get_candle_data(symbolToken, CandleIntervals.ONE_MINUTE, today_date_9_15, today_date_9_30)

        percentage_change = self.get_percentage_change2(symbolToken, first_15_min)
        money_money_factor = self.get_mm_factor2(symbolToken, first_15_min)
        # self.historicalClient.log_out()
        return ((percentage_change * money_money_factor),first_15_min)

class MM_data():
    last_day_close : float
    volume_moving_avg  : float


