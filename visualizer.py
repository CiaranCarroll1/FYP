import json
from textwrap import dedent as d

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

df = pd.read_csv("./gothinkster-realworld.csv")
df2 = pd.read_csv("./gothinkster-realworld-files.csv")

dates = df['Date'].tolist()
values = df['Total'].tolist()
adds = df['Additions'].tolist()
dels = df['Deletions'].tolist()
filenames = df2['Filename'].tolist()
filetotals = df2['Changes'].tolist()
del filenames[20:]
del filetotals[20:]

# data = {'Date': dates, 'Additions': adds, 'Deletions': dels, 'Total': values}
# df = pd.DataFrame(data=data)

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
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='basic-interactions',
        figure={
            'data': [
                {
                    'x': dates,
                    'y': values,
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
    ),

    dcc.Graph(
        id='files',
        figure={
            'data': [
                {
                    'x': filenames,
                    'y': filetotals,
                    'type': 'bar',
                    'name': 'Total'
                },
            ],
            'layout': {
                'title': 'File Changes'
            }
        }
    ),

    html.Div(className='row', children=[
        html.Div([
            dcc.Markdown(d("""
                    **Hover Data**

                    Mouse over values in the graph.
                """)),
            html.Pre(id='hover-data', style=styles['pre'])
        ], className='three columns'),

        html.Div([
            dcc.Markdown(d("""
                    **Click Data**

                    Click on points in the graph.
                """)),
            html.Pre(id='click-data', style=styles['pre']),
        ], className='three columns')
    ])
])

@app.callback(
    Output('hover-data', 'children'),
    [Input('basic-interactions', 'hoverData')])
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    Output('click-data', 'children'),
    [Input('basic-interactions', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)

if __name__ == '__main__':
    app.run_server(debug=True)
