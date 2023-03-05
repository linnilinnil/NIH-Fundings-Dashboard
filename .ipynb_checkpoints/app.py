###    FEB. - MARCH. 2023    ###
###  WRITTEN MY MARLENE LIN  ###
### FOR PIC16B FINAL PROJECT ###

# Creating a data dashboard
# path and os
import os
import pathlib
import re

# dash
import dash
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import datashader as ds, datashader.transfer_functions as tf, numpy as np
#from datashader import spatial

# plotting and df
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import pandas as pd 

# db
import sqlite3

# geo coding
#from geopy import geocoders  

# initialize dash application
app = Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

app.title = "NIH Data Dashboard - Grants and Funding"
server = app.server

# load data
# for now we just read pre-saved file
proj = pd.read_csv("abl-convert.csv").dropna()
years = list(proj["YEAR"].unique()) 
minyr = min(years)
maxyr = max(years)
years = years + ["all"]
months = list(proj["MONTH"].unique()) + ["all"]
funds = list(proj["FUNDING MECHANISM"].unique()) + ["all"]
insts = list(proj["INSTITUTION TYPE"].unique()) + ["all"]

m_access = "pk.eyJ1IjoibGlubmlsIiwiYSI6ImNsZW01bW9vaTBhMjIzdm1sb2V1b25qemcifQ.W5w-j8UQOorI_ZbO2ibrzA"
m_style = "mapbox://styles/linnil/clem66ou8000w01qus6lbbdm9"


app.layout = html.Div(
    id = "root",
    children=[
        html.Div(
            id = 'titles',
            children = [
                html.H1(id = "main-title",children="NIH Analytics"),
                html.P(
                id = "description",
                children=[
                    html.A(
                    "An interactive real-time NIH research project grants & funding web-based dashboard"
                    )
                ],
            ),
            ],
        ),

        html.Div(
            children = [
                html.H2(id = "map-title",children="Project Map"),
                html.P(
                    id = "map-description",
                    children=[
                        html.A(
                        "Projects by locations, award notice date, funding mechanisms, and institutiont types"
                        ),
                    ],
                ),
            ],
        ),

        html.Div(
            id = "select",
            children = [
                dcc.Slider(
                    id="years",
                    min=minyr,
                    max=maxyr,
                    value=minyr,
                    marks={
                                str(year): {
                                    "label": str(year),
                                    "style": {"color": "#7fafdf"},
                                }
                                for year in years
                            },
                ),
                dcc.Slider(
                    id="months",
                    min=1,
                    max=12,
                    value=1,
                    marks={
                                str(mo): {
                                    "label": str(mo),
                                    "style": {"color": "#7fafdf"},
                                }
                                for mo in months
                            },
                ),
                dcc.Dropdown(
                            id='ins-dropdown',
                            options=[{'label':val,'value':val} for val in insts],
                            value='all',
                            style={'width': '20%', 'display': 'inline-block'}
                ),
                dcc.Dropdown(
                            id='type-dropdown',
                            options=[{'label':val,'value':val} for val in funds],
                            value='all',
                            style={'width': '20%', 'display': 'inline-block'}
                ),
            ],
        ),

        html.Div(
            id = "map",
            children = [
                dcc.Graph(
                     id='map-display',
                     figure=dict(
                            layout=dict(
                                mapbox=dict(
                                    layers=[],
                                    accesstoken=m_access,
                                     style=m_style,
                                    center=dict(
                                        lat=38.72490, lon=-95.61446
                                    ),
                                    pitch=0,
                                    zoom=3.5,
                                ),
                                autosize=True,
                            ),
                     ),
                ),
            ]
        )
    ],
)
   


@app.callback(
    Output('map-display', 'figure'),
    Input('years', 'value'),
    Input('months', 'value'),
    Input('ins-dropdown', 'value'),
    Input('type-dropdown', 'value'),
    [State('map-display', 'figure')])
def show_proj(year,mo,inst,fund,figure):
    """
    Display map based on user-selected filters:
                    year, mo: year and month of award notice date,
                    inst: institution type,
                    fund: fundng mechanism,
                    figure: figure handle
                     
    Return: a dict of {data:...,layout:...} to be passed to the map plot's 
            figure argument.  
    """
    if year != "all":
        dat = proj[(proj['AWARD NOTICE DATE'] == year)]
    if inst != "all":
        dat = dat[dat['INSTITUTION TYPE'] == inst]
    if fund != "all":
        dat = dat[dat['FUNDING MECHANISM'] == fund]
    if mo != "all": 
        dat = dat[dat['FUNDING MECHANISM'] == mo]   
    
    if "layout" in figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        lat = 38.72490
        lon = -95.61446
        zoom = 3.5

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=m_access,
            style=m_style,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        dragmode="lasso",
    )


    data = [
        dict(
            lat=dat["LAT"],
            lon=dat["LON"],
            text=dat["FULL_LOC"],
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="white", opacity=0),
        )
    ]
    fig = dict(data=data, layout=layout)
    return fig



if __name__ == "__main__":
    app.run_server(debug=True,host="localhost", port=8000)