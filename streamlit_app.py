import streamlit as st
import pandas as pd
from python_files.method import prep_data, make_door_op_df, make_door_time_average, make_door_time_df, make_op_df_average, make_average_btw_station, make_average_time_df, export_data

#----------Data maker----------------------
SW_train = ["707014", "707015", "707016", "707017", "707018"]
SE_train = ["707009", "707011", "707012", "707013", "707028"]

pass_door = ['DOOR--14', 'DOOR--A2', 'DOOR--23', 'DOOR--A1', 'DOOR--63',
       'DOOR--64', 'DOOR--F2', 'DOOR--F1', 'DOOR--13', 'DOOR--21', 'DOOR--A3',
       'DOOR--F3', 'DOOR--A4', 'DOOR--F4', 'DOOR--62', 'DOOR--61', 'DOOR--22',
       'DOOR--12', 'DOOR--11', 'DOOR--24']
driver_door = ['DOOR--16', 'DOOR--A6', 'DOOR--15','DOOR--A5']

st.title("Class 707 Doors operations")

with st.sidebar:
    st.subheader("File uploader")
    file = st.file_uploader("Select pickle file", type="pickle")
    st.markdown("""Note: In order to accurately portray door ***opening*** time, outliers have been removed. It was suposed that very long times between door operations were because of maintenance or parking.""")
    st.markdown("""Limitations: <ul>
                    <li>Will only be able to process 2 days (48 hours) of data.</li>
                    <li>Will only work with the train numbers provided.</li>
                    </ul>""", unsafe_allow_html=True)

