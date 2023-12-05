import datetime
import json
import time
from money_money.DALS.brokerHistoricalDAL import BrokerHistoricalDAL
from money_money.DALS.brokerLiveDAL import BrokerLiveDAL
from money_money.Services.daily_scanner import DailyScanner
from money_money.utils.constants import CandleIntervals



class MMService:
    def __init__(self):
        # self.invoke_date = datetime.date.today() - datetime.timedelta(days=3)
        self.invoke_date = datetime.date.today()

    def find_stocks_for_trade(self):
        f = open('money_money/utils/nifty_50_token_map.json')
        nifty_50_token = json.load(f)

        money_money = []
        error_token = []
        
        daily_scan_obj = DailyScanner(self.invoke_date)

        start_time_oldData = time.time()
        for stock in nifty_50_token:
            time.sleep(0.7) # rate limit to get candle data is 3
            daily_scan_obj.calculate_old_details(nifty_50_token[stock])
        print("time taken to calc old data",time.time() - start_time_oldData)

        start_time_mm = time.time()
        for i in nifty_50_token:
            try:
                time.sleep(0.7) # rate limit to get candle data is 3
                money_money.append((i, nifty_50_token[i], daily_scan_obj.money_money_value(nifty_50_token[i])))
                print(money_money[-1])
            except Exception as ex:
                error_token.append(i)
                print(ex)
        print("time taken to calc mm data 1st",time.time() - start_time_mm)
        
        # print("----------------")
        # print(money_money)

        sorted_money_money = sorted(money_money, key=lambda x: x[2])
        selected_stocks = sorted_money_money[:10]

        return selected_stocks
    
    def sell_strategy(self, stock_token):
        historicalBrokerDAL = BrokerHistoricalDAL()

        today_date_9_15 = datetime.datetime.combine(self.invoke_date, datetime.time(9, 15))
        today_date_9_30 = datetime.datetime.combine(self.invoke_date, datetime.time(9, 30))
        first_15_min_data = historicalBrokerDAL.get_candle_data(stock_token, CandleIntervals.FIVE_MINUTE, today_date_9_15, today_date_9_30)

        check_further_candle = False

        # check first candle is red. If yes, check if first closes below 60% or in lower 60% of candle
        first_open = first_15_min_data[0][1]
        first_high = first_15_min_data[0][2]
        first_low = first_15_min_data[0][3]
        first_close = first_15_min_data[0][4]

        # if(first_close < first_open): # need not to check if its red directly check 60% condition
            # check if first closes below 60% or in lower 60% of candle
        threshhold_60 = (first_high-first_low)*0.6
        if(first_close < (first_high-threshhold_60)):
            check_further_candle = True
        else:
            return None
        # else:
        #     return None

        signal_candle = None
        entry = None
        stoploss = None
        quantity = None

        if(check_further_candle):
            lowest_so_far = 999999
            for i in first_15_min_data:
                lowest_so_far = min(lowest_so_far, i[3]) # i[3] is low of candle
            # check live data 
            stream_5min_data_DAL = BrokerLiveDAL(5, stock_token)
            stream_5min_data_DAL.stream_candle_data()

            last_itr_index = 0
            while True:
                if(len(stream_5min_data_DAL.candle_data_list) == last_itr_index+1):
                    if(signal_candle == None):
                        candle_data_5_min = stream_5min_data_DAL.candle_data_list[-1]
                        lowest_so_far = min(lowest_so_far, candle_data_5_min["low"])
                        
                        # check if any candle close in upper 40%
                        live_candle_open = candle_data_5_min["open"]
                        live_candle_high = candle_data_5_min["high"]
                        live_candle_low = candle_data_5_min["low"]
                        live_candle_close = candle_data_5_min["close"]
                        live_candle_timesatmp = candle_data_5_min["timestamp"]

                        threshhold_40 = (live_candle_high-live_candle_low)*0.4

                        if(live_candle_close >= threshhold_40):
                            signal_candle = [live_candle_open, live_candle_high, live_candle_low, live_candle_close, live_candle_timesatmp, last_itr_index]
                    else:
                        # do entry, stop loss logic
                        if(lowest_so_far <= signal_candle[2]):
                            entry = signal_candle[2]
                            stoploss = None
                            for indx,candle in enumerate(stream_5min_data_DAL.candle_data_list):
                                if(candle["close"]>candle["open"] and indx < signal_candle[5]):
                                    stoploss = candle["high"]

                        # if(entry != None and stoploss != None):
                        #     risk = 0.005 * captial
                        #     quantity = risk/entry-stoploss
                        #     break
                        
                    last_itr_index+= 1

        return {
                "entry_price":entry,
                "stoploss" : stoploss,
                "quantity" : quantity,
                "stock_token": stock_token
            }
        
