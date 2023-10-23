import pandas as pd
from datetime import datetime
import os
import json
import math

def single_day_trade_upper(df, symbol):
    candle_above_upper = 0
    
    sell_at = None
    sell_price = 0
    buy_at = None
    buy_price = 0

    sell_done = False
    
    stop_loss = 0
    stop_loss_trigger = False

    high = 0
    low = 0

    for index, row in df.iterrows():
        if(not sell_done):
            if(pd.to_datetime(row["datetime"].split(" ")[1]).time() < datetime.strptime('11:30', '%H:%M').time()):
                if(row['close']> row['upper_band']): # check green candle closing above bollinger value //TO-DO no need for green or red candle check
                    candle_above_upper += 1
                else:
                    if(candle_above_upper >= 2 and (row['open'] > row['close'])): # check red candle after atleast 2 green below bollinger above value
                        stop_loss = row['high'] # stoploss is signal candle high
                        sell_price = row['low'] # entry is signal candle low
                        sell_at = row["datetime"] # signal candle time
                        sell_done = True

                        high = row['high']
                        low = row['low']

                    candle_above_upper = 0 
        else:
            # to check stoploss is trigger after entry
            if(row["open"] >= stop_loss or row["high"] >= stop_loss or row["low"] >= stop_loss or row["close"] >= stop_loss):
                buy_price = stop_loss
                buy_at = row["datetime"]
                stop_loss_trigger = True
                break
            # to check day end is trigger after entry and stoploss is not triggered
            if(pd.to_datetime(row["datetime"].split(" ")[1]).time().hour == 15):
                buy_price = row["open"]
                buy_at = row["datetime"]
                break

    pAndL = sell_price - buy_price

    entry_time = sell_at
    exit_time = buy_at

    entry_price = sell_price
    exit_price = buy_price

    if(stop_loss_trigger):
        return (symbol[0], sell_at, buy_at, high, low, entry_time, exit_time, entry_price, exit_price, sell_price, buy_price, "StopLoss", "upper", stop_loss, pAndL)
    else:
        return (symbol[0], sell_at, buy_at, high, low, entry_time, exit_time,entry_price, exit_price, sell_price, buy_price, "DayEnd", "upper", stop_loss, pAndL)
    
def single_day_trade_lower(df, symbol):
    candle_above_upper = 0
    
    sell_at = None
    sell_price = 0
    buy_at = None
    buy_price = 0

    buy_done = False
    
    stop_loss = 0
    stop_loss_trigger = False

    high = 0
    low = 0

    for index, row in df.iterrows():
        if(not buy_done):
            if(pd.to_datetime(row["datetime"].split(" ")[1]).time() < datetime.strptime('11:30', '%H:%M').time()):
                if((row['open'] > row['close']) and (row['close'] < row['lower_band'])):  # to check red candle closes below bollinger lower value
                    candle_above_upper += 1
                else:
                    if(candle_above_upper >= 2 and (row['open'] < row['close'])): # check green candle after atleast 2 red below bollinger lower value
                        stop_loss = row['low']    # stoploss is signal candle low
                        buy_price = row['high']   # buy is signal candle high
                        buy_at = row["datetime"]  # signal candle time
                        buy_done = True

                        high = row['high']
                        low = row['low']

                    candle_above_upper = 0
        else:
            # to check stoploss is trigger after entry
            if(row["open"] <= stop_loss or row["high"] <= stop_loss or row["low"] <= stop_loss or row["close"] <= stop_loss):
                sell_price = stop_loss
                sell_at = row["datetime"]
                stop_loss_trigger = True
                break
            # to check day end is trigger after entry and stoploss is not triggered
            if(pd.to_datetime(row["datetime"].split(" ")[1]).time().hour == 15):
                sell_price = row["open"]
                sell_at = row["datetime"]
                break
    
    pAndL = sell_price - buy_price

    entry_time = buy_at
    exit_time = sell_at

    entry_price = buy_price
    exit_price = sell_price

    if(stop_loss_trigger):
        return (symbol[0], sell_at, buy_at, high, low, entry_time, exit_time, entry_price, exit_price, sell_price, buy_price, "StopLoss", "lower", stop_loss, pAndL)
    else:
        return (symbol[0], sell_at, buy_at, high, low, entry_time, exit_time,entry_price, exit_price, sell_price, buy_price, "DayEnd", "lower", stop_loss, pAndL)

