import time
from money_money.Services.MMService import MMService
import threading

def main():
    mm_service = MMService()
    stocks = mm_service.find_stocks_for_trade()
    print(stocks)

    for i in stocks:
        # time.sleep(0.5)
        mm_service.sell_strategy(i[1],i[2][1])

        # t = threading.Thread(target = mm_service.sell_strategy, args= (i[1],i[2][1],))
        # t.daemon = True
        # t.start()

    while True:
        if(0 < len(mm_service.trade) <= 3):
            print(mm_service.trade)
        


if __name__ == "__main__":
    main()
