import pandas as pd
import mplfinance as mpf

df = pd.read_csv('bollinger on data set/csv data/2022/bollinger values/CHOLAFIN.csv', parse_dates=True, index_col='datetime')
specific_date = '2022-01-05'
specific_date_data = df[df.index.date == pd.to_datetime(specific_date).date()]

# Create mplfinance plot
fig, axes = mpf.plot(specific_date_data, type='candle', title=f'{specific_date} OHLC with Bollinger Bands',
                     ylabel='Price', volume=True, style='yahoo',
                     addplot=[
                         mpf.make_addplot(specific_date_data['upper_band'], color='g'),
                         mpf.make_addplot(specific_date_data['lower_band'], color='r')
                     ],
                     panel_ratios=(6, 2),
                     figsize=(12, 8))

# %% 
mpf.show()