def single_day_trade_upper_next(df, symbol):
    candle_above_upper = 0
    
    sell_at = None
    sell_price = 0
    buy_at = None
    buy_price = 0

    sell_done = False
    signal_candle = False
    
    stop_loss = 0
    stop_loss_trigger = False

    high = 0
    low = 0

    for index, row in df.iterrows():
        if(not sell_done):
            if(not signal_candle):
                if(pd.to_datetime(row["datetime"].split(" ")[1]).time() < datetime.strptime('12:30', '%H:%M').time()):
                    if(row['close']> row['upper_band']): # check green candle closing above bollinger value //TO-DO no need for green or red candle check
                        candle_above_upper += 1
                    else:
                        if(candle_above_upper >= 2 and (row['open'] > row['close'])): # check red candle after atleast 2 green below bollinger above value
                            stop_loss = row['high'] # stoploss is signal candle high
                            sell_price = row['low'] # entry is signal candle low
                            sell_at = row["datetime"] # signal candle time
                            signal_candle = True

                            high = row['high']
                            low = row['low']

                        candle_above_upper = 0   
            else:
                if(row['low'] < sell_price and datetime.strptime('12:30', '%H:%M').time()): #(within 2 next candle next_to_signal_candle["low"] is less than signal["low"] then entry is signal cangdle entry )
                    sell_done = True
                
        else:
            # to check stoploss is trigger after entry
            if(row["open"] >= stop_loss or row["high"] >= stop_loss or row["low"] >= stop_loss or row["close"] >= stop_loss):
                buy_price = stop_loss
                buy_at = row["datetime"]
                stop_loss_trigger = True
                break
            # to check day end is trigger after entry and stoploss is not triggered
            if(pd.to_datetime(row["datetime"].split(" ")[1]).time().hour == 15):
                buy_price = row["open"]
                buy_at = row["datetime"]
                break

    pAndL = sell_price - buy_price

    entry_time = sell_at
    exit_time = buy_at

    entry_price = sell_price
    exit_price = buy_price

    if(stop_loss_trigger):
        return (symbol[0], sell_at, buy_at, high, low, entry_time, exit_time, entry_price, exit_price, sell_price, buy_price, "StopLoss", "upper", stop_loss, pAndL)
    else:
        return (symbol[0], sell_at, buy_at, high, low, entry_time, exit_time,entry_price, exit_price, sell_price, buy_price, "DayEnd", "upper", stop_loss, pAndL)
    
