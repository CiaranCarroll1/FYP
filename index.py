import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from pages import home, extractor, visualizer


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/extractor':
        return extractor.layout
    elif pathname == '/visualizer':
        return visualizer.layout
    else:
        return home.layout


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
