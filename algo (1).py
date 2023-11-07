from pathlib import Path
import requests
import json
import pandas as pd
from time import sleep
from datetime import datetime, time, timedelta,date
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import numpy as np
import telegram
import yfinance as yf

symbol_yf = {'NIFTY':"^NSEI" , 'BANKNIFTY': "^NSEBANK"}

pd.set_option('display.width', 1500)
pd.set_option('display.max_columns', 75)
pd.set_option('display.max_rows', 1500)

open_sp = 16111
expiry = None
excel_file = "Option_Chain_Analysis.xlsx"

oi_filename = os.path.join("Files", "oi_data_records_{0}.json".format(
    datetime.now().strftime("%d%m%y")))
mp_filename = os.path.join("Arpit", "mp_data_records_{0}.json".format(
    datetime.now().strftime("%d%m%y")))
df_list = []
mp_list = []


my_token = "1934115088:AAHzlJh-NKPm2MXiTpoHrpfm32ahvYZMUBI"
user_list = ["680755976"]


def send(msg, token=my_token):
    bot = telegram.Bot(token=token)
    for user in user_list:
        bot.sendMessage(chat_id=user, text=msg)

def get_cumulative_changeinoe(data,open_price):
    index = [-3,-2,-1,0,1,2,3]
    ans =0
    for i in range(1,len(data)):
        if(list(data["strikePrice"])[i] > open_price):
            for ind in index:
                if i +ind > 0 and i + ind < len(data) -1:
                    ans += data["changeinOpenInterest"][i+ind]
            break
    print("Change in oi",ans)
    return ans            


def fetch_oi(df, mp_df,symbol):
    print("loading oi")
    tries = 1
    max_retries = 3
    while tries <= max_retries:
        # try:
        # if True:
            ticker = yf.Ticker(symbol_yf[symbol])
            open_sp = list(ticker.history(period="2d",interval="1d")["Open"])[-1]
            print("Open Price",symbol,open_sp)
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
                'Accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'referer': 'https://www.nseindia.com/api/option-chain-indices?symbol='+symbol}
            url = "https://www.nseindia.com/api/option-chain-indices?symbol="+symbol

            r = requests.get(url, headers=default_headers).json()
           
            if expiry == False:
                ce_values = [data['CE'] for data in r['records']['data'] if "CE" in data and str(
                    data['expiryDate']).lower() == str(expiry).lower()]
                pe_values = [data['PE'] for data in r['records']['data'] if "PE" in data and str(
                    data['expiryDate']).lower() == str(expiry).lower()]
            else:
                ce_values = [data['CE']
                             for data in r['filtered']['data'] if "CE" in data]
                pe_values = [data['PE']
                             for data in r['filtered']['data'] if "PE" in data]

            ce_data = pd.DataFrame(ce_values)
            pe_data = pd.DataFrame(pe_values)
            ce_data = ce_data.sort_values(['strikePrice'])
            pe_data = pe_data.sort_values(['strikePrice'])
            ce_data['type'] = "CE"
            pe_data['type'] = "PE"
            df = pd.concat([ce_data,pe_data])

            oic_ce = get_cumulative_changeinoe(ce_data, open_sp)
            oic_pe = get_cumulative_changeinoe(pe_data, open_sp)

            return df,oic_ce - oic_pe

         except Exception as error:
            # print("error{0}".format(error), "failed")
            # tries = +1
            # sleep(10)
            # continue

    if tries >= max_retries:
        print("Max retries exceeded no new data at time{0}".format(
            datetime.now()))
        return df, mp_df


def main():
    global df_list
    print("starting script")
    try:
        df_list = json.loads(open(oi_filename).read())
    except Exception as error:
        print("Error reading data .Error:{0}".format(error))
        df_list = []
    if df_list:
        df = pd.DataFrame()
        for item in df_list:
            df = pd.concat([df, pd.DataFrame(item)])
    else:
        df = pd.DataFrame()

    try:
        mp_list = json.loads(open(mp_filename).read())
        mp_df = pd.DataFrame().from_dict(mp_list)
    except Exception as error:
        print("Error reading data .Error:{0}".format(error))
        mp_list = []
        mp_df = pd.DataFrame()

    timeframe = 5
    while time(9, 12) <= datetime.now().time() <= time(15, 50):
        timenow = datetime.now()
        check = True 
        # if timenow.minute / \
        #     10 in list(np.arange(0.0, 20.0)) else False
       
        if check:
            nextscan = timenow + timedelta(minutes=timeframe)
            df,nifty_value_oic = fetch_oi(df, mp_df,"NIFTY")
            df, banknifty_value_oic = fetch_oi(df, mp_df, "BANKNIFTY")

            if not df.empty:
                
                send(f' NIFTY Cumulative change in oi : {nifty_value_oic} \n BANKNIFTY cumulative change in oi : {banknifty_value_oic}')
                waitsecs = int((nextscan - datetime.now()).seconds)
                print("Wait for {0} seconds".format(waitsecs))
                sleep(waitsecs) if waitsecs > 0 else sleep(0)
            else:
                send(
                    f' NIFTY Cumulative change in oi : {nifty_value_oic} \n BANKNIFTY cumulative change in oi : {banknifty_value_oic}')

                print("No data received ")
                sleep(30)


if __name__ == '__main__':
    main()
