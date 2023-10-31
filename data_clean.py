import pandas as pd
import os


def clean_and_15_all():
    # colab code
    directory_path = "data/DATA-20230919T111938Z-002/DATA/NF_200/big_data"
    if os.path.exists(directory_path):
        file_names = os.listdir(directory_path)

    for i in file_names:
        print(i)
        # if(i.startswith('C')):
        #     clean_data(i)
        #     convert_1min_to_15min(i)
        #     os.remove(f"/content/drive/My Drive/data_stocks/{i}")
        #     print(i,"done")
        clean_data(i)
        convert_1min_to_15min(i)
        os.remove(f"/content/drive/My Drive/data_stocks/{i}")
        print(i,"done")

def clean_data(csv_name):
    df = pd.read_csv(f"data/DATA-20230919T111938Z-002/DATA/NF_200/big_data/{csv_name}")

    unique_dates = set([i.split(" ")[0] for i in df["datetime"]])
    
    dates_to_remove = []

    for trade_date in unique_dates:
        date_data = df[df['datetime'].str.startswith(trade_date)]
        if(len(date_data) != 375):
            dates_to_remove.append(trade_date)

    index_to_remove = []
    for i in range(len(df)):
        if(df.iloc[i]["datetime"].split(" ")[0] in dates_to_remove):
            index_to_remove.append(i)

    # print(index_to_remove)


    df = df.drop(index_to_remove)
    df.to_csv(f"clean data/{csv_name}", index=False)


def convert_1min_to_15min(csv_name):
    # Load the data from the Excel file
    df = pd.read_csv(f"clean data/{csv_name}")

    # Convert the 'datetime' column to datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Set the 'datetime' column as the index
    df.set_index('datetime', inplace=True)

    # Resample the data to 15-minute intervals and aggregate the values
    df_15min = df.resample('15T').agg({
        'symbol': 'first',
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })

    # Reset the index
    # df_15min.reset_index(inplace=True)
    
    # Remove rows with empty values (NaN)
    df_15min.dropna(inplace=True)

    # Save the 15-minute interval data to a new Excel file
    df_15min.to_csv(f"clean data/15min/{csv_name}")

def convert_1min_to_1day(csv_name):
    df = pd.read_csv(f"clean data/{csv_name}")

    # Convert the 'datetime' column to datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Set the 'datetime' column as the index
    df.set_index('datetime', inplace=True)

    # Resample the data to 15-minute intervals and aggregate the values
    df_1day = df.resample('1D').agg({
        'symbol': 'first',
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })

    # Reset the index
    # df_15min.reset_index(inplace=True)
    
    # Remove rows with empty values (NaN)
    df_1day.dropna(inplace=True)

    # Save the 15-minute interval data to a new Excel file
    df_1day.to_csv(f"clean data/1day/{csv_name}")


def add_day_diff():
    source_folder = "clean data/1day"
    file_names_src = os.listdir(source_folder)

    for i in file_names_src:
        diff_arr = [None]
        diff_arr_per = [None]
        df = pd.read_csv(f"clean data/1day/{i}")
        for idx in range(1,len(df)):
            diff_arr.append(df.iloc[idx]["open"] - df.iloc[idx-1]["close"])
            percent_change = ((df.iloc[idx]["open"] - df.iloc[idx-1]["close"])/df.iloc[idx-1]["close"])*100
            diff_arr_per.append(percent_change)

        print("done",i)
        df["diff"] = diff_arr
        df["diff percent"] = diff_arr_per
        df.to_csv(f"clean data/1d/{i}", index=False)
    print("all done")

add_day_diff()