if file is not None:
    @st.cache_data
    def data_maker(file):
        data = prep_data(file, False)
        whole_data = prep_data(file, True)
        door_dict_pass = make_door_op_df(pass_door, data)
        door_dict_drive = make_door_op_df(driver_door, data)
        df_door_fleet = make_op_df_average(door_dict_pass, True)
        df_door_train = make_op_df_average(door_dict_pass, False)
        df_door_fleet_driv = make_op_df_average(door_dict_drive, True)
        df_door_train_driv = make_op_df_average(door_dict_drive, False)

        door_dict_time = make_door_time_df(data)
        df_door_time_fleet = make_door_time_average(pass_door, door_dict_time, True)
        df_door_time_train = make_door_time_average(pass_door, door_dict_time, False)

        dict_station = make_average_btw_station(whole_data)
        df_station = pd.DataFrame([dict_station])

        time_df_dict = {}
        for status in ["Close", "Open", "Any"]:
            print(status)
            time_df = make_average_time_df(pass_door, door_dict_time, status)[0]
            time_df_dict[status] = time_df

        return data, door_dict_pass,door_dict_drive, time_df_dict, df_door_fleet, df_door_train, df_door_fleet_driv,df_door_train_driv , df_door_time_fleet, df_door_time_train, df_station

    data, door_dict_pass,door_dict_drive , time_df_dict, df_door_fleet, df_door_train, df_door_fleet_driv,df_door_train_driv ,  df_door_time_fleet, df_door_time_train, df_station = data_maker(file)

    #---------------------------------------------

    tab1, tab2 = st.tabs(["Fleet view", "Door View"])
    with tab1:
        cola, colb = st.columns(2)
        cola.header("SouthWestern fleet")
        colb.header("SouthEastern Fleet")
        cola.divider()
        colb.divider()
        cola.write("Door Operations counts (daily average)")
        colb.write("Door Operations counts (daily average)")
        ca1 = cola.container()
        ca2 = colb.container()
        ca1col1, ca1col2 = ca1.columns(2)
        ca1col1.metric("Passengers Doors | average", df_door_fleet["total"][0])
        ca1col2.metric("Drivers Doors | average", df_door_fleet_driv["total"][0])
        with ca1col1.expander("Results per trains"):
                st.dataframe(df_door_train[df_door_train["Train"].isin(SW_train)][["Train", "total"]], hide_index=True)
        with ca1col2.expander("Results per trains"):
                st.dataframe(df_door_train_driv[df_door_train_driv["Train"].isin(SW_train)][["Train", "total"]], hide_index=True)

        ca2col1, ca2col2 = ca2.columns(2)
        ca2col1.metric("Passengers Doors | average", df_door_fleet["total"][1])
        ca2col2.metric("Drivers Doors | average", df_door_fleet_driv["total"][1])
        with ca2col1.expander("Results per trains"):
                st.dataframe(df_door_train[df_door_train["Train"].isin(SE_train)][["Train", "total"]], hide_index=True)
        with ca2col2.expander("Results per trains"):
                st.dataframe(df_door_train_driv[df_door_train_driv["Train"].isin(SE_train)][["Train", "total"]], hide_index=True)

        cola.divider()
        colb.divider()
        cola.write("Time between passenger doors Operations")
        colb.write("Time between passenger doors Operations")
        cola.divider()
        colb.divider()

        cola.metric("Average time between any passenger doors operations", f'{df_door_time_fleet["Any"]["total"][0]} s',)
        colb.metric("Average time between any passenger doors operations", f'{df_door_time_fleet["Any"]["total"][1]} s')
        with cola.expander("See for results per trains"):
                st.dataframe(df_door_time_train["Any"][df_door_time_train["Any"]["Train"].isin(SW_train)][["Train", "total"]], hide_index=True)
        with colb.expander("See for results per trains"):
                st.dataframe(df_door_time_train["Any"][df_door_time_train["Any"]["Train"].isin(SE_train)][["Train", "total"]], hide_index=True)

        cola.metric("Average time doors stayed open (daily average)", f'{df_door_time_fleet["Open"]["total"][0]} s')
        colb.metric("Average time doors stayed open (daily average)", f'{df_door_time_fleet["Open"]["total"][1]} s')
        with cola.expander("See for results per trains"):
                st.dataframe(df_door_time_train["Open"][df_door_time_train["Open"]["Train"].isin(SW_train)][["Train", "total"]], hide_index=True)
        with colb.expander("See for results per trains"):
                st.dataframe(df_door_time_train["Open"][df_door_time_train["Open"]["Train"].isin(SE_train)][["Train", "total"]], hide_index=True)

        cola.metric("Average time doors stay closed (daily average)", f'{df_door_time_fleet["Close"]["total"][0]} s')
        colb.metric("Average time doors stay closed (daily average)", f'{df_door_time_fleet["Close"]["total"][1]} s')
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

    with tab2:
        col1, col2, col3 = st.columns(3)
        option_type = col1.selectbox("Type", ("Door operation count", "Time between operation"))
        option_day = col2.selectbox("Day", ("Day 1", "Day 2"))
        if option_type == "Time between operation":
            option_three = col3.selectbox("Operation", ("Open", "Close", "Any"))
            st.dataframe(time_df_dict[option_three][option_day].round(decimals=1), hide_index=True)
            data_exp = [time_df_dict[option_three][option_day].round(decimals=1), f"Door_time_{option_three}_{option_day}"]

        if option_type == "Door operation count":
            option_three = col3.selectbox("Door type", ("Driver Door", "Passenger Door"))
            if option_three == "Passenger Door":
                st.dataframe(door_dict_pass[option_day], hide_index=True)
                data_exp = [door_dict_pass[option_day], f"Door_op_{option_three}_{option_day}"]
            elif option_three == "Driver Door":
                st.dataframe(door_dict_drive[option_day], hide_index=True)
                data_exp = [door_dict_pass[option_day], f"Door_op_{option_three}_{option_day}"]
        #path = st.text_input("Path to save file")
        #to_export = data_exp
        #st.write(path + '\\' + to_export[1])
        #st.button("Export data", on_click=export_data, args=(path, to_export))
