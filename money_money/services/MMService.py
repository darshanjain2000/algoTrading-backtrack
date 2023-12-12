import datetime
import json
import time
from money_money.DALS.brokerHistoricalDAL import BrokerHistoricalDAL
from money_money.DALS.brokerLiveDAL import BrokerLiveDAL
from money_money.Services.daily_scanner import DailyScanner
from money_money.utils.constants import CandleIntervals


class MMService:
    def __init__(self):
        self.invoke_date = datetime.date.today() - datetime.timedelta(days=1)
        # self.invoke_date = datetime.date.today()
        print("invoke date:",self.invoke_date)

        self.trade = []

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

        #if time is 9:30am +
        for indx,i in enumerate(nifty_50_token):
            try:
                # time.sleep(0.4) # rate limit to get candle data is 3
                clientCode = (indx%3)+1 # we have 3 clients apps of historical api
                money_money_value = daily_scan_obj.money_money_value2(nifty_50_token[i],clientCode)
                money_money.append((i, nifty_50_token[i], money_money_value))
                print(money_money[-1])
                if(clientCode == 3):
                    time.sleep(0.8)

            except Exception as ex:
                error_token.append(i)
                print(ex)

        print("time taken to calc mm data 1st",time.time() - start_time_mm)
        
        # print("----------------")
        # print(money_money)

        sorted_money_money = sorted(money_money, key=lambda x: x[2][0])
        selected_stocks = sorted_money_money[:10]

        return selected_stocks
    
    def sell_strategy(self, stock_token, fifteen_min_data):
        captial = 100000

        historicalBrokerDAL = BrokerHistoricalDAL()

        # today_date_9_15 = datetime.datetime.combine(self.invoke_date, datetime.time(9, 15))
        # today_date_9_30 = datetime.datetime.combine(self.invoke_date, datetime.time(9, 30))
        # first_15_min_data = historicalBrokerDAL.get_candle_data(stock_token, CandleIntervals.FIVE_MINUTE, today_date_9_15, today_date_9_30)

        check_further_candle = False

        # check first candle is red. If yes, check if first closes below 60% or in lower 60% of candle
        # first_open = first_15_min_data[0][1]
        # first_high = first_15_min_data[0][2]
        # first_low = first_15_min_data[0][3]
        # first_close = first_15_min_data[0][4]
        first_open = fifteen_min_data[0][1]
        first_high = max([i[2] for i in fifteen_min_data[0:5]])
        first_low = min([i[3] for i in fifteen_min_data[0:5]])
        first_close = fifteen_min_data[4][4]

        # if(first_close < first_open): # need not to check if its red directly check 60% condition
            # check if first closes below 60% or in lower 60% of candle
        threshhold_60 = (first_high-first_low)*0.6
        if(first_close < (first_low + threshhold_60)):
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
            # for i in first_15_min_data:
            #     lowest_so_far = min(lowest_so_far, i[3]) # i[3] is low of candle
            lowest_so_far = min([i[2] for i in fifteen_min_data])
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

                        if(live_candle_close >= (live_candle_high - threshhold_40)):
                            signal_candle = [live_candle_open, live_candle_high, live_candle_low, live_candle_close, live_candle_timesatmp, last_itr_index]
                            break
                    last_itr_index += 1 
            while True:   
                # do entry, stop loss logic
                if(len(stream_5min_data_DAL.live_data)>0):
                    if(lowest_so_far <= stream_5min_data_DAL.live_data[-1]):
                        entry = stream_5min_data_DAL.live_data[-1]  # TO-DO, or signal_candle[2] # signal candle low
                        stoploss = signal_candle[1] # signal candle high
                        break
                        # for indx,candle in enumerate(stream_5min_data_DAL.candle_data_list):
                        #     if(candle["close"]>candle["open"] and indx < signal_candle[5]):
                        #         stoploss = candle["high"]

            if(entry != None and stoploss != None):
                risk = 0.005 * captial
                quantity = risk/(entry-stoploss)
        
        if(entry!=None and stoploss != None and quantity != None):
            self.trade.append({
                "entry_price":entry,
                "stoploss" : stoploss,
                "quantity" : quantity,
                "stock_token": stock_token
            })
            
        return {
                "entry_price":entry,
                "stoploss" : stoploss,
                "quantity" : quantity,
                "stock_token": stock_token
            }
        
