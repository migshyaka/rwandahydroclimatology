#!/usr/bin/env python
# coding: utf-8
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
from dash.dependencies import Input, Output
import os
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go

from app import app
from app import server
from apps import Maxtemp, mintemp, precipitation

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()
dfi = pd.read_csv(DATA_PATH.joinpath("Daily rainfall in mm.csv"))
dfi_i= dfi.iloc[:, [0, 1, 2]]
dfi_i= dfi_i.drop_duplicates()
dfi_i= gpd.GeoDataFrame(dfi_i, geometry=gpd.points_from_xy(dfi_i.Lon,dfi_i.Lat))
dfi_i= dfi_i.set_crs(epsg=3857)
token='pk.eyJ1IjoibXNoeWFrYTIiLCJhIjoiY2tycXp6ems1MDE1ZzJ0dDU2bmNxdDZrdiJ9.8nRmMg7trZMxCEmJsEOiiQ'

figi = go.Figure(go.Scattermapbox(
    lat= dfi_i.geometry.y,
    lon= dfi_i.geometry.x,
    mode= 'markers',

        marker=go.scattermapbox.Marker(
            size=9
        ),
    text=dfi_i["Station_Name"],
))

figi.update_layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=token,
        bearing=0,
        center=dict(
            lat=-1.96,
            lon=30.06
        ),
        pitch=0,
        zoom=6.8

    ),
    height=700
)



# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "30rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "32rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Rwanda's\nHydroclimatology", className="display-12"),
        html.Hr(),
        html.P(
            "Climatology analyis based on station datasets", className="lead"
        ),

        
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"), 
                dbc.NavLink('Maximum Temperature', href='/apps/Maxtemp',active="exact"),
                dbc.NavLink('Minimum Temperature', href='/apps/mintemp', active="exact"),
                dbc.NavLink('Precipitation', href='/apps/precipitation', active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return html.Div([
            html.H1("Welcome to the Rwanda's Hydroclimatology tool", style={'text-align':'center', 'color': ' dark red'}),
            dcc.Markdown('''
            
            Rwanda's Hydroclimatology tool analyzes hydroclimatology data from the Rwanda Meteorology Agency to provide annual averages, monthly averages, and anomalies. 
            This tool is intended for a wide range of users, including amateur climate enthusiasts, students, researchers, and decision makers.
             Rwanda's Hydroclimatology tool aims to improve the country's climate digital resources and applications. 
             Click on the variable of interest from the left menu to access the hydroclomatology analysis page.
              Each page includes a drop-down menu for selecting the station and year of interest, as well as a graph that can be downloaded. 
              The location of the meteorological station used in the analysis is depicted on the map below.
            '''),
            dcc.Graph(id="map_box",figure=figi),
            html.Footer( "© Copyright Hydroinformatics and Integrated Hydroclimate Research Group.")

        ])

    elif pathname == '/apps/Maxtemp':
        return Maxtemp.layout
    elif pathname == '/apps/mintemp':
        return mintemp.layout
    elif pathname == '/apps/precipitation':
        return precipitation.layout
    else:
        return "404 Page Error! Please choose a link"
if __name__ == '__main__':
    app.run_server(debug=False)
