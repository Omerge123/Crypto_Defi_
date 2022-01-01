import pandas as pd
import requests
import json
import numpy as np
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import streamlit as st


text_input = st.empty()
text_input.text("loading and may take up to 2min...")


@st.experimental_memo
def dataset():

    protocols = pd.json_normalize(json.loads(requests.get('https://api.llama.fi/protocols').text))

    flat_list = []
    for sublist in protocols['chains']:
        for item in sublist:
            flat_list.append(item)
        
    chainlist = list(dict.fromkeys(flat_list))

    #chainlist = ['Ethereum','Avalanche','Fantom','Arbitrum','Polygon',]
    
    df       = pd.DataFrame()
    df_chg   = pd.DataFrame()
    df_chart = pd.DataFrame()
    
    for count, x in enumerate(chainlist):
        url = 'https://api.llama.fi/charts/'+ x
        data = pd.json_normalize(json.loads(requests.get(url).text))
        data['date'] = pd.to_datetime(data['date'], unit='s', errors='ignore')
        data['chain'] = x
      
        df = df.append(data, ignore_index=True)
    
        #to take %change separate from accumulate
        try:
       
            data["1day_fix"]      = data['totalLiquidityUSD'].shift(1).tail(1).iloc[0]
            data["1day_fix_Date"] = data['date'].shift(1).tail(1).iloc[0]
            data["1day%"]  = round((((data['totalLiquidityUSD']/data["1day_fix"])-1)*100),2)

            data["7day_fix"]      = data['totalLiquidityUSD'].shift(7).tail(1).iloc[0]
            data["7day_fix_Date"] = data['date'].shift(7).tail(1).iloc[0]
            data["7day%"]  = round((((data['totalLiquidityUSD']/data["7day_fix"])-1)*100),2)
            
            data["3mth_fix"]      = data['totalLiquidityUSD'].shift(90).tail(1).iloc[0]
            data["3mth_fix_Date"] = data['date'].shift(90).tail(1).iloc[0]
            data["3mth%"]  = round((((data['totalLiquidityUSD']/data["3mth_fix"])-1)*100),2)
            
            data["6mth_fix"]      = data['totalLiquidityUSD'].shift(180).tail(1).iloc[0]
            data["6mth_fix_Date"] = data['date'].shift(180).tail(1).iloc[0]          
            data["6mth%"]  = round((((data['totalLiquidityUSD']/data["6mth_fix"])-1)*100),2)
            
            df_chart = df_chart.append(data, ignore_index=True)
        
            data["1day%"]  = round((((data['totalLiquidityUSD']/data['totalLiquidityUSD'].shift(1))-1)*100),2)
            data["7day%"]  = round((((data['totalLiquidityUSD']/data['totalLiquidityUSD'].shift(7))-1)*100),2)
            data["3mth%"]  = round((((data['totalLiquidityUSD']/data['totalLiquidityUSD'].shift(90))-1)*100),2)
            data["6mth%"]  = round((((data['totalLiquidityUSD']/data['totalLiquidityUSD'].shift(180))-1)*100),2)
       
            df_chg = df_chg.append(data.tail(1), ignore_index=True)

        
        except Exception:
            pass
        
                
    return df, df_chg, df_chart, chainlist


data = dataset() 

if data[3] != "":
    text_input.empty()

df       = data[0]    
df_chg   = data[1] 
df_chart = data[2]


####clear cache ###
from streamlit import caching

if str(date.today()) == str(df['date'].max())[:10]:

    print ('ok')
        
else :
   
    caching.clear_cache()
####################################

##############################

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
st.sidebar.markdown("## %Change")
select_event = st.sidebar.selectbox('Selection',options)
text(select_event)
chart(select_event)
chart2(select_event)
