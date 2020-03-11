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
    dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink('Home', href='/apps/home')),
            dbc.NavItem(dbc.NavLink('Extractor', href='/apps/extractor')),
            dbc.NavItem(dbc.NavLink('Visualizer', active=True, href='/apps/visualizer')),
        ],
        pills=True,
        style={
            'background-color': '#333',
            'margin-bottom': '20px',
            'padding': '10px'
        }
    ),

    html.H4('Select a repository to inspect...', className='title'),
    dcc.Dropdown(
        id='repositorytitle',
        options=[{'label': i, 'value': i} for i in available_repositories],
        value=available_repositories[0],
        placeholder='Select a Repository to Visualize...'
    ),

    # dcc.Graph(id='linechart'),

    dbc.Row(className='top', children=[
        dbc.Col(dcc.Graph(id='linechart')),
        dbc.Col(dcc.Graph(id='filecharthover')),
    ]),

    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='filechartinterval')),
            dbc.Col(dcc.Graph(id='filechartinterval2')),
            dbc.Col(dcc.Graph(id='filechartinterval3')),
        ]
    ),

    # dcc.Graph(id='filechart'),
    html.Div(className='footer', children=[html.A('GitHub', href='https://github.com/CiaranCarroll1/FYP')]),
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
            'title': 'Line Changes per Month (Click point to update Chart to Right)',
            'clickmode': 'event+select',
            # "plot_bgcolor": "rgb(0, 0, 0)",
            'paper_bgcolor': 'rgba(0,0,0,0)',
            # 'height': 400
        }
    }


def createfilechart(filenames, filetotals, title):
    return {
        'data': [
            {
                'x': filenames,
                'y': filetotals,
                'type': 'bar',
                'name': 'Total',
            },
        ],
        'layout': {
            'title': 'Files with Greatest Line Changes: ' + title,
            'paper_bgcolor': 'rgba(0,0,0,0)',
            # 'margin': dict(b=100)
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
    del filenames[20:]
    del filetotals[20:]
    del fileadds[20:]
    del filedels[20:]
    return createfilechart(filenames, filetotals, fileadds, filedels, title)


@app.callback([
    Output('filechartinterval', 'figure'),
    Output('filechartinterval2', 'figure'),
    Output('filechartinterval3', 'figure')],
    [Input('linechart', 'clickData'),
     Input('repositorytitle', 'value')])
def updatefilechart(clickData, repotitle):
    df = pd.read_csv("./repositories/" + repotitle + ".csv")
    if clickData is not None:
        month = clickData['points'][0]['x']
        df = df.loc[df['Date'] == month]
        month = month[:-3]
    else:
        months = df['Date'].tolist()
        month = months[len(months) - 1]
        df = df.loc[df['Date'] == month]
        month = month[:-3]
    df = df.groupby("Filename").sum()
    df = df.sort_values(by=['Total'], ascending=False)
    filenames = df.index.tolist()
    filetotals = df['Total'].tolist()
    del filenames[10:]
    del filetotals[10:]
    return createfilechart(filenames, filetotals, month), createfilechart(filenames, filetotals,
                                                                          month), createfilechart(filenames, filetotals,
                                                                                                  month)


@app.callback(
    Output('filecharthover', 'figure'),
    [Input('linechart', 'hoverData'),
     Input('repositorytitle', 'value')])
def updatefilechart(hoverData, repotitle):
    df = pd.read_csv("./repositories/" + repotitle + ".csv")
    if hoverData is not None:
        month = hoverData['points'][0]['x']
        df = df.loc[df['Date'] == month]
        month = month[:-3]
    else:
        months = df['Date'].tolist()
        month = months[len(months) - 1]
        df = df.loc[df['Date'] == month]
        month = month[:-3]
    df = df.groupby("Filename").sum()
    df = df.sort_values(by=['Total'], ascending=False)
    filenames = df.index.tolist()
    filetotals = df['Total'].tolist()
    del filenames[10:]
    del filetotals[10:]
    return createfilechart(filenames, filetotals, month)
