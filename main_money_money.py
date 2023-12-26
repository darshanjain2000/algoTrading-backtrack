import time
from money_money.Services.MMService import MMService
import threading

def main():
    mm_service = MMService()
    stocks = mm_service.find_stocks_for_trade()
    for st in stocks:
        print(st[0], st[2][0])

    # for indx,i in enumerate(stocks):
    #     mm_service.sell_strategy(i[1],i[2][1])

    #     # t = threading.Thread(target = mm_service.sell_strategy, args= (i[1],i[2][1],), name= i[0]+"sell thread")
    #     # t.daemon = True
    #     # t.start()
            
    stocks_for_live = []
    for i in stocks:
        if(mm_service.get_stock_for_live_else_place_order(i[1],i[2][1])):
            stocks_for_live.append((i[1], min([j[2] for j in i[2][1]]))) # min fo 15 min

    mm_service.init_websocket([i[0] for i in stocks_for_live]) # stocks symbol token

    for stck in stocks_for_live:
        th = threading.Thread(target = mm_service.strategy_on_live_data, args= (stck[0], stck[1],))
        th.daemon = True
        th.start()
        # mm_service.strategy_on_live_data(stck[0], stck[1])

    trades = []
    while True:
        if(len(mm_service.trade) == len(stocks_for_live)):
            mm_service.close_websocket()
            break
        
        # if(0 < len(mm_service.trade) <= 3):
        #     trades.append(mm_service.trade)
        #     print(mm_service.trade)
    print("-----------==========--------------===========--------")
    print(trades)

    while True:
        pass


if __name__ == "__main__":
    main()
