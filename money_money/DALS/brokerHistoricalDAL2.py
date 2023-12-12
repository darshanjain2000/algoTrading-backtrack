from SmartApi import SmartConnect
import json
import pyotp


class BrokerHistoricalDAL2:
    def __init__(self):
        config_file = open("money_money/config.json")
        configs = json.load(config_file)
        api_key = configs["HistorialAPI2"]["KEY"]
        self.clientId = configs["AngleONE"]["ClientId"]
        pwd = configs["AngleONE"]["Password"]

        token = configs["AngleONE"]["TOTP Code"]
        totp=pyotp.TOTP(token).now()

        self.smartApi = SmartConnect(api_key)
        data = self.smartApi.generateSession(self.clientId, pwd, totp)
        # authToken = data['data']['jwtToken']
        # refreshToken = data['data']['refreshToken']

        # # fetch the feedtoken
        # feedToken = self.smartApi.getfeedToken()

        # # fetch User Profile
        # res = self.smartApi.getProfile(refreshToken)
        # self.smartApi.generateToken(refreshToken)
        # res=res['data']['exchanges']

    def get_candle_data(self, symbolToken, interval, fromDate, toDate, exchange = "NSE"):
        try:
            if(type(fromDate) != str):
                fromDate = fromDate.strftime("%Y-%m-%d %H:%M")
            if(type(toDate) != str):
                toDate = toDate.strftime("%Y-%m-%d %H:%M")
                
            historicParam={
            "exchange": exchange,
            "symboltoken": symbolToken,
            "interval": interval,
            "fromdate": fromDate, 
            "todate": toDate #"2021-02-08 09:16"
            }
            candle_data = self.smartApi.getCandleData(historicParam)
            if(candle_data["message"] == "SUCCESS"):
                return candle_data['data']
            else:
                return None
        except Exception as e:
            print(f"Historic Api failed: {e.code} :{e}")

    def log_out(self):
        try:
            logout=self.smartApi.terminateSession(self.clientId)
            print("Logout Successfull")
        except Exception as e:
            print("Logout failed: {}".format(e.message))