def single_day_trade_lower_next(df, symbol):
    candle_above_upper = 0
    
    sell_at = None
    sell_price = 0
    buy_at = None
    buy_price = 0

    buy_done = False
    signal_candle = False

    stop_loss = 0
    stop_loss_trigger = False

    high = 0
    low = 0

    for index, row in df.iterrows():
        if(not buy_done):
            if(not signal_candle):
                if(pd.to_datetime(row["datetime"].split(" ")[1]).time() < datetime.strptime('12:30', '%H:%M').time()):
                    if(row['close'] < row['lower_band']):  # to check red candle closes below bollinger lower value
                        candle_above_upper += 1
                    else:
                        if(candle_above_upper >= 2 and (row['open'] < row['close'])): # check green candle after atleast 2 red below bollinger lower value
                            stop_loss = row['low']    # stoploss is signal candle low
                            buy_price = row['high']   # buy is signal candle high
                            buy_at = row["datetime"]  # signal candle time
                            buy_done = True

                            high = row['high']
                            low = row['low']

                        candle_above_upper = 0
            else:
                if(row['high'] > buy_price and datetime.strptime('12:30', '%H:%M').time()): #(within 2 next candle next_to_signal_candle["upper"] is less than signal["upper"] then entry is signal cangdle entry )
                    buy_done = True
        else:
            # to check stoploss is trigger after entry
            if(row["open"] <= stop_loss or row["high"] <= stop_loss or row["low"] <= stop_loss or row["close"] <= stop_loss):
                sell_price = stop_loss
                sell_at = row["datetime"]
                stop_loss_trigger = True
                break
            # to check day end is trigger after entry and stoploss is not triggered
            if(pd.to_datetime(row["datetime"].split(" ")[1]).time().hour == 15):
                sell_price = row["open"]
                sell_at = row["datetime"]
                break
    
    pAndL = sell_price - buy_price

    entry_time = buy_at
    exit_time = sell_at

    entry_price = buy_price
    exit_price = sell_price

    if(stop_loss_trigger):
        return (symbol[0], sell_at, buy_at, high, low, entry_time, exit_time, entry_price, exit_price, sell_price, buy_price, "StopLoss", "lower", stop_loss, pAndL)
    else:
        return (symbol[0], sell_at, buy_at, high, low, entry_time, exit_time,entry_price, exit_price, sell_price, buy_price, "DayEnd", "lower", stop_loss, pAndL)



def get_2022_data():
    base_path = "clean data/15min"
    csv_names = os.listdir(base_path)

    idx = 1
    for csv_name in csv_names:
        data_2022 = []
        df_15min = pd.read_csv(f"{base_path}/{csv_name}")

        for index, row in df_15min.iterrows():
            if(row["datetime"].split(" ")[0].split("-")[0] == '2022'):
                data_2022.append((row["datetime"],row["symbol"],row["open"],row["high"],row["low"],row["close"],row["volume"]))
        
        column_names = ["datetime","symbol","open","high","low","close","volume"]
        df = pd.DataFrame(data_2022,columns=column_names)
        df.dropna(inplace=True)
        df.to_csv(f"bollinger on data set/csv data/2022/{csv_name}")

        print(idx, csv_name)
        idx+=1
    
def get_stocks_percentage_change():
    base_path = "bollinger on data set/csv data/2022"
    csv_names = os.listdir(base_path)
    csv_names.remove("1day")

    def convert_1min_to_1day(csv_name):
        df = pd.read_csv(f"{base_path}/{csv_name}")

        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)

        df_1day = df.resample('1D').agg({
            'symbol': 'first',
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })

        df_1day.dropna(inplace=True)
        df_1day.to_csv(f"{base_path}/1day/{csv_name}")

    idex = 1
    for csv_name in csv_names:
        convert_1min_to_1day(csv_name)

        with_day_change = []
        df_1d = pd.read_csv(f"{base_path}/1day/{csv_name}")

        df_1min = pd.read_csv(f"clean data/{csv_name}")
        df_1min['datetime'] = pd.to_datetime(df_1min['datetime'])
        df_1min.set_index('datetime', inplace=True)

        for idx in range(1,len(df_1d)):
            today_date = df_1d.iloc[idx]["datetime"]

            day1_closing = df_1d.iloc[idx-1]["close"]
            day2_custom_open = df_1min.loc[f"{today_date} 09:46:00"]["open"]

            percentage_change = ((day2_custom_open - day1_closing) / day1_closing) * 100
            with_day_change.append((df_1d.iloc[idx]["datetime"],df_1d.iloc[idx]["symbol"],df_1d.iloc[idx]["open"],df_1d.iloc[idx]["high"],df_1d.iloc[idx]["low"],df_1d.iloc[idx]["close"],df_1d.iloc[idx]["volume"], percentage_change))

        column_names = ["datetime","symbol","open","high","low","close","volume", "percentage change"]
        df = pd.DataFrame(with_day_change,columns=column_names)
        df.dropna(inplace=True)
        df.to_csv(f"bollinger on data set/csv data/2022 daily change/{csv_name}")

        print(idex ,csv_name)
        idex+=1

