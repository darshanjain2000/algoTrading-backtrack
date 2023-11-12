import datetime
import json
import time
from money_money.DALS.brokerHistoricalDAL import BrokerHistoricalDAL
from money_money.DALS.brokerLiveDAL import BrokerLiveDAL
from money_money.Services.daily_scanner import DailyScanner
from money_money.utils.constants import CandleIntervals

class MMService:
    def __init__(self):
        self.invoke_date = datetime.date.today() - datetime.timedelta(days=3)
        # self.invoke_date = datetime.date.today()

    def find_stocks_for_trade(self):
        f = open('money_money/utils/nifty_200_token_map.json')
        nifty_200_token = json.load(f)

        money_money = []
        for i in nifty_200_token:
            money_money.append((i, nifty_200_token[i], DailyScanner(nifty_200_token[i], self.invoke_date).money_money_value()))
            print(money_money[-1])
            time.sleep(.25)

        # print(money_money)
        # money_money = [('BEL-EQ', '383', -1225.4281688991023),('DEVYANI-EQ', '5373', -968.9460395322369),('TATAPOWER-EQ', '3426', -1394.2108649602676),('SAIL-EQ', '2963', -8732.522495980103),('FLUOROCHEM-EQ', '13750', -0.5115687462065532),('BANKINDIA-EQ', '4745', 1940.8623793505144),('BPCL-EQ', '526', -297.34823733400583),('PIDILITIND-EQ', '2664', 4.6560470613430525),('TORNTPHARM-EQ', '3518', -0.5070066101716069),('DABUR-EQ', '772', -107.65844652070102),('GUJGASLTD-EQ', '10599', -31.100712072608246),('AUROPHARMA-EQ', '275', -596.4973373323036),('SHRIRAMFIN-EQ', '4306', -3.544294255451949),('PAYTM-EQ', '6705', -104.64388972680008),('CIPLA-EQ', '694', -3.5097766336018728),('TRENT-EQ', '1964', -8.534269982647245),('INFY-EQ', '1594', 9.447029003294778),('ASHOKLEY-EQ', '212', -7973.800966215393),('IGL-EQ', '11262', -19.70704852192087),('BAJAJHLDNG-EQ', '305', -0.028894072431385132),('MFSL-EQ', '2142', -11.036709767274038),('GRASIM-EQ', '1232', -7.686140046813682),('L&TFH-EQ', '24948', -357.2608987044561),('SBIN-EQ', '3045', -120.55686564563018),('MSUMI-EQ', '8596', -1041.8892347666508),('HINDPETRO-EQ', '1406', -266.82426015934476),('BOSCHLTD-EQ', '2181', 0.12320575501573926),('INDIGO-EQ', '11195', 9.879249938875585),('VBL-EQ', '18921', -0.28287109403779137),('TATACONSUM-EQ', '3432', -54.66318009305465),('PAGEIND-EQ', '14413', -0.17848316587635862),('SUNTV-EQ', '13404', 40.92469061756598),('HINDALCO-EQ', '1363', 40.057619228841),('BHARTIARTL-EQ', '10604', -14.707626909196629),('AMBUJACEM-EQ', '1270', 25.915890504635776),('RECLTD-EQ', '15355', -3870.307750158121),('PETRONET-EQ', '11351', -4366.843072629817),('ZEEL-EQ', '3812', 25628.321094530573),('DRREDDY-EQ', '881', -3.6015410072580805),('HAVELLS-EQ', '9819', -8.048614369233475),('GODREJPROP-EQ', '17875', 157.2650804845995),('DLF-EQ', '14732', -127.62900825694608),('BAJFINANCE-EQ', '317', -1.4753022793495283),('ALKEM-EQ', '11703', -10.736477188910447),('LTTS-EQ', '18564', -0.277170505225649),('BATAINDIA-EQ', '371', -1.8664479649201948),('POLYCAB-EQ', '9590', -3.8010677741669427),('VEDL-EQ', '3063', -10031.8216050015),('M&M-EQ', '2031', 30.93462823715081),('COFORGE-EQ', '11543', -1.895451160273776),('RELIANCE-EQ', '2885', -76.97111006468919),('TORNTPOWER-EQ', '13786', 181.17766848240447),('TATASTEEL-EQ', '3499', -4492.014667323853),('BALKRISIND-EQ', '335', -0.20130441459713747),('POWERGRID-EQ', '14977', 205.27459536697933),('YESBANK-EQ', '11915', 1176855.6544662255),('UBL-EQ', '16713', 0.2327279098137088),('HDFCBANK-EQ', '1333', -102.968061800604),('TATAELXSI-EQ', '3411', -0.8699011670540661),('FEDERALBNK-EQ', '1023', -3202.6817276830056),('APOLLOTYRE-EQ', '163', -366.7955620486356),('ICICIBANK-EQ', '4963', -137.12030797701476),('VOLTAS-EQ', '3718', -15.29748279566683),('LICI-EQ', '9480', 127.6112870012296),('TATACOMM-EQ', '3721', -0.41350827562515047),('COALINDIA-EQ', '20374', 828.6977850193629),('IPCALAB-EQ', '1633', -1.9751633224935985),('LODHA-EQ', '3220', 672.7309176314774),('ADANIPOWER-EQ', '17388', 2680.1480795389384),('PNB-EQ', '10666', -6778.231108098885),('KPITTECH-EQ', '9683', -258.4056421193621),('ASIANPAINT-EQ', '236', -2.5446553687074487),('BANKBARODA-EQ', '4668', -1381.9478213914053),('PERSISTENT-EQ', '18365', 0.41719834687687257),('BANDHANBNK-EQ', '2263', -941.2231402856634),('NAUKRI-EQ', '13751', 1.0595980416142852),('GLAND-EQ', '1186', -6.2734094148949495),('APLAPOLLO-EQ', '25780', 19.321946958726695),('ATGL-EQ', '6066', 2.886442829038697),('CGPOWER-EQ', '760', -55.18283627180589),('ADANIPORTS-EQ', '15083', 327.63011004692606),('CANBK-EQ', '10794', -578.7269968465487),('TVSMOTOR-EQ', '8479', 11.016160639713227),('JSWSTEEL-EQ', '11723', -32.36458321607366),('IOC-EQ', '1624', -4731.516340835793),('CHOLAFIN-EQ', '685', -11.932140374486977),('BAJAJFINSV-EQ', '16675', -8.414076846846443),('DELHIVERY-EQ', '9599', -8.162350215447857),('SRF-EQ', '3273', -3.4683653062565196),('ADANIENSOL-EQ', '10217', -16.634879026727052),('SIEMENS-EQ', '3150', -0.12229266483771521),('JUBLFOOD-EQ', '18096', -4.895436519501046),('TECHM-EQ', '13538', -21.908904217790827),('CUMMINSIND-EQ', '1901', -9.282737144157224),('EICHERMOT-EQ', '910', -2.875002803193154),('LT-EQ', '11483', -9.27256302238974),('ICICIPRULI-EQ', '18652', 1.0881209629168769),('HCLTECH-EQ', '7229', 28.03479516837704),('CONCOR-EQ', '4749', -22.78270357773579),('MRF-EQ', '2277', -0.000912350261679542),('LTIM-EQ', '17818', -0.6801504147268077),('INDIANB-EQ', '14309', 67.60027674180095),('LALPATHLAB-EQ', '11654', 7.904828565320116),('NTPC-EQ', '11630', -3117.188839462623),('JINDALSTEL-EQ', '6733', -72.25709404679694),('IDFCFIRSTB-EQ', '11184', -11735.648590907258),('HAL-EQ', '2303', 73.24497397710765),('MARICO-EQ', '4067', -24.98309142508981),('SHREECEM-EQ', '3103', -0.06336033840170502),('IDEA-EQ', '14366', 2401708.371466638),('FACT-EQ', '1008', 15.942843899181312),('AWL-EQ', '8110', 609.2008806529474),('ZOMATO-EQ', '5097', 2944.149221443345)]
        sorted_money_money = sorted(money_money, key=lambda x: x[2])
        selected_stocks = sorted_money_money[-10:]

        return selected_stocks
    
    def sell_stretigy(self, stock_token):
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

        if(first_close < first_open):
            # check if first closes below 60% or in lower 60% of candle
            threshhold_60 = (first_high-first_low)*0.6
            if(first_close < threshhold_60):
                check_further_candle = True
            else:
                return None
        else:
            return None

        signal_candle = None

        if(check_further_candle):
            lowest_so_far = 999999
            for i in first_15_min_data:
                lowest_so_far = min(lowest_so_far, i[3]) # i[3] is low of candle
            # check live data 
            realTimeBrokerDAL = BrokerLiveDAL()
            while True:
                candle_data_5_min = realTimeBrokerDAL.get_candle_data()
                lowest_so_far = min(lowest_so_far, candle_data_5_min[2])
                
                # check if any candle close in upper 40%
                live_candle_open = candle_data_5_min[0][1]
                live_candle_high = candle_data_5_min[0][2]
                live_candle_low = candle_data_5_min[0][3]
                live_candle_close = candle_data_5_min[0][4]

                threshhold_40 = (live_candle_high-live_candle_low)*0.4