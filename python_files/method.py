import pandas as pd
import numpy as np
import pickle
from os import path

SW_train = ["707014", "707015", "707016", "707017", "707018"]
SE_train = ["707009", "707011", "707012", "707013", "707028"]
list_status = ['Open', 'Close', 'Any']

def prep_data(file, need_data):
    #Open pre prepared data file
    file.seek(0)
    data_bytes = file.read()
    data_dict = pickle.loads(data_bytes)
    with open(file, 'rb') as f:
        data_dict = pickle.load(f)

    #Make list of doors name
    data_fil = data_dict[SW_train[0]]
    door_list = data_fil[data_fil["Description Clean"] == "Trace recording message"]["NameOfStation"].unique().tolist()

    #Mak the dictionary for the door operations per day and train
    door_dict_day = {}
    for i in [0,1]:
        door_dict_train = {}
        for train, data in data_dict.items():
            day = max(data["DateTime Clean"].dt.day) - 1
            door_dict = {}
            for door in door_list:
                data = data[data["DateTime Clean"].dt.day == day + i]
                df_test = data[data["NameOfStation"] == door].reset_index()
                df_test["Status"] = np.where(df_test.index%2 == 0, 0, 1)
                df_test["Time_diff (sec)"] = (df_test["DateTime Clean"] - df_test["DateTime Clean"].shift(1)).dt.total_seconds()
                door_dict[door] = df_test.drop(columns="level_0")
            door_dict_train[train] = door_dict
        door_dict_day[f"Day {i + 1}"] = door_dict_train
    if need_data is False:
        return door_dict_day
    else: return data_dict

def make_door_op_df(door_op, door_dict_day):
    series_day = {}
    for day, door_dict_train in door_dict_day.items():
        list_series = []
        for train, door_dict in door_dict_train.items():
            dict_series = {}
            dict_series["train_nb"] = str(train)
            for door in door_dict.keys():
                dict_series[door] = len(door_dict[door])
            list_series.append(dict_series)
        series_day[day] = list_series

    df_dict = {}
    for day, series in series_day.items():
        df_fin = pd.DataFrame.from_dict(series)
        df_fin = df_fin[["train_nb"] + door_op]
        df_fin["total"] = df_fin.sum(numeric_only = True, axis=1)
        df_dict[day] = df_fin

    return df_dict

def make_op_df_average(df_dict, fleet):
    """Set fleet to True to see average fleetwide, False to see per train."""
    df_ave = ((df_dict["Day 1"].select_dtypes("number") + df_dict["Day 2"].select_dtypes("number"))/2)
    df_ave.insert(loc=0, column='Train', value=df_dict["Day 2"]["train_nb"])

    if fleet is True:
        df_SW = df_ave[df_ave["Train"].isin(SW_train)].describe().loc[["mean"]]
        df_SE = df_ave[df_ave["Train"].isin(SE_train)].describe().loc[["mean"]]
        df_fleet = pd.concat([df_SW, df_SE]).reset_index()
        df_fleet["index"] = ["SouthWest", "SouthEast"]
        df_fleet_2 = df_fleet.rename(columns={"index":"Fleet"})
        df_fleet_2.head(1).values.tolist()[0][1:-2]

        return df_fleet_2
    else: return df_ave

def make_door_time_df(door_dict_day):
    time_day_dict = {}
    for day, train_data in door_dict_day.items():
        time_train_dict = {}
        for train, door_dict in train_data.items():
            time_door_dict = {}
            for door, data in door_dict.items():
                average_open = data[(data["Status"] == 1) & (data["Time_diff (sec)"]<150)]["Time_diff (sec)"].mean()
                average_close = data[data["Status"] == 0]["Time_diff (sec)"].mean()
                average_door = data["Time_diff (sec)"].mean()
                time_door_dict[door] = {"Open": average_open, "Close": average_close, "Any": average_door}
            time_train_dict[train] = time_door_dict
        time_day_dict[day] = time_train_dict

    return time_day_dict

def make_average_time_df(door_op, time_day_dict, status):

    series_time = {}
    for day, time_dict_train in time_day_dict.items():
        list_series = []
        for train, time_door_dict in time_dict_train.items():
            dict_series_time = {}
            dict_series_time["train_nb"] = str(train)
            for door, data in time_door_dict.items():
                dict_series_time[door] = data[status]
            list_series.append(dict_series_time)
        series_time[day] = list_series

    df_time_dict = {}
    for day, series in series_time.items():
        df_fin = pd.DataFrame.from_dict(series)
        df_fin = df_fin[["train_nb"] + door_op]
        df_fin["total"] = df_fin.mean(numeric_only = True, axis=1)
        df_time_dict[day] = df_fin

    df_ave_time = ((df_time_dict["Day 1"].select_dtypes("number") + df_time_dict["Day 2"].select_dtypes("number"))/2)
    df_ave_time.insert(loc=0, column='Train', value=df_time_dict["Day 2"]["train_nb"])
    return df_time_dict, df_ave_time

def make_door_time_average(door_op, time_day_dict, fleet):
    time_df_dict_ave = {}
    time_fleet_dict = {}
    for status in list_status:
        df = make_average_time_df(door_op, time_day_dict, status)[1].round(decimals=1)
        time_df_dict_ave[status] = df

        if fleet is True:
            df_SW_time = df[df["Train"].isin(SW_train)].describe().loc[["mean"]].round(decimals=1)
            df_SE_time = df[df["Train"].isin(SE_train)].describe().loc[["mean"]].round(decimals=1)
            df_fleet = pd.concat([df_SW_time, df_SE_time]).reset_index()
            df_fleet["index"] = ["SouthWest", "SouthEast"]
            df_fleet_2 = df_fleet.rename(columns={"index":"Fleet"})
            time_fleet_dict[status] = df_fleet_2
    if fleet is True:
        return time_fleet_dict
    else: return time_df_dict_ave

def make_average_btw_station(data_dict):
    train_list = SW_train + SE_train
    average_time_station = {}
    for train in train_list:
        mask = (data_dict[train]["Description Clean"] == "Beacon reader new ASDO data") | (data_dict[train]["Description Clean"] == "Standstill (v<0.2 km/h)") | (data_dict[train]["Description Clean"] =="Operation mode setpoint STATION - Door release is active")
        df_test = data_dict[train][mask]
        df_test["temp"] = df_test["Description Clean"].shift(1)
        df_test["Station"] = (df_test["temp"] == "Beacon reader new ASDO data") & (df_test["Description Clean"] == "Standstill (v<0.2 km/h)")
        df_test.drop(columns="temp", inplace = True)
        time_mean = df_test[df_test["Station"]== True]["Time_between_station"] = (df_test[df_test["Station"]== True]["DateTime Clean"] - df_test[df_test["Station"]== True]["DateTime Clean"].shift(1)).dt.total_seconds()
        average_time_station[train] = time_mean[time_mean<10000].mean()
    return average_time_station

def export_data(pathos, data):

    file_path = path.join(["D:", "Test", data[1] + ".csv"])
    data[0].to_csv(file_path)
    return "Save successfully?"
