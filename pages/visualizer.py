from urllib.parse import quote
import os

import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app

if os.path.exists('./data/data.h5'):
    reposdf = pd.read_hdf('./data/data.h5', 'repos')
    available_repositories = reposdf['Name'].unique()
else:
    available_repositories = []
abstractions = ["File Level", "Folder Level"]

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
            html.H5('ChangeVisualizer', className='header'),
            dbc.NavItem(dbc.NavLink('Home', href='/home')),
            dbc.NavItem(dbc.NavLink('Extractor', href='/extractor')),
            dbc.NavItem(dbc.NavLink('Visualizer', active=True, href='/visualiser')),
        ],
        pills=True,
        style={
            'background-color': '#333',
            'margin-bottom': '20px',
            'padding': '10px'
        }
    ),

    html.Div(id='repos-choice', children=[
        html.Div(id='dropdowns', children=[
            html.H4('Select a Repository and Abstraction to Explore', className='title'),
            dcc.Dropdown(
                id='repository_title',
                options=[{'label': i, 'value': i} for i in available_repositories],
                value=available_repositories[0],
                placeholder='Select Repository...'
            ),
            dcc.Dropdown(
                id='abstraction',
                options=[{'label': i, 'value': i} for i in abstractions],
                value=abstractions[0],
                placeholder='Select Abstraction...'
            ),
            html.Br(),
            html.A(
                'Download Data as CSV',
                id='download-link',
                download="rawdata.csv",
                href="",
                target="_blank"
            ),
        ]),
        html.Div(id='table'),
        html.Div(id='pareto_percents'),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='line_chart', clear_on_unhover=True)),
        dbc.Col(dcc.Graph(id='file_chart_hover', clear_on_unhover=True))
    ]),

    dbc.Row([
        dbc.Col(html.Div(id='filemonth1')),
        dbc.Col(html.Div(id='filemonth2')),
        dbc.Col(html.Div(id='filemonth3')),
    ]),
])


""" [Callbacks] """


@app.callback(
    Output('repository_title', 'options'),
    [Input('repository_title', 'value')])
def update_dropdown(repotitle):
    if os.path.exists('./data/data.h5'):
        repos = pd.read_hdf('./data/data.h5', 'repos')
        available_repos = repos['Name'].unique()
    else:
        available_repos = []
    return [{'label': i, 'value': i} for i in available_repos]


@app.callback([
    Output('table', 'children'),
    Output('pareto_percents', 'children'),
],
    [Input('repository_title', 'value')])
def update_table(repotitle):
    if repotitle is None:
        raise dash.exceptions.PreventUpdate
    else:
        df = pd.read_hdf('./data/data.h5', repotitle)

        df_f = df.groupby("Filename").sum()
        df_f = df_f.sort_values(by=['Total'], ascending=False)
        file_count = df_f['Total'].count()
        change = df_f['Total'].sum()

        df['Filename'] = df['Filename'].str.rsplit("/", 1).str[0]
        df.loc[df['Filename'].str.contains('.', regex=False), 'Filename'] = ''
        df['Filename'] = df['Filename'].astype(str) + '/'
        df_p = df.groupby("Filename").sum()
        df_p = df_p.sort_values(by=['Total'], ascending=False)
        folder_count = df_p['Total'].count()

        stats_1 = ["Folders", "Files", "Change (LOC)"]
        counts_1 = [folder_count, file_count, change]
        data_1 = {'': stats_1, 'Count': counts_1}
        df_1 = pd.DataFrame(data=data_1)

        _20p_files = round(file_count * 0.2)
        file_totals = df_f['Total'].tolist()
        del file_totals[int(_20p_files):]
        change_20p_files = sum(file_totals)
        file_percent = round((change_20p_files / change) * 100)

        stats_2 = ["80% Change (LOC) in 20% Files?"]
        percents_2 = [file_percent]
        data_2 = {'Pareto Principle': stats_2, 'Percent': percents_2}
        df_2 = pd.DataFrame(data=data_2)

        return dbc.Table.from_dataframe(df_1, bordered=True, hover=True, size='sm', style={'border': 'solid'}), \
               dbc.Table.from_dataframe(df_2, bordered=True, hover=True, size='sm', style={'border': 'solid'})


