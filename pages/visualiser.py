from urllib.parse import quote
from datetime import datetime

import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app

reposdf = pd.read_hdf('./data/data.h5', 'repos')
available_repositories = reposdf['Name'].unique()

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

""" [Layout] """


layout = html.Div([
    dbc.Nav(
        [
            html.H5('ChangeVisualiser', className='header'),
            dbc.NavItem(dbc.NavLink('Home', href='/home')),
            dbc.NavItem(dbc.NavLink('Extractor', href='/extractor')),
            dbc.NavItem(dbc.NavLink('Visualiser', active=True, href='/visualiser')),
        ],
        pills=True,
        style={
            'background-color': '#333',
            'margin-bottom': '20px',
            'padding': '10px'
        }
    ),

    html.H4('Select a repository to inspect...', className='title'),

    dbc.Row(children=[
        dbc.Col(
            [
                dcc.Dropdown(
                    id='repository_title',
                    options=[{'label': i, 'value': i} for i in available_repositories],
                    value=available_repositories[0],
                    placeholder='Select a Repository to Visualize...'
                ),
                html.A(
                    'Download Data',
                    id='download-link',
                    download="rawdata.csv",
                    href="",
                    target="_blank"
                ),
            ]),
        dbc.Col(
            [
                html.Div(id='table', children=[
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Files:")),
                            dbc.Col(html.Div(id='no_of_files')),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Total Change (LOC):")),
                            dbc.Col(html.Div(id='total_changes')),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div("Change(%) in Top 20% of Files:")),
                            dbc.Col(html.Div(id='percent')),
                        ]
                    ),
                ]),
            ]),
    ]),

    html.Div(id='paretos-value', style={'display': 'none'}),

    dbc.Row(className='top', children=[
        dbc.Col(
            [
                dcc.Graph(id='line_chart', clear_on_unhover=True),
            ]),
        dbc.Col(
            [
                dcc.Graph(id='file_chart_hover', clear_on_unhover=True),
            ]),
    ]),

    dbc.Row(
        [
            dbc.Col(html.Div(id='filemonth1')),
            dbc.Col(html.Div(id='filemonth2')),
            dbc.Col(html.Div(id='filemonth3')),
        ]
    ),
])


""" [Callbacks] """


@app.callback(
    Output('repository_title', 'options'),
    [Input('repository_title', 'value')])
def update_dropdown(repotitle):
    repos = pd.read_hdf('./data/data.h5', 'repos')
    available_repos = repos['Name'].unique()
    return [{'label': i, 'value': i} for i in available_repos]


@app.callback([
    Output('no_of_files', 'children'),
    Output('total_changes', 'children'),
    Output('percent', 'children')
    ],
    [Input('repository_title', 'value')])
def update_table(repotitle):
    if repotitle is None:
        raise dash.exceptions.PreventUpdate
    else:
        df = pd.read_hdf('./data/data.h5', repotitle)
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
    [Input('repository_title', 'value'),
     Input('file_chart_hover', 'hoverData')])
def update_linechart(repotitle, hoverData):
    if repotitle is None:
        raise dash.exceptions.PreventUpdate
    else:
        df = pd.read_hdf('./data/data.h5', repotitle)

        if hoverData is not None:
            df = df.loc[df['Filename'] == hoverData['points'][0]['x']]
            title = "LOC Changes p/month: " + hoverData['points'][0]['x']
        else:
            title = "LOC Changes p/month [Shift+Click points to Compare Below]"

        df['Date'] = pd.to_datetime(df['Date'])
        df.index = df['Date']
        df = df.resample('M').sum()
        columns = ['Total']
        df = df.replace(0, np.nan).dropna(axis=0, how='any', subset=columns).fillna(0).astype(int)
        timestamps = df.index.tolist()
        dates = []
        for timestamp in timestamps:
            date = timestamp.to_pydatetime()
            date = date.replace(day=1)
            dates.append(date)

        totals = df['Total'].tolist()
        adds = df['Additions'].tolist()
        dels = df['Deletions'].tolist()
        return createlinechart(dates, totals, adds, dels, title)


@app.callback(
    Output('file_chart_hover', 'figure'),
    [Input('line_chart', 'hoverData'),
     Input('repository_title', 'value')])
def update_file_chart_hover(hoverData, repotitle):
    if repotitle is None:
        raise dash.exceptions.PreventUpdate
    else:
        df = pd.read_hdf('./data/data.h5', repotitle)

        if hoverData is not None:
            month = hoverData['points'][0]['x']
            df['Date'] = df.Date.astype(str)
            df = df.loc[df['Date'] == month]
            month = month[:-3]
        else:
            month = "Full Lifecycle"

        df = df.groupby("Filename").sum()
        df = df.sort_values(by=['Filename'], ascending=True)

        filenames = df.index.tolist()
        filetotals = df['Total'].tolist()

        return createfilecharthover(filenames, filetotals, month)


@app.callback([
    Output('filemonth1', 'children'),
    Output('filemonth2', 'children'),
    Output('filemonth3', 'children')
    ],
    [Input('repository_title', 'value'),
     Input('line_chart', 'selectedData')])
def update_file_charts(repotitle, selectedData):
    if selectedData is None:
        return "", "", ""
    else:
        df = pd.read_hdf('./data/data.h5', repotitle)
        points = len(selectedData['points'])
        months = []

        for x in range(points):
            month = selectedData['points'][x]['x']
            months.append(get_month_data(df, month))

        if points >= 3:
            return createfilechart(months[0]), \
                   createfilechart(months[1]), \
                   createfilechart(months[2])
        elif points == 2:
            return createfilechart(months[0]), \
                   createfilechart(months[1]), \
                   ""
        elif points == 1:
            return createfilechart(months[0]), "", ""


@app.callback(
    dash.dependencies.Output('download-link', 'href'),
    [Input('repository_title', 'value')])
def update_download_link(repotitle):
    df = pd.read_hdf('./data/data.h5', repotitle)
    csv_string = df.to_csv(index=True, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)
    return csv_string


""" [functions] """


def createlinechart(dates, totals, adds, dels, title):
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
            'title': title,
            'clickmode': 'event+select',
            'hovermode': 'closest',
            'hovermode': 'x',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': 'black'},
            'margin': dict(b=100),
        }
    }


def createfilecharthover(filenames, filetotals, title):
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
            'title': 'Greatest Change (File level): ' + title,
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': 'black'},
            'margin': dict(
                b=100
            ),
        }
    }


def createfilechart(data):
    return [
        dcc.Graph(
            id='filechartmonth',
            figure={
                'data': [
                    {
                        'x': data[0],
                        'y': data[1],
                        'type': 'bar',
                        'name': 'Total',
                    },
                ],
                'layout': {
                    'title': 'Greatest Change (File level): ' + data[2],
                    'paper_bgcolor': 'rgba(0,0,0,0)',
                    'plot_bgcolor': 'rgba(0,0,0,0)',
                    'font': {'color': 'black'},
                    'margin': dict(
                        b=100
                    ),
                }
            }
        ),
    ]


def get_layout():
    return {
        'layout': {
            'font': {'color': 'black'},
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
        }
    }


def get_month_data(df, month):
    df['Date'] = df.Date.astype(str)
    df = df.loc[df['Date'] == month]
    month = month[:-3]
    df = df.groupby("Filename").sum()
    df = df.sort_values(by=['Total'], ascending=False)
    filenames = df.index.tolist()
    filetotals = df['Total'].tolist()
    del filenames[10:]
    del filetotals[10:]

    return filenames, filetotals, month
