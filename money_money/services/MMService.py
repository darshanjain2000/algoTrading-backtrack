import datetime
import json
import time
from money_money.DALS.brokerHistoricalDAL import BrokerHistoricalDAL
from money_money.DALS.brokerLiveDAL import BrokerLiveDAL
from money_money.Services.OrderService import OrderService, place_sllimit_order
from money_money.Services.daily_scanner import DailyScanner
from money_money.utils.constants import CandleIntervals
from pytz import timezone

from money_money.utils.trade_details import TradeDetails 


class MMService:
    def __init__(self):
        # self.invoke_date = datetime.date.today() - datetime.timedelta(days=1)
        self.invoke_date = datetime.date.today()
        print("invoke date:",self.invoke_date)

        self.trade = []
        self.stream_5min_data_DAL = None

    def find_stocks_for_trade(self):
        f = open('money_money/utils/nifty_50_token_map.json')
        nifty_50_token = json.load(f)

        money_money = []
        error_token = []
        
        daily_scan_obj = DailyScanner(self.invoke_date)

        start_time_oldData = time.time()
        for stock in nifty_50_token:
            time.sleep(1) # rate limit to get candle data is 3
            daily_scan_obj.calculate_old_details(nifty_50_token[stock])
        print("time taken to calc old data",time.time() - start_time_oldData)


        timeLessThan930 = True
        #if time is 9:30am +
        while timeLessThan930:
            if(datetime.datetime.now(timezone("Asia/Kolkata")).time() > datetime.time(9,30,5)):
                timeLessThan930 = False

        start_time_mm = time.time()
        for indx,i in enumerate(nifty_50_token):
            try:
                # time.sleep(0.4) # rate limit to get candle data is 3
                clientCode = (indx%3)+1 # we have 3 clients apps of historical api
                money_money_value = daily_scan_obj.money_money_value_with_15min_data(nifty_50_token[i],clientCode)
                money_money.append((i, nifty_50_token[i], money_money_value))

                # print(money_money[-1])
                if((indx+1)%3 == 0):
                    time.sleep(1)

            except Exception as ex:
                error_token.append(i)
                print("error in mm calculation",ex)

        print("time taken to calc mm data",time.time() - start_time_mm, "\n")
        
        # print("----------------")
        # print(money_money)

        sorted_money_money = sorted(money_money, key=lambda x: x[2][0])
        selected_stocks = sorted_money_money[:10]

        return selected_stocks
    

    def get_stock_for_live_else_place_order(self, stock_token, stock_name, fifteen_min_data):
        captial = 100000
        check_further_candle = False
        lowest_so_far = 999999

        first_open = fifteen_min_data[0][1]
        first_high = max([i[2] for i in fifteen_min_data[0:5]])
        first_low = min([i[3] for i in fifteen_min_data[0:5]])
        first_close = fifteen_min_data[4][4]
        lowest_so_far =min(lowest_so_far, min([i[3] for i in fifteen_min_data[0:5]]))
        
        # if(first_close < first_open): # need not to check if its red directly check 60% condition
            # check if first closes below 60% or in lower 60% of candle
        threshhold_60 = (first_high-first_low)*0.6
        if(first_close < (first_low + threshhold_60)):
            check_further_candle = True
        else:
            print(f"First candle did not close in below 60% (stock_token: {stock_token}, stock_name: {stock_name})")
            return False

        signal_candle = None
        entry = None
        stoploss = None
        quantity = None
        trigger_time = None
        
        if(check_further_candle):
            # if we get 5 min candle which close in top 40%
            second_open = fifteen_min_data[5][1]
            second_high = max([i[2] for i in fifteen_min_data[5:10]])
            second_low = min([i[3] for i in fifteen_min_data[5:10]])
            second_close = fifteen_min_data[9][4]
            threshhold_40 = (second_high-second_low)*0.4
            if(second_close >= (second_high - threshhold_40)):
                signal_candle = [second_open, second_high, second_low, second_close]
                check_further_candle = False
                lowest_so_far =min(lowest_so_far, min([i[3] for i in fifteen_min_data[5:10]]))
                trigger_time = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 25))

            if(check_further_candle):
                third_open = fifteen_min_data[10][1]
                third_high = max([i[2] for i in fifteen_min_data[10:15]])
                third_low = min([i[3] for i in fifteen_min_data[10:15]])
                third_close = fifteen_min_data[14][4]
                threshhold_40 = (third_high-third_low)*0.4
                if(third_close >= (third_high - threshhold_40)):
                    signal_candle = [third_open, third_high, third_low, third_close]
                    check_further_candle = False
                    lowest_so_far =min(lowest_so_far, min([i[3] for i in fifteen_min_data[10:15]]))
                    trigger_time = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 30))

            entry = lowest_so_far # TO-DO ask lower till signal candle or till 9:30 or lower just before signal candle
            if(signal_candle!=None):
                stoploss = signal_candle[1]

            if(entry != None and stoploss != None):
                risk = 0.005 * captial
                quantity = risk/(stoploss - entry)
        
        if(entry!=None and stoploss != None and quantity != None):
            trade = TradeDetails(stock_name, stock_token, entry, stoploss, quantity, trigger_time)
            self.trade.append(trade)
            # {
            #     "entry_price":entry,
            #     "stoploss" : stoploss,
            #     "quantity" : quantity,
            #     "stock_token": stock_token,
            #     "stock_name": stock_name
            # }
            order_dervice = OrderService()
            order_dervice.place_sllimit_order(trade)

            return False

        return True

    def init_websocket(self, stock_tokens):
        self.stream_5min_data_DAL = BrokerLiveDAL(5, stock_tokens)
        self.stream_5min_data_DAL.stream_candle_data(stock_tokens)
    
    def close_websocket(self):
        self.stream_5min_data_DAL.close_web_socket()


    def strategy_on_live_data(self, stock_token, stock_name, lowest_so_far):
        captial = 100000

        signal_candle = None
        entry = None
        stoploss = None
        quantity = None

        last_itr_index = 0
        while True:
            if(len(self.stream_5min_data_DAL.candle_data_list[stock_token]) == last_itr_index+1):
                if(signal_candle == None):
                    candle_data_5_min = self.stream_5min_data_DAL.candle_data_list[stock_token][-1]
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

        entry = lowest_so_far
        stoploss = signal_candle[1]

        if(entry != None and stoploss != None):
            risk = 0.005 * captial
            quantity = risk/(stoploss - entry)
        
        if(entry!=None and stoploss != None and quantity != None):
            trade = TradeDetails(stock_name, stock_token, entry, stoploss, quantity, time.now())
            self.trade.append(trade)
            # {
            #     "entry_price":entry,
            #     "stoploss" : stoploss,
            #     "quantity" : quantity,
            #     "stock_token": stock_token,
            #     "stock_name": stock_name
            # }
            order_dervice = OrderService()
            order_dervice.place_sllimit_order(trade)