@app.callback(
    Output('line_chart', 'figure'),
    [Input('repository_title', 'value'),
     Input('abstraction', 'value'),
     Input('file_chart_hover', 'hoverData')])
def update_linechart(repotitle, abstraction, hoverData):
    if repotitle is None:
        raise dash.exceptions.PreventUpdate
    else:
        df = pd.read_hdf('./data/data.h5', repotitle)

        if hoverData is not None:
            if abstraction == "Folder Level":
                df['Filename'] = df['Filename'].str.rsplit("/", 1).str[0]
                df.loc[df['Filename'].str.contains('.', regex=False), 'Filename'] = ''
                df['Filename'] = df['Filename'].astype(str) + '/'
            df = df.loc[df['Filename'] == hoverData['points'][0]['x']]
            title = "LOC Change p/month: " + hoverData['points'][0]['x']
        else:
            title = "LOC Change p/month [Shift+Click points to Compare Below]"

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
     Input('abstraction', 'value'),
     Input('repository_title', 'value')])
def update_file_chart_hover(hoverData, abstraction, repotitle):
    if repotitle is None:
        raise dash.exceptions.PreventUpdate
    else:
        df = pd.read_hdf('./data/data.h5', repotitle)

        if abstraction == "Folder Level":
            df['Filename'] = df['Filename'].str.rsplit("/", 1).str[0]
            df.loc[df['Filename'].str.contains('.', regex=False), 'Filename'] = ''
            df['Filename'] = df['Filename'].astype(str) + '/'

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
     Input('abstraction', 'value'),
     Input('line_chart', 'selectedData')])
def update_file_charts(repotitle, abstraction, selectedData):
    if selectedData is None or repotitle is None:
        raise dash.exceptions.PreventUpdate
    else:
        df = pd.read_hdf('./data/data.h5', repotitle)

        if abstraction == "Folder Level":
            df['Filename'] = df['Filename'].str.rsplit("/", 1).str[0]
            df.loc[df['Filename'].str.contains('.', regex=False), 'Filename'] = ''
            df['Filename'] = df['Filename'].astype(str) + '/'

        points = len(selectedData['points'])
        months = []
        fnames = df['Filename'].tolist()

        count = 1
        for i, file_i in enumerate(fnames):
            if not fnames[i][0].isdigit():
                for j, file_j in enumerate(fnames):
                    if file_i == file_j and not i == j:
                        fnames[j] = str(count) + " " + fnames[j]
                fnames[i] = str(count) + " " + fnames[i]
                count += 1
                
        df['Filename'] = fnames

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
    [Input('repository_title', 'value'),
     Input('abstraction', 'value')])
def update_download_link(repotitle, abstraction):
    if repotitle is None:
        raise dash.exceptions.PreventUpdate
    else:
        df = pd.read_hdf('./data/data.h5', repotitle)
        if abstraction == "Folder Level":
            df['Filename'] = df['Filename'].str.rsplit("/", 1).str[0]
            df.loc[df['Filename'].str.contains('.', regex=False), 'Filename'] = ''
            df['Filename'] = df['Filename'].astype(str) + '/'
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
            'title': 'LOC Change p/file: ' + title,
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
                        'x': data[2],
                        'y': data[1],
                        'hovertext': data[0],
                        'type': 'bar',
                        'name': 'Total',
                    },
                ],
                'layout': {
                    'title': 'Greatest Change: ' + data[3],
                    'xaxis': {'type': 'category'},
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
    df = df.groupby(['Filename']).sum()
    df = df.sort_values(by=['Total'], ascending=False)
    filenames = []
    filenumbers = []
    for file in df.index.tolist():
        split = file.split()
        filenames.append(split[1])
        filenumbers.append("(" + split[0] + ")")
    filetotals = df['Total'].tolist()
    del filenames[10:]
    del filenumbers[10:]
    del filetotals[10:]

    return filenames, filetotals, filenumbers, month
