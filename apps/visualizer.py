import json
from urllib.parse import quote

import pandas as pd
import dash
import dash_table
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
    dbc.Nav(
        [
            html.H5('ChangeVisualizer', className='header'),
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
        id='repository_title',
        options=[{'label': i, 'value': i} for i in available_repositories],
        value=available_repositories[0],
        placeholder='Select a Repository to Visualize...'
    ),

    html.Div(id='table', children=[
        dbc.Row(
            [
                dbc.Col(html.Div("No. of Files:")),
                dbc.Col(html.Div(id='no_of_files')),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("Total Line Changes:")),
                dbc.Col(html.Div(id='total_changes')),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(html.Div("% of Change in Top 20% of Files:")),
                dbc.Col(html.Div(id='percent')),
            ]
        ),
    ]),


    dbc.Row(className='top', children=[
        dbc.Col(
            [
                dcc.Graph(id='line_chart', clear_on_unhover=True),
                html.A(
                    'Download Data',
                    id='download-link',
                    download="rawdata.csv",
                    href="",
                    target="_blank"
                )
            ]),
        dbc.Col(
            [
                dcc.Graph(id='file_chart_hover'),
                html.A(
                    'Download Data',
                    id='download-link-2',
                    download="rawdata.csv",
                    href="",
                    target="_blank"
                )
            ]),
    ]),

    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='file_chart_month1')),
            dbc.Col(dcc.Graph(id='file_chart_month2')),
            dbc.Col(dcc.Graph(id='file_chart_month3')),
        ]
    ),
])


def createlinechart(dates, totals, adds, dels):
    return {
        'data': [
            {
                'x': dates,
                'y': totals,
                'mode': 'lines+markers',
                'name': 'Total'
            },
            {
                'x': dates,
                'y': adds,
                'mode': 'lines+markers',
                'name': 'Additions'
            },
            {
                'x': dates,
                'y': dels,
                'mode': 'lines+markers',
                'name': 'Deletions'
            },
        ],
        'layout': {
            'title': 'Line Changes per Month',
            'clickmode': 'event+select',
            'hovermode': 'closest',
            'hovermode': 'x',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': dict(
                b=100
            )
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
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'margin': dict(
                b=100
            )
        }
    }


@app.callback(
    Output('repository_title', 'options'),
    [Input('repository_title', 'value')])
def update_dropdown(repotitle):
    repos = pd.read_csv("./repos.csv")
    available_repos = repos['Name'].unique()
    return [{'label': i, 'value': i} for i in available_repos]


@app.callback([
    Output('no_of_files', 'children'),
    Output('total_changes', 'children'),
    Output('percent', 'children')
    ],
    [Input('repository_title', 'value')])
def update_table(repotitle):
    df = pd.read_csv("./repositories/" + repotitle + ".csv")
    df = df.groupby("Filename").sum()
    df = df.sort_values(by=['Total'], ascending=False)

    nof = df['Total'].count()
    nof_20 = round(df['Total'].count() * 0.2)
    total = df['Total'].sum()
    totals = df['Total'].tolist()
    del totals[int(nof_20):]
    change_80 = sum(totals)
    percent = round((change_80 / total) * 100)

    return nof, total, percent


@app.callback(
    Output('line_chart', 'figure'),
    [Input('repository_title', 'value')])
def update_linechart(repotitle):
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
    Output('file_chart_hover', 'figure'),
    [Input('line_chart', 'hoverData'),
     Input('repository_title', 'value')])
def update_file_chart_hover(hoverData, repotitle):
    df = pd.read_csv("./repositories/" + repotitle + ".csv")
    if hoverData is not None:
        month = hoverData['points'][0]['x']
        df = df.loc[df['Date'] == month]
        month = month[:-3]
        df = df.groupby("Filename").sum()
        df = df.sort_values(by=['Total'], ascending=False)
        nof = 10
    else:
        month = "Entire Project"
        df = df.groupby("Filename").sum()
        df = df.sort_values(by=['Total'], ascending=False)
        nof = int(round(df['Total'].count() * 0.2))
        if nof < 10:
            nof = 10
    filenames = df.index.tolist()
    filetotals = df['Total'].tolist()
    del filenames[nof:]
    del filetotals[nof:]
    return createfilechart(filenames, filetotals, month)


@app.callback([
    Output('file_chart_month1', 'figure'),
    Output('file_chart_month2', 'figure'),
    Output('file_chart_month3', 'figure')
    ],
    [Input('repository_title', 'value'),
     Input('line_chart', 'selectedData')])
def update_file_charts(repotitle, selectedData):
    if selectedData is None:
        return get_layout(), get_layout(), get_layout()
    else:
        df = pd.read_csv("./repositories/" + repotitle + ".csv")
        month1 = selectedData['points'][0]['x']
        month1, filenames1, filetotals1 = get_month_data(df, month1)
        points = len(selectedData['points'])

        if points >= 2:
            month2 = selectedData['points'][1]['x']
            month2, filenames2, filetotals2 = get_month_data(df, month2)

        if points >= 3:
            month3 = selectedData['points'][2]['x']
            month3, filenames3, filetotals3 = get_month_data(df, month3)

        if points >= 3:
            return createfilechart(filenames1, filetotals1, month1), \
                   createfilechart(filenames2, filetotals2, month2), \
                   createfilechart(filenames3, filetotals3, month3)
        elif points == 2:
            return createfilechart(filenames1, filetotals1, month1), \
                   createfilechart(filenames2, filetotals2, month2), \
                   get_layout()
        else:
            return createfilechart(filenames1, filetotals1, month1), get_layout(), get_layout()


def get_layout():
    return {
        'layout': {
            'title': 'Click Line Chart to Update (Shift+Click for Comparisons)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
        }
    }


def get_month_data(df, month):
    df = df.loc[df['Date'] == month]
    month = month[:-3]
    df = df.groupby("Filename").sum()
    df = df.sort_values(by=['Total'], ascending=False)
    filenames = df.index.tolist()
    filetotals = df['Total'].tolist()
    del filenames[10:]
    del filetotals[10:]

    return month, filenames, filetotals


@app.callback(
    dash.dependencies.Output('download-link', 'href'),
    [Input('repository_title', 'value')])
def update_download_link(repotitle):
    df = pd.read_csv("./repositories/" + repotitle + ".csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df.index = df['Date']
    df = df.resample('M').sum()
    csv_string = df.to_csv(index=True, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)
    return csv_string


@app.callback(
    dash.dependencies.Output('download-link-2', 'href'),
    [Input('repository_title', 'value')])
def update_download_link_2(repotitle):
    df = pd.read_csv("./repositories/" + repotitle + ".csv")
    df = df.groupby("Filename").sum()
    df = df.sort_values(by=['Total'], ascending=False)
    csv_string = df.to_csv(index=True, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)
    return csv_string
