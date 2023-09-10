import altair as alt
import math
import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
#import snowflake_utils
from PIL import Image

#im = Image.open("./data/images.png")

st.set_page_config(
     page_title="Netflix viewings",
#     page_icon=im,
     layout="wide",
     initial_sidebar_state="expanded",
)

def data_cleaning(): 
    df= pd.read_csv('data/netflix_titles.csv')
    df = df[df['date_added'].notna()]
#    st.dataframe(df, use_container_width=True)
    df["date_added"] = pd.to_datetime(df["date_added"], format='mixed')
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month
    return df 

def get_variation(values: pd.Series) -> np.float64:
    base = values.iloc[0]  # first element in window iteration
    current = values.iloc[-1]  # last element in window iteration
    return (current - base) if base else 0  # avoid ZeroDivisionError / base 

def pop_last(x): 
    x= x[-3:]
    print(x)
    last=x.pop(2)
    
    return x,last



st.markdown("<h1 style='text-align: center;'>Waterfall Chart</h1>", unsafe_allow_html=True)


df  = data_cleaning()
col = "year_added"
#calculate yoy
vc2 = df[col].value_counts().reset_index().rename(columns = {col : "counts", "index" : col})
vc2 =vc2.sort_values(by=['counts'])
#vc2['percent'] = (vc2['counts']/vc2['counts'].sum())* 100

vc2['yoy']=vc2['count'].pct_change()
print(vc2)

# get the percentage change of type 
df2=df[df['year_added'].isin([2020, 2021])].groupby(['type','year_added'])['show_id'].size().reset_index(name='counts')

print(df2)

x_list,last=pop_last(vc2['counts'].tolist())
y_list,last_amount=pop_last(vc2['count'].tolist())

change= get_variation(df2[df2["type"] == "Movie"]['counts'])
y_list.append(round(change,2))
change2 = get_variation(df2[df2["type"] == "TV Show"]['counts'])
y_list.append(round(change2,2))
y_list.append(0)

x_list = x_list+ ['Movie','TV Show']
x_list.append(last)


x_list=['FY 2019','FY 2020', 'Movie', 'TV Show', 'FY 2021']
print(x_list)
text_list = []
for index, item in enumerate(y_list):
    if item > 1 and index >1 and index != len(y_list) - 1:
        text_list.append(f'+{str(y_list[index])}')
    else:
        text_list.append(str(y_list[index]))


for index, item in enumerate(text_list):
    if item[0] == '+' and index != 0 and index != len(text_list) - 1:
        text_list[index] = '<span style="color:#2ca02c">' + text_list[index] + '</span>'
    elif item[0] == '-' and index != 0 and index != len(text_list) - 1:
        text_list[index] = '<span style="color:#d62728">' + text_list[index] + '</span>'
    if index <= 1 :
        text_list[index] = '<b>' + text_list[index] + '</b>'
    elif index == len(text_list) - 1: 
        text_list[index] = '<b>' + str(last_amount) + '</b>'


fig = go.Figure(go.Waterfall(
    name = "Programs", orientation = "v",
    measure = ["absolute","absolute","relative", "relative", "total"],
    x = x_list,
    y = y_list,
    textposition = "outside",
    text = text_list,
    connector = {"line":{"color":'rgba(0,0,0,0)'}},
))

fig.update_layout(
        title = {'text':'<b>Waterfall chart</b><br><span style="color:#666666">Netflix market growth from 2019 to 2021</span>'},
 #       showlegend = True
)

st.plotly_chart(fig, use_container_width=True)