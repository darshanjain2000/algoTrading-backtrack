from money_money.DALS.orderDAL import OrderDAL
from money_money.utils.trade_details import TradeDetails

class OrderService:

    def check_total_positions():
        pass

    def place_sllimit_order(self, trade_details:TradeDetails): 
        order_dal = OrderDAL()
        order_dal.placeSLLimitOrder(trade_details.stock_name, trade_details.stock_token, trade_details.entry, trade_details.stoploss, trade_details.quantity)       
        print({
                    "entry_price":trade_details.entry,
                    "stoploss" : trade_details.stoploss,
                    "quantity" : trade_details.quantity,
                    "stock_token": trade_details.stock_token,
                    "stock_name": trade_details.stock_name,
                    "time triggered": trade_details.trigger_time
                })