import json
from textwrap import dedent as d
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app

reposdf = pd.read_csv("./repos.csv")
available_repositories = reposdf['Name'].unique()

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

layout = html.Div([
    html.H1('Visualizing Change Data in GitHub Repositories', className='header'),
    html.Nav(className="navbar", children=[
        html.A('Home', href='/apps/home'),
        html.A('Extractor', href='/apps/extractor'),
        html.A('Visualizer', href='/apps/visualizer')
    ]),

    html.H4('Select a repository to inspect...', className='title'),
    dcc.Dropdown(
        id='repositorytitle',
        options=[{'label': i, 'value': i} for i in available_repositories],
        value=available_repositories[0],
        placeholder='Select a Repository to Visualize...'
    ),


    html.Div(className='container', children=[
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='linechart')),
                dbc.Col(dcc.Graph(id='filechart')),
            ]
        ),
    ]),

    dcc.Graph(id='filechartinterval'),
    html.Div(className='footer', children='Footer'),
])

def createlinechart(dates, totals, adds, dels):
    return {
        'data': [
            {
                'x': dates,
                'y': totals,
                'type': 'line',
                'name': 'Total'
            },
            {
                'x': dates,
                'y': adds,
                'type': 'line',
                'name': 'Additions'
            },
            {
                'x': dates,
                'y': dels,
                'type': 'line',
                'name': 'Deletions'
            },
        ],
        'layout': {
            'title': 'Line Changes per Month (Click point to update Graph Below)',
            'clickmode': 'event+select'
        }
    }

def createfilechart(filenames, filetotals, fileadds, filedels, title):
    return {
        'data': [
            {
                'x': filenames,
                'y': filetotals,
                'type': 'bar',
                'name': 'Total',
            },
            {
                'x': filenames,
                'y': fileadds,
                'type': 'bar',
                'name': 'Additions',
            },
            {
                'x': filenames,
                'y': filedels,
                'type': 'bar',
                'name': 'Deletions',
            },
        ],
        'layout': {
            'title': 'Files with Greatest Total Change: ' + title,
            'margin': dict(
                b=100
            )
        }
    }

@app.callback(
    Output('linechart', 'figure'),
    [Input('repositorytitle', 'value')])
def updatelinechart(repotitle):
    df = pd.read_csv("./repositories/" + repotitle + ".csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df.index = df['Date']
    df = df.resample('M').sum()
    timestamps = df.index.tolist()
    dates = []
    for timestamp in timestamps:
        date = timestamp.to_pydatetime()
        date = date.replace(day=1)
        dates.append(date)

    totals = df['Total'].tolist()
    adds = df['Additions'].tolist()
    dels = df['Deletions'].tolist()
    return createlinechart(dates, totals, adds, dels)

@app.callback(
    Output('filechart', 'figure'),
    [Input('repositorytitle', 'value')])
def updatefilechart(repotitle):
    title = "Full lifecycle"
    df = pd.read_csv("./repositories/" + repotitle + ".csv")
    df = df.groupby("Filename").sum()
    df = df.sort_values(by=['Total'], ascending=False)
    filenames = df.index.tolist()
    filetotals = df['Total'].tolist()
    fileadds = df['Additions'].tolist()
    filedels = df['Deletions'].tolist()
    del filenames[10:]
    del filetotals[10:]
    del fileadds[10:]
    del filedels[10:]
    return createfilechart(filenames, filetotals, fileadds, filedels, title)

@app.callback(
    Output('filechartinterval', 'figure'),
    [Input('linechart', 'clickData'),
     Input('repositorytitle', 'value')])
def updatefilechart(clickData, repotitle):
    df = pd.read_csv("./repositories/" + repotitle + ".csv")
    month = "    "
    if clickData is not None:
        month = clickData['points'][0]['x']
        df = df.loc[df['Date'] == month]
        month = month[:-3]
    else:
        months = df['Date'].tolist()
        month = months[0]
        df = df.loc[df['Date'] == month]
        month = month[:-3]
    df = df.groupby("Filename").sum()
    df = df.sort_values(by=['Total'], ascending=False)
    filenames = df.index.tolist()
    filetotals = df['Total'].tolist()
    fileadds = df['Additions'].tolist()
    filedels = df['Deletions'].tolist()
    del filenames[20:]
    del filetotals[20:]
    del fileadds[20:]
    del filedels[20:]
    return createfilechart(filenames, filetotals, fileadds, filedels, month)
