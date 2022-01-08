import pandas as pd
import requests
import json
import numpy as np
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import streamlit as st


##################### Data pull from Google ###################

sheet_id=st.secrets.db_credentials.password

df = "https://docs.google.com/spreadsheets/d/" + sheet_id +  "/gviz/tq?tqx=out:csv&sheet=" +  'df'
df_chg = "https://docs.google.com/spreadsheets/d/" + sheet_id +  "/gviz/tq?tqx=out:csv&sheet=" +  'df_chg'
df_chart = "https://docs.google.com/spreadsheets/d/" + sheet_id +  "/gviz/tq?tqx=out:csv&sheet=" +  'df_chart'

df       = pd.read_csv(df)
df_chg   = pd.read_csv(df_chg)
df_chart = pd.read_csv(df_chart)

#convert date to right format##
df['date']       = pd.to_datetime(df['date'].str[:10], errors='ignore')
df_chg['date']   = pd.to_datetime(df_chg['date'].str[:10], errors='ignore')
df_chart['date'] = pd.to_datetime(df_chart['date'].str[:10], errors='ignore')

df_chart['1day_fix_Date'] = pd.to_datetime(df_chart['1day_fix_Date'].str[:10], errors='ignore')
df_chart['7day_fix_Date'] = pd.to_datetime(df_chart['7day_fix_Date'].str[:10], errors='ignore')
df_chart['3mth_fix_Date'] = pd.to_datetime(df_chart['3mth_fix_Date'].str[:10], errors='ignore')
df_chart['6mth_fix_Date'] = pd.to_datetime(df_chart['6mth_fix_Date'].str[:10], errors='ignore')


today_run_date = df['Today'].iloc[0]

#####################################################################
df_chg2 = df_chg.replace([np.inf, -np.inf], np.nan).fillna(0) 

#column_name = df_chg2.columns.values.tolist()[-4:]
options = ["1day%","7day%", "3mth%", "6mth%"]

def text(x):
    date_filter = x[:-1] + '_fix_Date'

    xy = df_chg2.sort_values(by=[x],ascending=False).head(10).reset_index().filter(['chain',x])
    name = xy['chain'].values.tolist()
    df_chart2 = df_chart[df_chart.chain.isin(name)]

    date = df_chart2[date_filter].iloc[0]
    st.write('Top ' + x + ' change from ' + str(date)[:10] )

def chart(value):
    
    xy = df_chg2.sort_values(by=[value],ascending=False).head(10).reset_index().filter(['chain',value])
    
    y = xy['chain'].values.tolist()
    x = xy[value].values.tolist()
    
    fig = plt.figure(figsize = (10, 5))
    plt.barh(y,x)
    #plt.title(value + 'change')
    plt.ylabel('Chain')
    plt.xlabel('Value(%)')
    st.pyplot(fig)


######chart####
def chart2(value2):
    
    xy = df_chg2.sort_values(by=[value2],ascending=False).head(10).reset_index().filter(['chain',value2])
    name = xy['chain'].values.tolist()
    
    df_chart2 = df_chart[df_chart.chain.isin(name)]

    date_filter = value2[:-1] + '_fix_Date'
    df_chart3 = df_chart2[df_chart2[date_filter]<= df_chart2['date']] 
    df_chart4 = df_chart3.pivot(index='date', columns='chain', values=value2).fillna(0)
    df_chart5 = df_chart4.reset_index(level=0).rename_axis(None, axis=1).set_index("date")

    #df_chart3.plot()
    st.line_chart(data=df_chart5)


# Title the app
#st.title('Defi llama TVL Chain')
st.header('DeFi Llama Total Value Locked (TVL) Chain')



# charts
st.sidebar.markdown(today_run_date)
select_event = st.sidebar.selectbox('Selection',options)
text(select_event)
chart(select_event)
chart2(select_event)
