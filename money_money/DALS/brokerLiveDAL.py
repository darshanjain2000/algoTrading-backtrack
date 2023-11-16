import datetime
from SmartApi import SmartConnect
import json
import pyotp
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from logzero import logger

class BrokerLiveDAL:
    def __init__(self, interval):
        config_file = open("money_money/config.json")
        configs = json.load(config_file)
        API_KEY = configs["LiveAPI"]["KEY"]
        CLIENT_ID = configs["AngleONE"]["ClientId"]
        pwd = configs["AngleONE"]["Password"]

        token = configs["AngleONE"]["TOTP Code"]
        totp=pyotp.TOTP(token).now()

        self.smartApi = SmartConnect(API_KEY)
        login_data = self.smartApi.generateSession(CLIENT_ID, pwd, totp)

        JWT_TOKEN = login_data["data"]["jwtToken"]
        RESFRESH_TOKEN = login_data["data"]["refreshToken"]
        # feedToken = self.smartApi.getfeedToken()        
        FEED_TOKEN = login_data["data"]["feedToken"]

        self.sws = SmartWebSocketV2(JWT_TOKEN, API_KEY, CLIENT_ID, FEED_TOKEN)

        self.candle_data_list = []
        self.candlestick_interval = datetime.timedelta(minutes=interval)

    def get_candle_data(self, symbolToken, mode = "OHLC", exchange = "NSE"):
        correlation_id = "alphanumid"
        mode = 1  # 1.LTP; 2.Quote; 3.Snap Quote
        token_list = [
            {
                "exchangeType": 1,
                "tokens": [symbolToken]
            }
            # {
            #     "exchangeType": 1,
            #     "tokens": ["26009"]
            # }
        ]

        def on_data(wsapp, message):
            logger.info("Ticks: {}".format(message))
            self.append_candle_data(message)
            # close_connection()

        def on_open(wsapp):
            logger.info("on open")
            self.sws.subscribe(correlation_id, mode, token_list)

        def on_error(wsapp, error):
            logger.error(error)

        def on_close(wsapp):
            logger.info("Close")

        def close_connection():
            self.sws.close_connection()


        # Assign the callbacks.
        self.sws.on_open = on_open
        self.sws.on_data = on_data
        self.sws.on_error = on_error
        self.sws.on_close = on_close

        temp = self.sws.connect()

    def log_out(self):
        try:
            logout=self.smartApi.terminateSession(self.clientId)
            print("Logout Successfull")
        except Exception as e:
            print("Logout failed: {}".format(e.message))

    def append_candle_data(self, tick):
        last_traded_price = tick['last_traded_price']
        tick_time = datetime.fromtimestamp(tick['exchange_timestamp'] / 1000)  # Convert milliseconds to seconds

        # Initialize a new candlestick if it's the first tick or a new candle interval has started
        if self.last_candlestick_time is None or tick_time >= self.last_candlestick_time + self.candlestick_interval:
            if self.current_candle:
                self.candlesticks.append(self.current_candle)  # Append completed candlestick to the list
            self.last_candlestick_time = tick_time.replace(second=0, microsecond=0)
            self.current_candle = {
                "open": last_traded_price,
                "high": last_traded_price,
                "low": last_traded_price,
                "close": last_traded_price,
                "timestamp": self.last_candlestick_time
            }
        else:
            # Update current candlestick with new tick data
            self.current_candle['high'] = max(self.current_candle['high'], last_traded_price)
            self.current_candle['low'] = min(self.current_candle['low'], last_traded_price)
            self.current_candle['close'] = last_traded_price

    def stream_candle_data(self, symbolToken):
        self.get_candle_data(symbolToken)

obj = BrokerLiveDAL()
obj.get_five_min_candle_data()
obj.get_candle_data("3045")