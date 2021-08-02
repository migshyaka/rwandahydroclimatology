#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# importing libraries 
import pandas as pd
import numpy as np
import plotly.express as px
import datetime
import json as simplejson
import pathlib
import os
from pathlib import Path
from app import app

# reading the dataset
# par_dir = os.pardir
# data_path = os.path.join(par_dir, "../datasets")
# data_path = Path(data_path)
# df = pd.read_csv("../datasets/Maximum temperature.csv")
# df.head()
# PATH = pathlib.Path(__file__).parent
# DATA_PATH = PATH.joinpath("../rwandahydroclimatology/datasets").resolve()
# df = pd.read_csv(DATA_PATH.joinpath("Maximum temperature.csv"))
df = pd.read_csv("rwandahydroclimatology/datasets/Maximum temperature.csv")


# In[7]:


# pre-processing( adding date column to the dataframe)
df["date"] = pd.to_datetime(df[["Year", "Month", "Day"]])
df["month_year"] = pd.to_datetime(df["date"]).dt.to_period('M')
df.sort_values("date", inplace=True)
year_station = df.loc[(df["Station_Name"] == 'KITABI') & (df['Year'] == 1980)]
col_one_list = df['Station_Name'].unique().tolist()


# In[8]:


# creating a fuction for monthly anomalies

def monthly_anomalies(station_name):
    dff = df[df["Station_Name"] == station_name]
    Year_month = dff.groupby(["Year", "Month"], as_index=False).mean()
    monyhly_av = dff.groupby(["Month"], as_index=False).mean()
    monyhly_av = monyhly_av.rename(columns={"TMPMAX": "climatology"})
    monyhly_av = monyhly_av.drop(['Lat', 'Lon', 'Elev', 'Year', 'Day'], axis=1)
    merged = Year_month.merge(monyhly_av, on='Month')
    merged["anomalies"] = merged["TMPMAX"] - merged["climatology"]
    merged['day'] = 1
    merged["date"] = pd.to_datetime(merged[["Year", "Month", "day"]])
    # merged["month_year"]= pd.to_datetime(merged["date"]).dt.to_period('M')
    merged["month_year"] = merged.date.dt.strftime('%Y-%m')
    merged["color"] = (merged["anomalies"] > 0).apply(lambda x: 'r' if x else 'b')
    figure = px.bar(merged, x="month_year", y="anomalies", color="color", title="Monthly Maximum Temperature Anomalies",
                    labels={"month_year": "Time(year-month)", 'anomalies': "Anomalies(℃)"})

    return figure


# In[9]:


# webapp
# importing libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# Load Data
layout = html.Div([
    html.H1("Maximum Temperature Climatology of Rwanda"),
    dcc.Store(id='intermediate-value'),

    html.Label([
        "Stations",
        dcc.Dropdown(
            id="station_namep",
            value="GITEGA",
            searchable=True,
            persistence=True,
            persistence_type='local',
            options=[{"label": c, "value": c}
                     for c in col_one_list
                     ]),
        html.Div(id='graph-containerp', children=[]),
        dcc.Graph(id='annual_average_graphp'),
        dcc.Graph(id='monthly_anomaliesp')
    ]),
    html.Div([
        # html.H1(children='Hello Dash'),
        html.Div(id='graph-container1p', children=[]),
        dcc.Dropdown(
            id="station_yearsp",
            value="2019",
            persistence=True,
            persistence_type='local',
            searchable=True,
            options=[]

        ),
        dcc.Graph(id='annual_graphp')

    ])

])


@app.callback(
    Output(component_id='graph-containerp', component_property='children'),
    Output(component_id='annual_average_graphp',component_property= 'figure'),
    Output(component_id='monthly_anomaliesp', component_property='figure'),
    Input(component_id='station_namep', component_property='value'))
def update_figure(station):
    station_df = df[df["Station_Name"] == station]
    monyhly_av = station_df.groupby(["Month"], as_index=False).mean()
    annual_av = station_df.groupby(["Year"], as_index=False).mean()
    figure = monthly_anomalies(station)

    fig = px.bar(
        monyhly_av, x="Month", y="TMPMAX",
        title="Monthly Average Maximum Temperature", labels={"Month": "Time(month)", 'TMPMAX': "Max Temperature(℃)"}
    )
    fig_on = px.bar(
        annual_av, x="Year", y="TMPMAX",
        title="Annual average Maximum Temperature", labels={"Month": "Time(year)", 'TMPMAX': "Max Temperature(℃)"}
    )
    #     figure= px.bar(merged, x="Year", y="PRECIP" )

    return dcc.Graph(id='display-map', figure=fig), fig_on, figure


# station callback
@app.callback(Output(component_id='station_yearsp', component_property='options'),
              Input(component_id='station_namep',component_property= 'value'))
def update_years(years):
    station_df = df[df["Station_Name"] == years]
    list_years = station_df['Year'].unique().tolist()
    station_year = [{'label': i, 'value': i} for i in sorted(list_years)]

    return station_year


# annual average (specific year) plot

@app.callback(Output(component_id='annual_graphp', component_property='figure'),
              Input(component_id='station_namep', component_property='value'),
              Input(component_id='station_yearsp', component_property='value'))
def update_newfig(name, yea):
    year_station = df.loc[(df["Station_Name"] == name) & (df['Year'] == yea)]
    annual_monthly = year_station.groupby(["Month"], as_index=False).mean()
    figur = px.bar(
        annual_monthly, x="Month", y="TMPMAX",
        title="Monthly Maximum Temperature", labels={"Month": "Time(month)", 'TMPMAX': "Max Temperature(℃)"})

    return figur