def daily_sorted_stock_diff():
    path = "bollinger on data set/csv data/2022 daily change"
    stocks = os.listdir(path)

    dataset = {}
    for i in stocks:
        df = pd.read_csv(f"{path}/{i}")
        for j in range(1,len(df)):

            if(dataset.get(df.iloc[j]["datetime"])==None):
                dataset[df.iloc[j]["datetime"]] = [(i.split(".")[0],df.iloc[j]["percentage change"])]
            else:
                dataset[df.iloc[j]["datetime"]].append((i.split(".")[0],df.iloc[j]["percentage change"]))

        print("done", i)
    print("DONE")
    print(dataset)

    sorted_date_dict = dict(sorted(dataset.items(), key=lambda item: item[0]))

    with open("bollinger on data set/daily_sorted_stock_diff.json", "w") as outfile:
        json.dump(sorted_date_dict, outfile)

def sort_daily_diff():
    f = open('bollinger on data set/daily_sorted_stock_diff.json')
    data = json.load(f)
    for i in data:
        sorted_list = sorted(data[i], key=lambda x: x[1])
        print(sorted_list)
        data[i] = sorted_list

    with open("bollinger on data set/daily_sorted_stock_diff_sorted.json", "w") as json_file:
        json.dump(data, json_file)

def generate_bollinger_bands_values():
    path = "bollinger on data set/csv data/2022/"
    csvs = os.listdir(path)
    csvs.remove("1day")
    csvs.remove("bollinger values")

    for csv in csvs:
        df_15min = pd.read_csv(f"{path}/{csv}")

        window = 20 
        std_dev = 2

        df_15min['rolling_mean'] = df_15min['close'].rolling(window=window).mean()
        df_15min['rolling_std'] = df_15min['close'].rolling(window=window).std()

        df_15min['upper_band'] = df_15min['rolling_mean'] + (std_dev * df_15min['rolling_std'])
        df_15min['lower_band'] = df_15min['rolling_mean'] - (std_dev * df_15min['rolling_std'])

        df_15min.dropna(inplace=True)

        df_15min.to_csv(f"bollinger on data set/csv data/2022/bollinger values/{csv}")

        print("Done",csv)

    print("DONE")



def apply():
    f = open('bollinger on data set/daily_sorted_stock_diff_sorted.json')
    data = json.load(f)

    signals = []
    error = []
    top_size = 10
    for day in data:
        signal = []

        gainer = data[day][-top_size:]
        loser = data[day][:top_size]

        for top in gainer:
            df = pd.read_csv(f"bollinger on data set/csv data/2022/bollinger values/{top[0]}.csv")
            day_df = df[df['datetime'].str.startswith(day)]
            if(len(day_df) == 25):
                upper = single_day_trade_upper(day_df,top)
                lower = single_day_trade_lower(day_df,top)
                
                if(upper[1] != None):# to remove not fullfilled request
                    signal.append(upper)
                if(lower[1] != None):
                    signal.append(lower)

            else:
                print(f"day data size is not 25 for {low}@{day}")
                error.append(f"{low}@{day}")
            
        for low in loser:
            df = pd.read_csv(f"bollinger on data set/csv data/2022/bollinger values/{low[0]}.csv")
            day_df = df[df['datetime'].str.startswith(day)]
            if(len(day_df) == 25):
                upper = single_day_trade_upper_next(day_df,low)
                lower = single_day_trade_lower_next(day_df,low)
                
                if(upper[1] != None): # to remove not fullfilled request
                    signal.append(upper)
                if(lower[1] != None):
                    signal.append(lower)
            else:
                print(f"day data size is not 25 for {low}@{day}")
                error.append(f"{low}@{day}")

        if(len(signal)>5):

            def key_function(item):
                format_string = "%Y-%m-%d %H:%M:%S"

                if(item[12] == "lower"): #if(row["Operation"] == "lower"):
                    date_time_obj = datetime.strptime(item[2], format_string) # row["Buy Time"]
                if(item[12] == "upper"):
                    date_time_obj = datetime.strptime(item[1], format_string) # row["Sell Time"]
                
                return date_time_obj.time()

            sorted_data = sorted(signal, key=key_function)

            signals.extend(sorted_data[:5])

        else:
            signals.extend(signal)

        print("done",day)

    signals_df = pd.DataFrame(signals, columns=["Symbol", "Sell Time", "Buy Time", "High at order", "Low at order", "Entry", "Exit", "Entry Price", "Exit Price", "Sell Price", "Buy Price", "Exit Type", "Operation", "StopLoss", "P and L" ])
    signals_df.dropna(inplace=True)
    signals_df.to_csv("bollinger on data set/signals_next2.csv")
    print(error)

