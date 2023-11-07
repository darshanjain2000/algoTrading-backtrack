from datetime import timedelta
import datetime


class daily_scanner:
    def __init__(self, invoke_date, stock):
        self.moving_avg_period = 20
        self.invoke_date = invoke_date
        self.stock = stock

    def get_percentage_change(self):
        yesterday = self.invoke_date - timedelta(days=1)

        today_date_9_29 = datetime.datetime.combine(datetime.date.today(), datetime.time(9, 29))
        change = get_olhcv_by_date_time(self.stock, today_date_9_29).close - get_day_close_by_date(self.stock, yesterday)

        return (change/get_day_close_by_date(self.stock, yesterday))* 100
    
    def get_mm_factor(self):
        first_15_min_volume = get_olhcv_by_datetime_no_of_candle(self.stock, datetime.date.today(),0,15).volume # candle from(0) to(15)
        close_price_list = get_day_close_by_date_range(self.stock, datetime.date.today()-1 ,datetime.date.today()-self.moving_avg_period-1)
        
        return first_15_min_volume/close_price_list.mean()
    
    def money_money_value(self):
        return get_percentage_change() * get_mm_factor()