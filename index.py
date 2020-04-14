import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from pages import home, extractor, visualiser

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/extractor':
        return extractor.layout
    elif pathname == '/visualiser':
        return visualiser.layout
    else:
        return home.layout


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=True)
