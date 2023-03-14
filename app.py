#------------------------------------------------------ DATA IMPORT ------------------------------------------------------ 


#importing the necessary components
import dash
import json
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

app = dash.Dash(__name__)

server = app.server
#------------------------------------------------------ DEMO DATA ------------------------------------------------------ 

#host files on github
path = 'https://raw.githubusercontent.com/linnilinnil/NIH-Fundings-Dashboard/main/'

#read in file, for demo purpose they all come from pre-saved csv.
fund_org = pd.read_csv(path + "fund_org_avg.csv")
fund_pi = pd.read_csv(path + "fund_pi_avg.csv")
fund_proj = pd.read_csv(path + "fund_proj_avg.csv")
fatal = pd.read_csv(path+'fatal.csv')
nonfatal = pd.read_csv(path+'nonfatal.csv')
divsum = pd.read_csv(path + 'divsum.csv')
#filter options
years = list(np.arange(2011,2023))
fund_mech = ['All','RPGs - SBIR/STTR', 'RPGs - Non SBIR/STTR',
       'Other Research-Related', 'Training - Individual',
       'Training - Institutional', 'Research Centers', 'Other',
       'Construction']
inst_type = ['All','None', 'Research Institutes', 'Domestic Higher Education',
       'Independent Hospitals']
ind = ["Avg. Funding per PI","Avg. Funding per Org.","Avg. Funding per Project"]

#------------------------------------------------------ CONTROL ------------------------------------------------------ 
#YEAR SLIDER
year_slider = daq.Slider(
        id = 'year_slider',
        handleLabel={"showCurrentValue": True,"label": "Year"},
        value = 2022,
        marks = {str(i):str(i) for i in years},
        min = min(years),
        max = max(years),
        size=450, 
        color='0c4db4'
    )

#FUNDING TYPE
fund_dd = dcc.Dropdown(
        id = 'fund_drop',
        clearable=False, 
        searchable=False, 
        options=[dict(label=fund_mech[i], value=fund_mech[i]) for i in range(len(fund_mech))],
        value='All', 
    )

#INSTITUTE TYPE
inst_dd = dcc.Dropdown(
        id = 'inst_drop',
        clearable=False, 
        searchable=False, 
        options=[dict(label=inst_type[i], value=inst_type[i]) for i in range(len(inst_type))],
        value='All',
    )

map_indice = dcc.Dropdown(
        id='map_idx', 
        className='radio',
        clearable=False, 
        searchable=False, 
        options=[dict(label=ind[i], value=i) for i in range(len(ind))],
        value=2, 
    )

parallel = px.parallel_categories(fatal, dimensions=['exist','est_str','mort_str'],
                color="exist", color_continuous_scale="PuBu",
                labels={'exist':'Category existed time (yr)',
                        'est_str':'Estimated pct. change',
                        'mort_str':'Mortality rate (raw ct.)'}
                )
dimensions=['exist','est_str','mort_bin']
parallel.update_traces(dimensions=[{"categoryorder": "category descending"} for _ in dimensions])

fatal10 = fatal.sort_values('2019 US Mortality 19').iloc[-10:,]
nonfatal10 = nonfatal.sort_values('2019 US Mortality 19').iloc[-10:,]

def get_histo(type,ten):
    area = "Area(M.USD)"
    
    sem = pd.melt(ten, id_vars=['Research/Disease Areas \n (Dollars in millions and rounded)'], 
            value_vars=fatal.columns[1:17],
            var_name='year', value_name='value')
    sem = sem.rename(columns={'2022 Estimated': '2022','2023 Estimated': '2023',
                            'Research/Disease Areas \n (Dollars in millions and rounded)':area})
    sem['value'] = sem['value'].astype(int)
    if type == 'nonfatal':
        up = 800
    else:
        up = 8000
    histo = px.bar(sem, x=area, 
                y="value", color=area,
                title='Top 10 funded '+type+ ' diseases',
                hover_name = area,
                hover_data = [area],
                color_continuous_scale="PuBu",
                animation_frame="year",range_y=[0,up],
                height=600)
    histo.update_layout(showlegend=False)
    histo.update_xaxes(tickangle=60)
    return histo
