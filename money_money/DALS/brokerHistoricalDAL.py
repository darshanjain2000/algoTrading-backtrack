from SmartApi import SmartConnect
import json
import pyotp


class BrokerHistoricalDAL:
    def __init__(self):
        config_file = open("money_money/config.json")
        configs = json.load(config_file)
        api_key = configs["HistorialAPI"]["KEY"]
        clientId = configs["AngleONE"]["ClientId"]
        pwd = configs["AngleONE"]["Password"]

        token = configs["AngleONE"]["TOTP Code"]
        totp=pyotp.TOTP(token).now()

        self.smartApi = SmartConnect(api_key)
        data = self.smartApi.generateSession(clientId, pwd, totp)
        # authToken = data['data']['jwtToken']
        # refreshToken = data['data']['refreshToken']

        # # fetch the feedtoken
        # feedToken = self.smartApi.getfeedToken()

        # # fetch User Profile
        # res = self.smartApi.getProfile(refreshToken)
        # self.smartApi.generateToken(refreshToken)
        # res=res['data']['exchanges']

    def get_candle_data(self):
        try:
            historicParam={
            "exchange": "NSE",
            "symboltoken": "3045",
            "interval": "ONE_MINUTE",
            "fromdate": "2021-02-08 09:00", 
            "todate": "2021-02-08 09:16"
            }
            candle_data = self.smartApi.getCandleData(historicParam)
            print(candle_data)
        except Exception as e:
            print("Historic Api failed: {}".format(e.message))



BrokerHistoricalDAL().get_candle_data()