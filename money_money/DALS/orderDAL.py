import datetime
import threading
import time
from SmartApi import SmartConnect
import json
import pyotp
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger

class OrderDAL:
    def __init__(self):
        config_file = open("money_money/config.json")
        configs = json.load(config_file)
        API_KEY = configs["LiveAPI"]["KEY"]
        CLIENT_ID = configs["AngleONE"]["ClientId"]
        self.clientId = configs["AngleONE"]["ClientId"]
        pwd = configs["AngleONE"]["Password"]

        token = configs["AngleONE"]["TOTP Code"]
        totp=pyotp.TOTP(token).now()

        self.smartApi = SmartConnect(API_KEY)
        login_data = self.smartApi.generateSession(CLIENT_ID, pwd, totp)

        JWT_TOKEN = login_data["data"]["jwtToken"]
        RESFRESH_TOKEN = login_data["data"]["refreshToken"]
        # feedToken = self.smartApi.getfeedToken()        
        FEED_TOKEN = login_data["data"]["feedToken"]

        self.res=login_data['data']['exchanges']


    def placeSLLimitOrder(self, stock_symbol, stock_token, entry_price, stoploss_price, quantity):
            try:
                sllo_price = entry_price - 0.05
                orderparams = {
                    "variety": "NORMAL",
                    "tradingsymbol": f"{stock_symbol}",
                    "symboltoken": f"{stock_token}",
                    "transactiontype": "SELL",
                    "exchange": "NSE",
                    "ordertype": "STOPLOSS_LIMIT",
                    "producttype": "INTRADAY",
                    "duration": "DAY",
                    "price": f"{sllo_price}",
                    # "squareoff": "0",
                    # "stoploss": f"{stoploss_price}",
                    "quantity": f"{quantity}"
                    }
                # Method 1: Place an order and return the order ID
                # orderid = self.smartApi.placeOrder(orderparams)
                logger.info(f"PlaceOrder : orderid")
                return "orderid"
            except Exception as e:
                logger.exception(f"Order placement failed: {e}")