#histo = get_histo()

def cleanpi(pi):
    pi=pi[pi['ETHNICITY2']!="Unknown"]
    pi=pi[pi['ETHNICITY2']!="Withheld"]

    pi=pi[pi['gender']!="Unknown"]
    pi=pi[pi['gender']!="Withheld"]

    pi=pi[pi['race']!="Unknown"]
    pi=pi[pi['race']!="Withheld"]
    pi=pi[pi['age']!="Unknown"]

    pi['tot_doll']=round(pi['tot_doll'],2)

    cols=["FY","ETHNICITY2","gender","DEGREE","tot_doll","race","age"]
    pi=pi[cols]
    pi = pi.rename(columns={'ETHNICITY2':'hispanic','DEGREE':'degree'})
    return pi

## not reading because this shit is too large lmao
path2 = 'https://raw.githubusercontent.com/linnilinnil/NIH-Fundings-Dashboard/main/'

#pi = pd.read_csv(path2+'pi-organization/pi.csv')
#pi = cleanpi(pi)


def stacked_bar(divsum,par):
    subdiv = divsum.groupby([par,'FY'])['tot_doll'].agg(sum)
    subdiv = subdiv.reset_index(0).reset_index(0)
    subdiv = pd.pivot(subdiv, index='FY', columns=par, values='tot_doll')
    return px.bar(subdiv)

fatal_radio = dbc.RadioItems(
        id='fatal_radio', 
        className='radio',
        options=[dict(label='Fatal', value=0), dict(label='Non-fatal', value=1)],
        value=0, 
        inline=True
    )

div_radio = dbc.RadioItems(
        id='div_radio', 
        className='radio',
        options=[dict(label='Race', value=0), dict(label='Degree', value=1), dict(label='Age', value=2)],
        value=0, 
        inline=True
    )
#------------------------------------------------------ APP LAYOUT ------------------------------------------------------ 

app.layout = html.Div([

    html.Div([
        html.H1(children='NIH FUNDING\n& GRANTS DATA'),
        html.Label(['We are interested in investigating the distributions and usage of NIH Research Project Grants & Fundings. We based our data analysis and visualization on some of the key questions asked by researchers regarding the NIH funding & grants data in this ',
                    html.A('post.',href='https://nexus.od.nih.gov/all/2022/01/18/inequalities-in-the-distribution-of-national-institutes-of-health-research-project-grant-funding/')], 
                    style={'color':'rgb(33 36 35)'})
    ], className='side_bar'),
    html.Br(),
    html.Br(),
    html.Div(children = [
            html.Div([
                        html.Label("Choose the Funding Mechanism:"), 
                        html.Br(),
                        html.Br(),
                        fund_dd,
                    ], className='box', style={'margin': '10px', 'padding-top':'15px', 'padding-bottom':'15px'}),
            html.Div([
                        html.Label("Choose the Institution Type:"), 
                        html.Br(),
                        html.Br(),
                        inst_dd,
                    ], className='box', style={'margin': '10px', 'padding-top':'15px', 'padding-bottom':'15px'}),
            html.Div([
                        html.Label("Choose the average funding indice:"), 
                        html.Br(),
                        html.Br(),
                        map_indice,
                    ], className='box', style={'margin': '10px', 'padding-top':'15px', 'padding-bottom':'15px'}),
            ],className='row',style={'margin-left': '20%','padding-right':0}),
    html.Div([
                html.Div([
                            dcc.Graph(id='map', 
                                    figure = dict(
                                    ),style={'position':'relative'}),
                            html.Div([
                                    html.Label("Choose the fiscal year:"), 
                                    year_slider], 
                                    style={'margin-left':'20%','position':'relative','top':'-30px'},),
                            html.Br(),
                            html.Br(),],
                            className = 'box',
                            style = {'margin-left':"20%",'margin-right':"10%","width":"100%"}),],
                style={'width':'100%'},
                className='row'),
    html.Div([
                html.Div([
                            dcc.Graph(id='parallel', 
                                    figure = parallel)],
                            style={'margin-left':'20%','margin-right':"10%",'width': '100%'},
                            className='box'),],
                className='row'),
    html.Div([
                html.Div([
                            html.Div([
                                      fatal_radio,
                            ]),
                            dcc.Graph(  id='histo', 
                                        figure = dict(),
                                        hoverData={'points': [{'hovertext': 'Cancer '}]},
                                        )],
                            style={'margin-left':'20%','width': '55%'},
                            className='box'),
                html.Div([
                            dcc.Graph(id='hoverline', 
                                    figure = dict(),)],
                            style={'width': '45%',},
                            className='box'),],
                className='row'),
    html.Div([
                html.Div([
                            html.Div([
                                      div_radio,
                            ]),
                            dcc.Graph(  id='stacked', 
                                        )],
                            style={'margin-left':'20%','width': '100%'},
                            className='box'),
                #html.Div([
                 #           dcc.Graph(id='hoverline', 
                  #                  figure = dict(),)],
                   #         style={'width': '45%',},
                    #        className='box'),
                ],
                className='row'),
                
                
])

