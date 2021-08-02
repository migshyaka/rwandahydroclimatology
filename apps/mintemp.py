#!/usr/bin/env python
# coding: utf-8

# In[2]:


# importing libraries 
import pandas as pd
import numpy as np 
import plotly.express as px
import datetime
import json as simplejson
import os
from app import app


# In[ ]:


# reading the dataset
# par_dir = os.pardir
# data_path = os.path.join(par_dir, "datasets")
# #data_path = Path(data_path)
# dfn = pd.read_csv("/Users/pntaganda2/Documents/summner2021/proj/datasets/Minimum temperature.csv")

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()
dfn = pd.read_csv(DATA_PATH.joinpath("Minimum temperature.csv"))


#pre-processing( adding date column to the dataframe)
dfn["date"]= pd.to_datetime(dfn[["Year","Month","Day"]])
dfn["month_year"]= pd.to_datetime(dfn["date"]).dt.to_period('M')
dfn.sort_values("date", inplace=True)
year_stationn=dfn.loc[(dfn["Station_Name"]=='KITABI')& (dfn['Year']== 1980)]
col_one_listn = dfn['Station_Name'].unique().tolist()

# creating a fuction for monthly anomalies

def monthly_anomaliesn(station_name):
    dff= dfn[dfn["Station_Name"]==station_name]
    Year_month= dff.groupby(["Year","Month"], as_index=False).mean()
    monyhly_av= dff.groupby(["Month"], as_index=False).mean()
    monyhly_av=monyhly_av.rename(columns={"TMPMIN": "climatology"})
    monyhly_av=monyhly_av.drop(['Lat', 'Lon','Elev', 'Year','Day'], axis=1)
    merged= Year_month.merge(monyhly_av, on='Month')
    merged["anomalies"]=merged["TMPMIN"]-merged["climatology"]
    merged['day'] = 1
    merged["date"]= pd.to_datetime(merged[["Year","Month","day"]])
    #merged["month_year"]= pd.to_datetime(merged["date"]).dt.to_period('M')
    merged["month_year"]=merged.date.dt.strftime('%Y-%m')
    merged["color"]= (merged["anomalies"] > 0).apply(lambda x: 'r' if x else 'b')
    figuren= px.bar(merged, x="month_year", y="anomalies", color="color", title="Monthly Minimum Temperature Anomalies",
                   labels={"month_year": "Time(year-month)", 'anomalies': "Anomalies(℃)"} )

    return figuren


# In[20]:


# webapp
 # importing libraries
#from jupyter_dash import JupyterDash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
# Load Data

layout= html.Div([
    html.H1("Minimum Temperature Climatology of Rwanda"),
    dcc.Store(id='intermediate-value'),
    
    html.Label([
        "Stations",
        dcc.Dropdown(
            id= "station_namen",
            value="KITABI",
            searchable=True,
            options=[{"label":c, "value":c}
            for c in col_one_listn
                    ] ),
        html.Div(id='graph-containern', children=[]),
        dcc.Graph(id='annual_average_graphn'),
        dcc.Graph(id='monthly_anomaliesn')
    ]),
    html.Div([
        #html.H1(children='Hello Dash'),
        html.Div(id='graph-container1n', children=[]),
    dcc.Dropdown(
            id= "station_yearsn",
            persistence=True,
            persistence_type='local',
            value="2019",
            searchable=True,
            options=[]
            
                     ), 
     dcc.Graph(id='annual_graphn')
        
               
        
    ])

        
])


@app.callback(
    Output(component_id='graph-containern', component_property='children'),
    Output(component_id='annual_average_graphn', component_property= 'figure'),
    Output(component_id='monthly_anomaliesn', component_property='figure'),
    Input(component_id='station_namen', component_property='value'))
def update_figuren(station):
    
    station_df = dfn[dfn["Station_Name"]==station]
    monyhly_av= station_df.groupby(["Month"], as_index=False).mean()
    annual_av= station_df.groupby(["Year"], as_index=False).mean()
    figuren=monthly_anomaliesn(station)
    
    
    
    
    fign=px.bar(
        monyhly_av, x="Month", y="TMPMIN",
        title="Monthly Average Minimum Temperature", labels={"Month": "Time(month)", 'TMPMIN': "Min Temperature(℃)"}
    )
    fig_onn=px.bar(
        annual_av, x="Year", y="TMPMIN",
        title="Annual average Minimum Temperature", labels={"Month": "Time(year)", 'TMPMIN': "Min Temperature(℃)"}
    )
#     figure= px.bar(merged, x="Year", y="PRECIP" )

    return dcc.Graph(id='display-mapn', figure=fign),fig_onn,figuren
# station callback 
@app.callback( Output(component_id='station_yearsn', component_property='options'),
            Input(component_id='station_namen', component_property= 'value'))

def update_yearsn(years):
    station_dfn = dfn[dfn["Station_Name"]==years]
    list_years=station_dfn['Year'].unique().tolist()
    station_yearn= [{'label': i, 'value': i} for i in sorted(list_years)]
    
    return station_yearn

# annual average (specific year) plot 

@app.callback ( Output(component_id='annual_graphn', component_property='figure'),
                Input(component_id='station_namen', component_property='value'),
                Input(component_id='station_yearsn', component_property='value'))
def update_newfign(name, yea):
    year_station= dfn.loc[(dfn["Station_Name"]==name)& (dfn['Year']==yea)]
    annual_monthly=year_station.groupby(["Month"], as_index=False).mean()
    figurn=px.bar(
    annual_monthly, x="Month", y="TMPMIN",
    title="Monthly Minimum Temperature", labels={"Month": "Time(month)", 'TMPMIN': "Min Temperature(℃)"})
    
    return figurn
    



# In[ ]:




