
import pandas as pd
import numpy as np
import plotly.express as px
import datetime
import os
from app import app
import pathlib


# par_dir = os.pardir
# data_path = os.path.join(par_dir, "datasets")
# #data_path = Path(data_path)
# df = pd.read_csv("/Users/pntaganda2/Documents/summner2021/proj/datasets/Daily rainfall in mm.csv")

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()
dfn = pd.read_csv(DATA_PATH.joinpath("Daily rainfall in mm.csv"))


# In[2]:


df["date"]= pd.to_datetime(df[["Year","Month","Day"]])
df["month_year"]= pd.to_datetime(df["date"]).dt.to_period('M')
df.sort_values("date", inplace=True)

#merged.head()


# In[23]:


def monthly_anomalies(station_name):
    dff= df[df["Station_Name"]==station_name]
    Year_month= dff.groupby(["Year","Month"], as_index=False).mean()
    monyhly_av= dff.groupby(["Month"], as_index=False).mean()
    monyhly_av=monyhly_av.rename(columns={"PRECIP": "climatology"})
    monyhly_av=monyhly_av.drop(['Lat', 'Lon','Elev', 'Year','Day'], axis=1)
    merged= Year_month.merge(monyhly_av, on='Month')
    merged["anomalies"]=merged["PRECIP"]-merged["climatology"]
    merged['day'] = 1
    merged["date"]= pd.to_datetime(merged[["Year","Month","day"]])
    #merged["month_year"]= pd.to_datetime(merged["date"]).dt.to_period('M')
    merged["month_year"]=merged.date.dt.strftime('%Y-%m')
    merged["color"]= (merged["anomalies"] > 0).apply(lambda x: 'r' if x else 'b')
    figure= px.bar(merged, x="month_year", y="anomalies", color="color", title="Monthly Precipitation Anomalies",
                   labels={"month_year": "Time(year-month)", 'anomalies': "Anomalies(mm/day)"} )

    return figure


# In[4]:


#json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
#figure= px.bar(merged, x="month_year", y="anomalies", color="color" )

#figure


# In[7]:


year_station=df.loc[(df["Station_Name"]=='KITABI')& (df['Year']== 1980)]


# In[8]:


col_one_list = df['Station_Name'].unique().tolist()


# In[21]:



import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
# Load Data

layout= html.Div([
    html.H1("Rainfall Climatology of Rwanda"),
    dcc.Store(id='intermediate-value'),
    
    html.Label([
        "Stations",
        dcc.Dropdown(
            id= "station_name",
            value="GITEGA",
            searchable=True,
            persistence=True,
            persistence_type='local',
            options=[{"label":c, "value":c}
            for c in col_one_list
                    ] ),
        html.Div(id='graph-container', children=[]),
        dcc.Graph(id='annual_average_graph'),
        dcc.Graph(id='monthly_anomalies')
    ]),
    html.Div([
        #html.H1(children='Hello Dash'),
        html.Div(id='graph-container1', children=[]),
    dcc.Dropdown(
            id= "station_years",
            value="2019",
            searchable=True,
            persistence=True,
            persistence_type='local',
            options=[]
            
                     ), 
     dcc.Graph(id='annual_graph')
        
               
        
    ])

        
])


@app.callback(
    Output(component_id='graph-container', component_property='children'),
    Output(component_id='annual_average_graph', component_property='figure'),
    Output(component_id='monthly_anomalies', component_property='figure'),
    Input(component_id='station_name', component_property='value'))
def update_figure(station):
    
    station_df = df[df["Station_Name"]==station]
    monyhly_av= station_df.groupby(["Month"], as_index=False).mean()
    annual_av= station_df.groupby(["Year"], as_index=False).mean()
    figure=monthly_anomalies(station)
    
    
    
    
    fig=px.bar(
        monyhly_av, x="Month", y="PRECIP",
        title="Monthly Average Precipitation", labels={"Month": "Time(month)", 'PRECIP': "Precipitation(mm/day)"}
    )
    fig_on=px.bar(
        annual_av, x="Year", y="PRECIP",
        title="Annual average precipitation", labels={"Month": "Time(year)", 'PRECIP': "Precipitation(mm/day)"}
    )
#     figure= px.bar(merged, x="Year", y="PRECIP" )

    return dcc.Graph(id='display-map', figure=fig),fig_on,figure
# station callback 
@app.callback( Output(component_id='station_years',component_property='options'),
            Input(component_id='station_name', component_property='value'))

def update_years(years):
    station_df = df[df["Station_Name"]==years]
    list_years=station_df['Year'].unique().tolist()
    station_year= [{'label': i, 'value': i} for i in sorted(list_years)]
    
    return station_year

# annual average (specific year) plot 

@app.callback ( Output(component_id='annual_graph', component_property='figure'),
                Input(component_id='station_name', component_property= 'value'),
                Input(component_id='station_years' , component_property='value'))
def update_newfig(name, yea):
    year_station= df.loc[(df["Station_Name"]==name)& (df['Year']==yea)]
    annual_monthly=year_station.groupby(["Month"], as_index=False).mean()
    figur=px.bar(
    annual_monthly, x="Month", y="PRECIP",
    title="Monthly precipitation", labels={"Month": "Time(month)", 'PRECIP': "Precipitation(mm/day)"})
    
    return figur
    


# In[11]:


def annual_month_average( station_name):
    sta_df= df[df["Station_Name"]==station_name]
    list_years=sta_df['Station_Name'].unique().tolist()
    html.Div([
    html.Div(id='graph-container1', child=[]),
    dcc.Slider(
        id='my-slider',
        min=min(list_years),
        max=max(list_years),
        value=min(list_years),
        marks=[{"label":i, "value":i }
               for i in list_years  ])
        ])
    
    app.callback( Output('graph-container11', 'child'), Input('year', 'value'))
    
    dd_year=sta_df[sta_df["Year"]==value]
    av= dd_year.groupby("Month", as_index=True).mean()
    fig1= px.bar(av, x="Month", y="PRECIP",
        title="Annual Monthly precipitation")
    
    return fig1
    
    
    
    
    
    


# In[ ]:



    