#------------------------------------------------------ CALLBACK ------------------------------------------------------ 
# helper function to create time series

def draw_line(df, selected):
    area = "Research/Disease Areas \n (Dollars in millions and rounded)"
    sub = df[df[area]== selected]
    sub.rename(columns={'2022 Estimated': '2022','2023 Estimated':'2023'})
    melted = pd.melt(sub, id_vars=[area], 
            value_vars=fatal.columns[1:17],
            var_name='year', value_name='value')
    melted['value'] = melted['value'].astype(int)
    
    fig = px.line(melted,x='year',y='value',title="Change in "+ selected+'\n'+"research fund, M.USD")
    fig.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 1,
            dtick = 1
        )
    )
    return fig

# MAP

@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input(component_id='fund_drop', component_property='value'),
    Input(component_id='inst_drop', component_property='value'),
    Input(component_id='year_slider', component_property='value'),
    Input(component_id='map_idx', component_property='value')]
)
def update_map(fund,inst,yr,idx):
    if idx == 2:
        by_year = fund_proj.copy()
    elif idx == 1:
        by_year = fund_org.copy()
    else:
        by_year = fund_pi.copy()
    if fund != "All":
        by_year = by_year[by_year["FUNDING MECHANISM"]==fund]
    if inst != "All":
        by_year = by_year[by_year["INSTITUTION TYPE"]==inst]

    by_year = by_year[by_year['YEAR']==int(yr)]
    by_year = by_year.groupby(
    ['CODE']
    )['FUNDING'].agg('mean').reset_index(0)


    fig = px.choropleth(by_year,color='FUNDING',
                        locations="CODE", 
                        locationmode="USA-states", 
                        scope="usa",
                        color_continuous_scale="PuBu",
                        range_color=(0, 2*10e5))
    
    return fig

# HIST HOVER
@app.callback(
    [Output('hoverline', 'figure'),
     Output('histo', 'figure'),],
    [Input('histo', 'hoverData'),
     Input('fatal_radio', 'value')
     ])
def update_line(hoverData,val):
    if val == 0:
        df = fatal10
        type = 'fatal'
    else:
        type = 'nonfatal'
        df = nonfatal10
    selected_area = hoverData['points'][0]['hovertext']
    return draw_line(df, selected_area),get_histo(type,df)


# DIST PLOT 
@app.callback(
    Output('stacked', 'figure'),
    Input('div_radio', 'value'))
def update_stack(val):
    #0 race, 1 degree, 2 age
    if val == 0:
       para = 'race'
    elif val == 1:
        para = 'degree'
    else:
        para = 'age'
    return stacked_bar(divsum,para)

if __name__ == '__main__':
    app.run_server(debug=True,port="7001")
if __name__ == '__main__':
    app.run_server(debug=True,port="7001")

