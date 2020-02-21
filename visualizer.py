import json
from textwrap import dedent as d

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

reposdf = pd.read_csv("./repos.csv")
available_repositories = reposdf['Name'].unique()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div(children=[
    html.H1(children='Change Data Visualization'),

    html.Div(children='''
        Select a Repository to Visualize.
    '''),

    dcc.Dropdown(
        id='repositorytitle',
        options=[{'label': i, 'value': i} for i in available_repositories],
        value=available_repositories[0]
    ),


    dcc.Graph(id='linechart'),

    html.Div([
        html.Div([
            dcc.Graph(id='filechart')
        ], className="six columns"),

        html.Div([
            dcc.Graph(id='filechartinterval')
        ], className="six columns"),
    ], className="row"),


    html.Div(className='row', children=[
        html.Div([
            dcc.Markdown(d("""
                    **Click Data**

                    Click on points in the graph.
                """)),
            html.Pre(id='click-data', style=styles['pre']),
        ], className='three columns'),

        html.Div([
            dcc.Markdown(d("""
                **Selection Data**

                Choose the lasso or rectangle tool in the graph's menu
                bar and then select points in the graph.

                Note that if `layout.clickmode = 'event+select'`, selection data also 
                accumulates (or un-accumulates) selected data if you hold down the shift
                button while clicking.
            """)),
            html.Pre(id='selected-data', style=styles['pre']),
        ], className='three columns'),
    ]),

    html.Div(),
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
            'title': 'Change over time',
            'clickmode': 'event+select'
        }
    }

def createfilechart(filenames, filetotals, fileadds, filedels, title):
    return {
        'data': [
            {
                'y': filenames,
                'x': filetotals,
                'type': 'bar',
                'name': 'Total',
                'orientation': 'h'
            },
            {
                'y': filenames,
                'x': fileadds,
                'type': 'bar',
                'name': 'Additions',
                'orientation': 'h'
            },
            {
                'y': filenames,
                'x': filedels,
                'type': 'bar',
                'name': 'Deletions',
                'orientation': 'h'
            },
        ],
        'layout': {
            'title': 'Files with Greatest Total Change: ' + title,
            'margin': dict(
                l=200,
                r=10,
                b=100,
                t=100,
                pad=4
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
    del filenames[20:]
    del filetotals[20:]
    del fileadds[20:]
    del filedels[20:]
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

@app.callback(
    Output('click-data', 'children'),
    [Input('linechart', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)

@app.callback(
    Output('selected-data', 'children'),
    [Input('linechart', 'selectedData')])
def display_selected_data(selectedData):
    return json.dumps(selectedData, indent=2)

if __name__ == '__main__':
    app.run_server(debug=True)
