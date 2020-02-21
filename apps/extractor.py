import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

layout = html.Div([
    html.H2('Visualizing Change Data in GitHub Repositories', className='header'),
    html.Nav(className="navbar", children=[
        html.A('Home', href='/apps/home'),
        html.A('Extractor', href='/apps/extractor'),
        html.A('Visualizer', href='/apps/visualizer')
    ]),
    html.Div(className='footer', children='Footer'),
])


@app.callback(
    Output('app-1-display-value', 'children'),
    [Input('app-1-dropdown', 'value')])
def display_value(value):
    return 'You have selected "{}"'.format(value)