def calc_funds():
    available_funds = 100000
    risk = 0.005

    df = pd.read_csv(f"bollinger on data set/signals_next2.csv")

    day = "2022-01-05"
    day_pl = 0
    
    net_pl=[]

    for index, row in df.iterrows():
        if(day == row["Sell Time"].split(" ")[0]):          
            if(row["Operation"] == "upper"):
                quantity = math.floor(abs((risk*available_funds)/(row["Sell Price"]-row["StopLoss"])))
            if(row["Operation"] == "lower"):
                quantity = math.floor(abs((risk*available_funds)/(row["Buy Price"]-row["StopLoss"])))
            row["net PL"] = quantity*row["P and L"]
            row["funds"] = available_funds
            day_pl += row["net PL"]
        else:
            day = row["Sell Time"].split(" ")[0]
            available_funds += day_pl
            day_pl = 0

            if(row["Operation"] == "upper"):
                quantity = math.floor(abs((risk*available_funds)/(row["Sell Price"]-row["StopLoss"])))
            if(row["Operation"] == "lower"):
                quantity = math.floor(abs((risk*available_funds)/(row["Buy Price"]-row["StopLoss"])))
            row["net PL"] = quantity*row["P and L"]
            row["funds"] = available_funds
            day_pl += row["net PL"]
        
        net_pl.append((row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14], row[15],row[16],row[17]))

    colums_header = ["Symbol", "Sell Time", "Buy Time", "High at order", "Low at order", "Entry", "Exit", "Entry Price", "Exit Price", "Sell Price", "Buy Price", "Exit Type", "Operation", "StopLoss", "P and L","net p&l","funds" ]
    # colums_header = ["Symbol", "Sell Time", "Sell Price", "Buy Time", "Buy Price", "High at order", "Low at order", "Exit Type", "Operation", "P and L", "Stop Loss","net SL","net p&l","funds"]
    signals_df = pd.DataFrame(net_pl, columns=colums_header)
    signals_df.to_csv("bollinger on data set/signals_next2_pl.csv")


def generate_rsi_values_csv():
    def calculate_rsi(data, period=14):
        deltas = [data[i] - data[i - 1] for i in range(1, len(data))]
        gain = [d if d > 0 else 0 for d in deltas]
        loss = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gain[:period]) / period
        avg_loss = sum(loss[:period]) / period

        rs_values = [avg_gain / avg_loss] if avg_loss > 0 else [0]

        for i in range(period, len(data) - 1):
            avg_gain = (avg_gain * (period - 1) + gain[i]) / period
            avg_loss = (avg_loss * (period - 1) + loss[i]) / period
            rs = avg_gain / avg_loss
            rs_values.append(rs)

        rsi_values = [100 - (100 / (1 + rs)) for rs in rs_values]

        return [None] * period + rsi_values
    
    path = "bollinger on data set/csv data/2022/bollinger values"
    csvs = os.listdir(path)
    csvs.remove("rsi value")

    rsi_period = 14
    
    for csv in csvs:
        df_15min = pd.read_csv(f"{path}/{csv}")
        rsi_values = calculate_rsi(df_15min["close"], rsi_period)
        df_15min["RSI"] = rsi_values
        df_15min.to_csv(f"bollinger on data set/csv data/2022/bollinger values/rsi value/{csv}", index=False)


    
generate_rsi_values_csv()
        