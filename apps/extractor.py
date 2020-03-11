from github import Github
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from app import app

ACCESS_TOKEN = '821f643807b3d0078f309d35531c7e59d577aa43'
g = Github(ACCESS_TOKEN)

layout = html.Div([
    html.H1('Visualizing Change Data in GitHub Repositories', className='header'),
    dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink('Home', href='/apps/home')),
            dbc.NavItem(dbc.NavLink('Extractor', active=True, href='/apps/extractor')),
            dbc.NavItem(dbc.NavLink('Visualizer', href='/apps/visualizer')),
        ],
        pills=True,
        style={
            'background-color': '#333',
            'margin-bottom': '20px',
            'padding': '10px'
        }
    ),

    html.Div(className='container', children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Search Repositories using Keywords"),
                        html.H6("(format : 'keyword, keyword etc.')"),
                        html.Div(dcc.Input(id='left-input-box', type='text')),
                        html.Button('Submit', id='left-button'),
                        dcc.Loading(id="loading-icon", children=[
                            html.Div(id='left-output-container')
                        ], type="default")
                    ]
                ),
                dbc.Col(
                    [
                        html.H4("Enter Repository to Extract Data"),
                        html.H6("(format : 'owner/name')"),
                        html.Div(dcc.Input(id='right-input-box', type='text')),
                        html.Button('Submit', id='right-button'),
                        dcc.Loading(id="loading-icon", children=[
                            html.Div(id='right-output-container')
                        ], type="default")
                    ]
                ),
            ]
        ),
    ]),

    html.Div(className='footer', children=[html.A('GitHub', href='https://github.com/CiaranCarroll1/FYP')]),
])

def extract_data(value):
    reposdf = pd.read_csv("./repos.csv")
    repositories = reposdf['Name'].tolist()
    repo = g.get_repo(value)
    value = value.replace("/", "_")
    dates = []
    filenames = []
    totals = []
    adds = []
    dels = []

    commits = repo.get_commits()
    for commit in commits:
        date = commit.commit.author.date.date()
        date = date.replace(day=1)

        files = commit.files

        for file in files:
            dates.append(date)
            fname = file.filename
            if '/' in fname:
                fsplit = fname.split('/')
                fname = fsplit[len(fsplit) - 1]
            filenames.append(fname)
            totals.append(file.changes)
            adds.append(file.additions)
            dels.append(file.deletions)

    data = {'Date': dates, 'Filename': filenames, 'Total': totals, 'Additions': adds, 'Deletions': dels}
    df = pd.DataFrame(data=data)

    df.to_csv('./repositories/' + value + '.csv', index=False)

    if value not in repositories:
        repositories.append(value)
    datar = {'Name': repositories}
    dfr = pd.DataFrame(data=datar)

    dfr.to_csv('./repos.csv', index=False)

@app.callback(
    Output('left-output-container', 'children'),
    [Input('left-button', 'n_clicks')],
    [State('left-input-box', 'value')])
def update_output(n_clicks, value):
    if n_clicks is None or value is None:
        raise dash.exceptions.PreventUpdate
    else:
        count = 0
        query = '+'.join(value) + '+in:readme+in:description'
        result = g.search_repositories(query, 'stars', 'desc')
        urls = []
        for repo in result:
            count = count + 1
            urls.append(html.P(repo.clone_url))
            if count == 20:
                break
        return urls

@app.callback(
    Output('right-output-container', 'children'),
    [Input('right-button', 'n_clicks')],
    [State('right-input-box', 'value')])
def update_output(n_clicks, value):
    if n_clicks is None or value is None:
        raise dash.exceptions.PreventUpdate
    else:
        extract_data(value)
        return "Completed: Visit Visualizer to Examine Data"


