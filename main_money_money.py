import time
from money_money.Services.MMService import MMService

def main():
    mm_service = MMService()
    stocks = mm_service.find_stocks_for_trade()
    print(stocks)
    # stocks = [('NTPC-EQ', '11630', -0.6834768175051006), ('AXISBANK-EQ', '5900', -0.2940410031125713), ('ITC-EQ', '1660', -0.23916207737158113), ('POWERGRID-EQ', '14977', -0.08606018366445702), ('ICICIBANK-EQ', '4963', -0.08180192170576304), ('SBIN-EQ', '3045', -0.06705606760516111), ('HEROMOTOCO-EQ', '1348', -0.05026106863897161), ('TECHM-EQ', '13538', -0.03961703616235896), ('BRITANNIA-EQ', '547', -0.03275378692473779), ('EICHERMOT-EQ', '910', -0.02967646230241627)]

    for i in stocks:
        time.sleep(0.5)
        mm_service.sell_strategy(i[1])
        


if __name__ == "__main__":
    main()
