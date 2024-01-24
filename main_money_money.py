from money_money.Services.MMService import MMService
import threading

def main():
    mm_service = MMService()
    stocks = mm_service.find_stocks_for_trade()

    print(f"Top 10 negative money_money for date: {mm_service.invoke_date}")
    for st in stocks:
        print(f"{st[0]}({st[1]}) {st[2][0]}")
            
    stocks_for_live = []
    for i in stocks:
        stock_token = i[1]
        stock_name = i[0]
        fifteen_min_data = i[2][1][:-1] #since its 16 min data 9:15 to 9:30

        if(mm_service.get_stock_for_live_else_place_order(stock_token, stock_name, fifteen_min_data)):
            stocks_for_live.append((stock_token, stock_name, min([j[3] for j in fifteen_min_data]))) # min of 15 min

    mm_service.init_websocket([i[0] for i in stocks_for_live]) # stocks symbol token

    for stck in stocks_for_live:
        stock_token = stck[0]
        stock_name = stck[1]
        lowest_so_far =stck[2]
        th = threading.Thread(target = mm_service.strategy_on_live_data, args= (stock_token, stock_name, lowest_so_far,))
        th.daemon = True
        th.start()

    while True:
        mm_executed_trades_tokens = [i['stock_token'] for i in mm_service.trade]
        live_stocks_tokens = [i[0] for i in stocks_for_live]

        if(all(item in mm_executed_trades_tokens for item in live_stocks_tokens)):
            mm_service.close_websocket()
            print("closed websocket\n")
            break


if __name__ == "__main__":
    main()
