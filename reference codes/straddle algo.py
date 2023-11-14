#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 14:47:28 2021

@author: rk_algopy
"""


#import logging
import datetime
import sys
from datetime import date, timedelta,datetime,time,timezone
import calendar
import statistics
from time import sleep
import pandas as pd
from alice_blue import *
import telegram


alice = None
client=None
socket_opened = False

df_token_ltp = pd.DataFrame(columns=['token','ltp','Open','high','low','close','time'])
df_ohlc = pd.DataFrame(columns=['token','ltp','Open','high','low','close','time'])
todays_max_min_pnl = pd.DataFrame(columns=['time','pnl'])

NSE_holiday = [date(2021, 1, 26),date(2021, 3, 11),date(2021, 3, 29),date(2021, 4, 2),
               date(2021, 4, 14),date(2021, 4, 21),date(2021, 5, 13),
               date(2021, 7, 21),date(2021, 8, 19),date(2021, 9, 10),
               date(2021, 10, 15),date(2021, 11, 5),date(2021, 11, 19)]


# OTHER PARAMETERS -:  CHANGE AS PER YOUR REQUIREMENTS
#Alice blue credentials

username = '301308'
password = 'Hardik26$'
api_secret = '95Wv4zovAaPMs1AWFJAnOHIHM1Rujy7714s9RvaMZkjds2BfRU8EEahtFG0x1PM8'
twoFA = 'hardiksir'
app_id='26xXP3kjJZ'



first_position_entry_time = time(9,30)    # Change time as per your wish
final_position_exit_time  = time(15,15)    # Change time as per your wish
market_close_time = time(15,30)

timeframe = 3                          #RSI Timeframe
num_of_re_check = 3
num_of_lots =1                         # In multiple of 1
expiry_sl = 1.20                       # for 20% it should be 1.2 and so on 
Live_Trade = False             

my_token="1780753038:AAEY2-gmmIcqkBrBGjahw1QyE0EQESEa34I"
bot_chat_id='680755976'
                                     
# OTHER PARAMETERS ENDS:::: -:  CHANGE AS PER REQUIREMENTS ENDS

Is_Run_Now = False
today = date.today()
position_start = datetime.combine(today, first_position_entry_time)
position_entry_wait_time = position_start - timedelta(minutes=30)
isExpiry=False

def event_handler_quote_update(message):
    global ltp
    
    message.pop("instrument",None)        
    ltp = message['ltp']
    Token =message['token']
    Open = message['open']
    high = message['high']
    low = message['low']
    close = message['close']
    time = datetime.now().time().replace(second=0, microsecond=0)
    token_ohlc = [Token,ltp,Open,high,low,close,time]
    append_token_ltp(token_ohlc)
    
def append_token_ltp(token_ohlc):
    try:
        global df_token_ltp
        global df_ohlc
    
        new_series = pd.Series(token_ohlc, index = df_token_ltp.columns)
        df_token_ltp = df_token_ltp.append(new_series, ignore_index=True)
        df_token_ltp.drop_duplicates(subset='token',keep='last',inplace=True)
        
        if datetime.now().minute%timeframe == 2:
            new_series = pd.Series(token_ohlc, index = df_ohlc.columns)
            df_ohlc = df_ohlc.append(new_series, ignore_index=True)
            df_ohlc.drop_duplicates(subset=['token','time'],keep='last',inplace=True)
        
    except Exception as e:
        send(f"error while appending ltp: {e} ::time::{datetime.now().time()}")


def open_callback():
    global socket_opened
    socket_opened = True
    
def open_socket_now():
    global socket_opened

    socket_opened = False
    alice.start_websocket(subscribe_callback=event_handler_quote_update,
                          socket_open_callback=open_callback,
                          run_in_background=True)
    sleep(10)
    while(socket_opened==False):    # wait till socket open & then subscribe
        pass 
                                    
def get_call_n_put_n_place_straddle(atm_ce,atm_pe):
    #send('get_call_n_put_n_place_straddle')
    straddle_status = False
    try:
        global nifty_call,nifty_put,combined_executed_price
        combined_executed_price=0
    
        nifty_call = alice.get_instrument_for_fno(symbol = 'NIFTY', expiry_date= datecalc, is_fut=False, strike=atm_ce, is_CE = True)
        alice.subscribe(nifty_call, LiveFeedType.MARKET_DATA)
        sleep(1)
        nifty_put = alice.get_instrument_for_fno(symbol = 'NIFTY', expiry_date= datecalc, is_fut=False, strike=atm_pe, is_CE = False)
        alice.subscribe(nifty_put, LiveFeedType.MARKET_DATA)
        sleep(1)               
        ce_order_placed =  df_token_ltp.loc[df_token_ltp['token']==nifty_call[1]]['ltp'].values[0]
        pe_order_placed =  df_token_ltp.loc[df_token_ltp['token']==nifty_put[1]]['ltp'].values[0]
        
        order_success,ce_executed_price = sell_Alice_ce(nifty_call,ce_order_placed)  
        if order_success:
            order_success,pe_executed_price = sell_Alice_pe(nifty_put,pe_order_placed)
            if not order_success:
                send(f"Order failed for PE..Exiting existing CE")
                exit_all_positions([str(nifty_call[1])])
            else:                
                if ce_executed_price and pe_executed_price:                    
                    combined_executed_price = ce_executed_price + pe_executed_price
                    send(f"combined_executed_price::{round(combined_executed_price,2)}")
                    straddle_status = True
        else:
            send(f"Order failed for CE..No placing order for PE")
            
        return straddle_status
            
       
      
    except Exception as e:
        send(f"Error in get_ce_curr_price::{e}")
        
def get_order_execued_price(order_id):
    order_success,executed_price=False,0
    num_of_re_rettempt=1
    try:
        for i in range(num_of_re_rettempt):
            
            order = alice.get_order_history(order_id)
            try:
                if len(order['data']) > 0:
                    if order['data'][0]['order_status'] != 'complete':
                        send(f"Rejection reason is:: {order['data'][0]['rejection_reason']}")
                        sleep(1)
                    else:
                        executed_price = order['data'][0]['average_price']
                        order_success = True
                        break
            except Exception as e:
                send(f"Error in get_order_for order id:: {e}")
        if executed_price ==0:
            send(f"Issue while placing order..order_id is {order_id}")
    except Exception as e:
        send(f"Error in get_order_execued_price:: {e}")
    if not Live_Trade:
        order_success= True
    return order_success,executed_price 

def get_date_curr_expiry(atm_ce):
    
    global datecalc
    call = None
    datecalc = date.today()
    while call == None:        
        try:
            call = alice.get_instrument_for_fno(symbol = 'NIFTY', expiry_date= datecalc, is_fut=False, strike=atm_ce, is_CE = True)
            if call == None:
                datecalc = datecalc + timedelta(days=1)
        except:
            pass
    send(f"Date_curr_expiry is:{datecalc}")
    get_sl_percentge(datecalc)

def get_sl_percentge(datecalc):
    global isExpiry
    no_of_days = datecalc - date.today()
    
    if no_of_days.days == 0:
        isExpiry = True
   
    


def sell_Alice_ce(nifty_call,ce_order_placed):
    order_success,executed_price=False,0
    
    quantity = num_of_lots*int(nifty_call[5])  
    try:
        sell_order = alice.place_order(transaction_type = TransactionType.Sell,
                                 instrument = nifty_call,
                                 quantity = quantity,
                                 order_type = OrderType.Market,
                                 product_type = ProductType.Intraday,
                                 price = 0.0,
                                 trigger_price = None,
                                 stop_loss = None,
                                 square_off = None,
                                 trailing_sl = None,
                                 is_amo = False)
       
        if sell_order['status'] == 'success':
            order_id = sell_order['data']['oms_order_id']
            order_success,ce_executed_price = get_order_execued_price(order_id)
            if order_success:
                if ce_executed_price ==0:
                    ce_executed_price=ce_order_placed
                send(f"Sell CE strike:{nifty_call[2]} placed at price :{ce_executed_price} at time{datetime.now().time()}")
                      
        else:
            send(f"Sell CE failed..please check")
    except Exception as e:
        send(f"Error in sell_Alice_ce::{e}")
    return order_success,ce_executed_price    

def sell_Alice_pe(nifty_put,pe_order_placed):
  
    quantity = num_of_lots*int(nifty_put[5])
  
    try:    
        sell_order = alice.place_order(transaction_type = TransactionType.Sell,
                                 instrument = nifty_put,
                                 quantity = quantity,
                                 order_type = OrderType.Market,
                                 product_type = ProductType.Intraday,
                                 price = 0.0,
                                 trigger_price = None,
                                 stop_loss = None,
                                 square_off = None,
                                 trailing_sl = None,
                                 is_amo = False)
       
        if sell_order['status'] == 'success':
            order_id = sell_order['data']['oms_order_id']
            order_success,pe_executed_price = get_order_execued_price(order_id)
            if order_success:
                if pe_executed_price ==0:
                    pe_executed_price=pe_order_placed
                
                send(f"Sell PE strike:{nifty_put[2]} placed at price :{pe_executed_price} at time{datetime.now().time()}")
        else:
            send(f"Sell PE failed..please check")
    except Exception as e:
        send(f"Error in sell_Alice_pe::{e}")
    return order_success,pe_executed_price    


def get_mtm():
    try:
        global todays_max_min_pnl
        positions = alice.get_daywise_positions()
        pnl=0
        for pos in positions['data']['positions']:
        
            pnl = int(float((pos['m2m']).replace(',',''))) + pnl
        
        new_row = [datetime.now().time(),pnl]
        new_series = pd.Series(new_row, index = todays_max_min_pnl.columns)
        todays_max_min_pnl = todays_max_min_pnl.append(new_series, ignore_index=True)
        
        return pnl
    except Exception as e:
        send(f"error get_mtm: {e}")
        

        
def exit_all_positions(ins):
    send("Exiting All positions")
    quantity = num_of_lots*int(nifty_call[5]) 
    
    positions = alice.get_netwise_positions()
    if len(positions['data']['positions']) >0:
        for pos in positions['data']['positions']:
            
            if pos['net_quantity'] < 0:
                if pos['instrument_token'] in ins: #[str(nifty_call[1]),str(nifty_put[1])]:
                    instrument = alice.get_instrument_by_token('NFO', pos['instrument_token'])
                    
                    order = alice.place_order(transaction_type = TransactionType.Buy,
                                 instrument =instrument,
                                 quantity = quantity,
                                 order_type = OrderType.Market,
                                 product_type = ProductType.Intraday,
                                 price = 0.0,
                                 trigger_price = None,
                                 stop_loss = None,
                                 square_off = None,
                                 trailing_sl = None,
                                 is_amo = False)
                    send(f"Exited {quantity} quan from  positions of {instrument[2]}  at price: {pos['ltp']}")
                
def get_RSI(df,period=14):
    try:
        """
        window_length = 14
        delta = df2['ltp'].diff()
        up, down = delta.clip(lower=0), delta.clip(upper=0)
        roll_up1 = up.ewm(span=window_length).mean()
        roll_down1 = down.abs().ewm(span=window_length).mean()
        RS1 = roll_up1 / roll_down1
        df2['RSI1'] = 100.0 - (100.0 / (1.0 + RS1))
        
        roll_up2 = up.rolling(window_length).mean()
        roll_down2 = down.abs().rolling(window_length).mean()
        
        # Calculate the RSI based on SMA
        RS2 = roll_up2 / roll_down2
        df2['RSI2'] = 100.0 - (100.0 / (1.0 + RS2))
        """
        
        #below jig
        delta = df['ltp'].diff()
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        rUp = up.ewm(com=period - 1, adjust=False).mean()
        rDown = down.ewm(com=period - 1, adjust=False).mean().abs()
        df['RSI'] = 100 - 100 / (1 + rUp / rDown)
        df['RSI'].fillna(0, inplace=True)
        #return df
        return df.RSI.values[-1] 
    except Exception as e:
        send(f"RSI::{e}")

def send(msg, chat_id=bot_chat_id, token=my_token):
    print(msg)
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)        

    
def main():
    global alice,socket_opened,Is_Run_Now
    """
    
    while datetime.now().time()<= position_entry_wait_time.time():
        sleep(60)
    """   
    while alice is None:
        send('logging in alice')
        try:
            access_token =  AliceBlue.login_and_get_access_token(username=username, password=password, twoFA=twoFA,  api_secret=api_secret, app_id=app_id)
            alice = AliceBlue(username=username, password=password, access_token=access_token, master_contracts_to_download=['NSE','NFO'])
        except:
            send('login failed Alice..exiting Algo')
            raise SystemExit
            
    if socket_opened == False:
        open_socket_now()
        
    # Get  Nifty Symbol
    
    order_placed,Straddle_Exited,num_of_re_check_counter,cur_minute,cur_minute3 =False,False,0,0,0
    Straddle_re_entered,trailing_combined_premium,data_subscribed= False,0,False
    if datetime.now().time() < first_position_entry_time:
        send(f"Waiting to take first position till {first_position_entry_time}")
           
    while datetime.now().time()<= market_close_time:
        if datetime.now().time() >= time(9,15) and not data_subscribed:
            Nifty_Index = alice.get_instrument_by_symbol('NSE', 'Nifty 50') 
            India_Vix_Index = alice.get_instrument_by_symbol('NSE', 'India VIX') 
            alice.subscribe(India_Vix_Index, LiveFeedType.MARKET_DATA)
            data_subscribed = True
            
        try:      
            if (datetime.now().time().replace(second=0, microsecond=0) == first_position_entry_time or Is_Run_Now) and not order_placed :
                alice.subscribe(Nifty_Index, LiveFeedType.MARKET_DATA)               
                sleep(2)
                straddle_sold_ltp  = df_token_ltp.loc[df_token_ltp['token']==Nifty_Index[1]]['ltp'].values[0]                  
                send(f"Nifty spot price at which straddle is sold is : {straddle_sold_ltp}")
                atm_ce,atm_pe = round(straddle_sold_ltp/50)*50,round(straddle_sold_ltp/50)*50
                send(f"selected Call and Put Strike: ATM_CE: {atm_ce},,ATM_PE: {atm_pe} at time {datetime.now().time()}")
                get_date_curr_expiry(atm_ce)
                straddle_status = get_call_n_put_n_place_straddle(atm_ce,atm_pe)
                if not straddle_status:
                    send(f"Issue while placing straddle..Exiting Algo")
                    break
                if isExpiry:
                    trailing_combined_premium = combined_executed_price
                    send(f"Its Expiry and combined_executed_price {round (combined_executed_price)} and initial sl is {round(combined_executed_price*expiry_sl,2)} ")
                    
                else:
                    if datetime.now().date().weekday() in [0,1,4]:
                        sl_range = combined_executed_price/3
                    elif datetime.now().date().weekday() == 2:
                        sl_range = combined_executed_price/2
                    else:
                        sl_range = combined_executed_price/3                                 
                    send(f"StopLoss range for the straddle..lower::{round(straddle_sold_ltp-sl_range,2)}, Upper::{round(straddle_sold_ltp+sl_range,2)}")
                order_placed,Is_Run_Now = True,False
                
            if order_placed:
                if isExpiry:
                    if not Straddle_Exited:  
                        
                        ce_ltp = df_token_ltp.loc[df_token_ltp['token']==nifty_call[1]]['ltp'].values[0]
                        pe_ltp = df_token_ltp.loc[df_token_ltp['token']==nifty_put[1]]['ltp'].values[0]
                        
                        if (ce_ltp+pe_ltp) > (trailing_combined_premium*expiry_sl):
                           
                           if num_of_re_check_counter > num_of_re_check:                         
                               send(f"Curr price of CE:{ce_ltp} and PE:{pe_ltp} ,has broken the decided range..Exiting the Straddle")
                               send(f"Trailing combined premium was: {trailing_combined_premium} and current sl was {round(trailing_combined_premium*expiry_sl,2)} ")
                            
                               exit_all_positions([str(nifty_call[1]),str(nifty_put[1])])
                               Straddle_Exited = True
                               Straddle_re_entered = False
                           alice.subscribe(nifty_call, LiveFeedType.MARKET_DATA)
                           alice.subscribe(nifty_put, LiveFeedType.MARKET_DATA)
                           sleep(1)
                           num_of_re_check_counter = num_of_re_check_counter + 1
                           
                        if ce_ltp+pe_ltp < trailing_combined_premium and (trailing_combined_premium*expiry_sl) -(ce_ltp+pe_ltp) > 10 :
                           trailing_combined_premium = ce_ltp+pe_ltp
                    
                else:
                    if not Straddle_Exited:  
                        try:                         
                            curr_ltp = df_token_ltp.loc[df_token_ltp['token']==Nifty_Index[1]]['ltp'].values[0]
                        except Exception as e:
                            send(f"error::{e}")
                        
                        if curr_ltp < (straddle_sold_ltp - sl_range) or curr_ltp > (straddle_sold_ltp + sl_range):                       
                            
                            if num_of_re_check_counter > num_of_re_check:
                            
                                send(f"Curr price of NIFTY:: {curr_ltp} ,has broken the decided range..Exiting the Straddle")
                                send(f"StopLoss range for the straddle was..lower::{round(straddle_sold_ltp-sl_range,2)}, Upper::{round(straddle_sold_ltp+sl_range,2)}")
                             
                                exit_all_positions([str(nifty_call[1]),str(nifty_put[1])])
                                Straddle_Exited = True
                                Straddle_re_entered = False
                            alice.subscribe(Nifty_Index, LiveFeedType.MARKET_DATA)
                            sleep(.75)
                            num_of_re_check_counter = num_of_re_check_counter + 1
            
                if Straddle_Exited and not Straddle_re_entered:
                    """
                    if isExpiry:
                        if datetime.now().time() <= time(14):                        
                            Is_Run_Now,order_placed = True,False
                            Straddle_re_entered,Straddle_Exited = True,False
                            send(f"Combined SL hit on Expiry,,Re-entering Straddle")
                        else:
                            send(f"No reentry after 2PM on expiry")
                            break
                        
                    else:
                        
                        if len(df_ohlc)>0 and datetime.now().minute%timeframe ==0 and  datetime.now().minute != cur_minute3:
                            cur_minute3 = datetime.now().minute
                            df_rsi = df_ohlc.loc[df_ohlc['token']==India_Vix_Index[1]].copy()
                            if len(df_rsi) > 14:
                                rsi = get_RSI(df_rsi)
                                df_rsi.to_csv('rsi')
                                send(f"Current value of RSI is : {rsi} at time {datetime.now().time()}")
                                if rsi <= 55:
                        """
                    new_offset = 0
                    bot = telegram.Bot(token=my_token)
                    start_time = datetime.now(tz=timezone.utc)
                    send(f"Please confirm whether algo should reenter straddle..Please type 'yes' in your telegram bot to continue")  
                    while datetime.now().time() <= final_position_exit_time:
                        all_updates = bot.get_updates(new_offset)
                        
                        if len(all_updates) > 0:                                
                            first_chat_text = all_updates[-1]['message']['text']
                            msg_time = all_updates[-1]['message']['date']
                            if msg_time > start_time:
                                if first_chat_text.lower() == 'yes':
                                    send(f"User gave a go ahead..Re-entering Straddle")
                                    Is_Run_Now,order_placed = True,False
                                    Straddle_re_entered,Straddle_Exited = True,False
                                    break
                        sleep(5)
                        
                if  datetime.now().minute%5==0 and  datetime.now().minute != cur_minute:
                    cur_minute = datetime.now().minute
                    num_of_re_check_counter=0
                    if isExpiry:
                        send(f"Current combined prem is {(ce_ltp+pe_ltp)} and New combined SL is :{round(trailing_combined_premium*expiry_sl,2)}")
                    else:
                        send(f"Current nifty price is:{curr_ltp}")
                        
                        
                if datetime.now().time() >= final_position_exit_time:                                 
                    exit_all_positions([str(nifty_call[1]),str(nifty_put[1])])
                    break
            sleep(1)               
        except Exception as e:
            send(f"some error occured at initial main:::->{e}")

           
    
if(__name__ == '__main__'):
    send('started Straddle')
   
    if date.today() in NSE_holiday:
        send('Enjoy!!..Its a no trade day')
        sys.exit()
    
    main()
    send(f"Exiting for the day at time :: {datetime.now().time()}")
    sys.exit()
    
        


   
    
