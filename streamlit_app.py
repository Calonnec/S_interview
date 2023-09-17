import streamlit as st
import pandas as pd
import plotly.express as pl
from python_files.method import prep_data, make_door_op_df, make_door_time_average, make_door_time_df, make_op_df_average, make_average_btw_station

#----------Data maker----------------------
SW_train = ["707014", "707015", "707016", "707017", "707018"]
SE_train = ["707009", "707011", "707012", "707013", "707028"]

data = prep_data(False)
whole_data = prep_data(True)
door_dict = make_door_op_df(data)
df_door_fleet = make_op_df_average(door_dict, True)
df_door_train = make_op_df_average(door_dict, False)

door_dict_time = make_door_time_df(data)
df_door_time_fleet = make_door_time_average(door_dict_time, True)
df_door_time_train = make_door_time_average(door_dict_time, False)

dict_station = make_average_btw_station(whole_data)
df_station = pd.DataFrame([dict_station])
#---------------------------------------------

st.title("Class 707 Door operation")
cola, colb = st.columns(2)
cola.header("SouthWestern fleet")
colb.header("SouthEastern Fleet")
cola.divider()
colb.divider()
cola.write("Door Operations counts")
colb.write("Door Operations counts")

cola.metric("Door operation | Mean", df_door_fleet["total"][0])
colb.metric("Door operation | Mean", df_door_fleet["total"][1])
with cola.expander("See for results per trains"):
        st.dataframe(df_door_train[df_door_train["Train"].isin(SW_train)][["Train", "total"]], hide_index=True)
with colb.expander("See for results per trains"):
        st.dataframe(df_door_train[df_door_train["Train"].isin(SE_train)][["Train", "total"]], hide_index=True)

cola.divider()
colb.divider()
cola.write("Time between Door Operations")
colb.write("Time between Door Operations")
cola.divider()
colb.divider()

cola.metric("Avergae time between any door operations | Any", df_door_time_fleet["Any"]["total"][0])
colb.metric("Avergae time between any door operations | Any", df_door_time_fleet["Any"]["total"][1])
with cola.expander("See for results per trains"):
        st.dataframe(df_door_time_train["Any"][df_door_time_train["Any"]["Train"].isin(SW_train)][["Train", "total"]], hide_index=True)
with colb.expander("See for results per trains"):
        st.dataframe(df_door_time_train["Any"][df_door_time_train["Any"]["Train"].isin(SE_train)][["Train", "total"]], hide_index=True)

cola.metric("Avergae time between door openings | Open", df_door_time_fleet["Open"]["total"][0])
colb.metric("Avergae time between door openings | Open", df_door_time_fleet["Open"]["total"][1])
with cola.expander("See for results per trains"):
        st.dataframe(df_door_time_train["Open"][df_door_time_train["Open"]["Train"].isin(SW_train)][["Train", "total"]], hide_index=True)
with colb.expander("See for results per trains"):
        st.dataframe(df_door_time_train["Open"][df_door_time_train["Open"]["Train"].isin(SE_train)][["Train", "total"]], hide_index=True)

cola.metric("Avergae time between door closings | Close", df_door_time_fleet["Close"]["total"][0])
colb.metric("Avergae time between door closings | Close", df_door_time_fleet["Close"]["total"][1])
with cola.expander("See for results per trains"):
        st.dataframe(df_door_time_train["Close"][df_door_time_train["Close"]["Train"].isin(SW_train)][["Train", "total"]], hide_index=True)
with colb.expander("See for results per trains"):
        st.dataframe(df_door_time_train["Close"][df_door_time_train["Close"]["Train"].isin(SE_train)][["Train", "total"]], hide_index=True)

cola.divider()
colb.divider()
cola.write("Estimated time between stations")
colb.write("Estimated time between stations")
cola.divider()
colb.divider()

cola.metric("Average time between stations", df_station.T[df_station.T.index.isin(SW_train)].mean().round(1))
with cola.expander("See for results per trains"):
        st.dataframe(df_station.T[df_station.T.index.isin(SW_train)].round(1).rename(columns={0:"Time"}))
colb.metric("Average time between stations", df_station.T[df_station.T.index.isin(SE_train)].mean().round(1))
with colb.expander("See for results per trains"):
        st.dataframe(df_station.T[df_station.T.index.isin(SE_train)].round(1).rename(columns={0:"Time"}))
