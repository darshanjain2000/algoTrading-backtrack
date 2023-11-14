from money_money.Services.MMService import MMService

def main():
    mm_service = MMService()
    stocks = mm_service.find_stocks_for_trade()



if __name__ == "__main__":
    main()
