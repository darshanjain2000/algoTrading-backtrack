import os
import pandas as pd
import json

def check_files_by_name():
    source_folder = "clean data"
    destination_folder = "clean data/15min"

    file_names_src = os.listdir(source_folder)
    print(file_names_src)
    source_name = set(file_names_src)
    print(len(source_name))

    print("----")

    file_names_dst = os.listdir(destination_folder)
    print(file_names_dst)
    destination_name = set(file_names_dst)
    print(len(destination_name))

    print(source_name-destination_name)

def get_len():
    source_folder = "clean data"
    file_names_src = os.listdir(source_folder)
    file_names_src.remove('15min')

    for i in file_names_src:
        df = pd.read_csv(f"clean data/{i}")
        df2 = pd.read_csv(f"data/DATA-20230919T111938Z-002/DATA/NF_200/big_data/{i}")
        print(i,len(df2)-len(df))

def check_first_date():
    file_names_src = os.listdir("clean data")
    file_names_src.remove('15min')

    array = []
    kvp = {}

    for i in file_names_src:
        df = pd.read_csv(f"clean data/{i}")
        array.append(df.iloc[0]["datetime"].split(" ")[0])

        if(kvp.get(df.iloc[0]["datetime"].split(" ")[0])==None):
            kvp[df.iloc[0]["datetime"].split(" ")[0]] = [i]
        else:
            kvp[df.iloc[0]["datetime"].split(" ")[0]].append(i)

    print(set(array))
    print("----------------")
    print(kvp)

# sorted start dates ['2017-07-03', '2017-07-04', '2017-07-05', '2017-07-06', '2017-07-07', '2017-07-11', '2017-07-12', '2017-07-14', '2017-07-24', '2017-07-25', '2017-07-26', '2017-08-09', '2017-08-11', '2017-09-07', '2017-09-19', '2017-10-04', '2017-11-08', '2017-11-20', '2018-03-06', '2018-03-28', '2018-04-02', '2018-04-05', '2018-07-02', '2018-08-07', '2018-08-08', '2019-02-07', '2019-04-18', '2019-07-05', '2019-10-15', '2020-01-23', '2020-03-17', '2020-10-28', '2020-11-23', '2021-01-13', '2021-02-02', '2021-06-25', '2021-11-08']
def daily_sorted_stock_diff():
    path = "clean data/1day"
    stocks = os.listdir(path)

    dataset = {}
    for i in stocks:
        df = pd.read_csv(f"{path}/{i}")
        for j in range(1,len(df)):

            if(dataset.get(df.iloc[j]["datetime"])==None):
                dataset[df.iloc[j]["datetime"]] = [(i.split(".")[0],df.iloc[j]["diff percent"])]
            else:
                dataset[df.iloc[j]["datetime"]].append((i.split(".")[0],df.iloc[j]["diff percent"]))

        print("done", i)
    print("DONE")
    print(dataset)

    sorted_date_dict = dict(sorted(dataset.items(), key=lambda item: item[0]))

    with open("daily_sorted_stock_diff.json", "w") as outfile:
        json.dump(sorted_date_dict, outfile)

def sort_daily_diff():
    f = open('daily_sorted_stock_diff.json')
    data = json.load(f)
    for i in data:
        sorted_list = sorted(data[i], key=lambda x: x[1])
        print(sorted_list)
        data[i] = sorted_list

    with open("daily_sorted_stock_diff_sorted.json", "w") as json_file:
        json.dump(data, json_file)