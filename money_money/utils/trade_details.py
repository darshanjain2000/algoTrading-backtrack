class TradeDetails:
    def __init__(self, stock_symbol, stock_token, entry_price, stoploss_price, quantity, trigger_time):
        self.entry = entry_price
        self.stoploss = stoploss_price
        self.quantity = quantity
        self.stock_token = stock_token,
        self.stock_name = stock_symbol,
        self.trigger_time = trigger_time