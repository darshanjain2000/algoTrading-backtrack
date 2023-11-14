import requests
import json

url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

nifty200 = ['ABB', 'ACC', 'APLAPOLLO', 'AUBANK', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ADANIPOWER', 'ATGL', 'AWL', 'ABCAPITAL', 'ABFRL', 'ALKEM', 'AMBUJACEM', 'APOLLOHOSP', 'APOLLOTYRE', 'ASHOKLEY', 'ASIANPAINT', 'ASTRAL', 'AUROPHARMA', 'DMART', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BAJAJHLDNG', 'BALKRISIND', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'BATAINDIA', 'BERGEPAINT', 'BDL', 'BEL', 'BHARATFORG', 'BHEL', 'BPCL', 'BHARTIARTL', 'BIOCON', 'BOSCHLTD', 'BRITANNIA', 'CGPOWER', 'CANBK', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'COFORGE', 'COLPAL', 'CONCOR', 'COROMANDEL', 'CROMPTON', 'CUMMINSIND', 'DLF', 'DABUR', 'DALBHARAT', 'DEEPAKNTR', 'DELHIVERY', 'DEVYANI', 'DIVISLAB', 'DIXON', 'LALPATHLAB', 'DRREDDY', 'EICHERMOT', 'ESCORTS', 'NYKAA', 'FEDERALBNK', 'FACT', 'FORTIS', 'GAIL', 'GLAND', 'GODREJCP', 'GODREJPROP', 'GRASIM', 'FLUOROCHEM', 'GUJGASLTD', 'HCLTECH', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE', 'HAVELLS', 'HEROMOTOCO', 'HINDALCO', 'HAL', 'HINDPETRO', 'HINDUNILVR', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'IDFCFIRSTB', 'ITC', 'INDIANB', 'INDHOTEL', 'IOC', 'IRCTC', 'IRFC', 'IGL', 'INDUSTOWER', 'INDUSINDBK', 'NAUKRI', 'INFY', 'INDIGO', 'IPCALAB', 'JSWENERGY', 'JSWSTEEL', 'JINDALSTEL', 'JUBLFOOD', 'KPITTECH', 'KOTAKBANK', 'L&TFH', 'LTTS', 'LICHSGFIN', 'LTIM', 'LT', 'LAURUSLABS', 'LICI', 'LUPIN', 'MRF', 'LODHA', 'M&MFIN', 'M&M', 'MANKIND', 'MARICO', 'MARUTI', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'MSUMI', 'MPHASIS', 'MUTHOOTFIN', 'NHPC', 'NMDC', 'NTPC', 'NAVINFLUOR', 'NESTLEIND', 'OBEROIRLTY', 'ONGC', 'OIL', 'PAYTM', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PIDILITIND', 'PEL', 'POLYCAB', 'POONAWALLA', 'PFC', 'POWERGRID', 'PRESTIGE', 'PGHH', 'PNB', 'RECLTD', 'RVNL', 'RELIANCE', 'SBICARD', 'SBILIFE', 'SRF', 'MOTHERSON', 'SHREECEM', 'SHRIRAMFIN', 'SIEMENS', 'SONACOMS', 'SBIN', 'SAIL', 'SUNPHARMA', 'SUNTV', 'SYNGENE', 'TVSMOTOR', 'TATACHEM', 'TATACOMM', 'TCS', 'TATACONSUM', 'TATAELXSI', 'TATAMTRDVR', 'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TECHM', 'RAMCOCEM', 'TITAN', 'TORNTPHARM', 'TORNTPOWER', 'TRENT', 'TIINDIA', 'UPL', 'ULTRACEMCO', 'UNIONBANK', 'UBL', 'MCDOWELL-N', 'VBL', 'VEDL', 'IDEA', 'VOLTAS', 'WIPRO', 'YESBANK', 'ZEEL', 'ZOMATO', 'ZYDUSLIFE']
nifty200_eq = [i+"-EQ" for i in nifty200]

response = requests.get(url)

if response.status_code == 200:
    data = json.loads(response.text)

    symbol_token_map = {}

    for item in data:
        token = item.get("token")
        symbol = item.get("symbol")
        if token and symbol and item["exch_seg"] == "NSE":
            if(symbol in nifty200_eq):
                symbol_token_map[symbol] = token

    with open("money_money/utils/nifty_200_token_map.json", "w") as outfile: 
        json.dump(symbol_token_map, outfile)
    print(symbol_token_map)

else:
    print("Failed to retrieve data from the URL")