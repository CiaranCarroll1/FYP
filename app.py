import os
import redis

import dash
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'ChangeVisualizer'
server = app.server
server.secret_key = os.environ.get('secret_key', 'secret')
app.config.suppress_callback_exceptions = True
r = redis.StrictRedis.from_url("redis://h:pccc9ec6523412f670125b1cc08c3b03c064fd186b3f4bc0356e3beefcd31d101@ec2-52-50-246-38.eu-west-1.compute.amazonaws.com:21709")
