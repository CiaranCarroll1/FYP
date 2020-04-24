from celery.result import AsyncResult
from tasks import query

from github import Github, GithubException
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

from app import app

ACCESS_TOKEN = '821f643807b3d0078f309d35531c7e59d577aa43'
g = Github(ACCESS_TOKEN)


""" [Layout] """


layout = html.Div([
    dbc.Nav(
        [
            html.H5('ChangeVisualizer', className='header'),
            dbc.NavItem(dbc.NavLink('Home', href='/home')),
            dbc.NavItem(dbc.NavLink('Extractor', active=True, href='/extractor')),
            dbc.NavItem(dbc.NavLink('Visualizer', href='/visualizer')),
        ],
        pills=True,
        style={
            'background-color': '#333',
            'margin-bottom': '20px',
            'padding': '10px'
        }
    ),

    html.Div(id='task-id', children='none', style={'display': 'none'}),
    html.Div(id='task-status', children='task-status', style={'display': 'none'}),
    dcc.Interval(id='task-interval', interval=250, n_intervals=0),

    dbc.Modal(
        [
            dbc.ModalHeader("How Search Results are Ranked"),
            dbc.ModalBody("""
                Results are sorted by best match, as indicated by a score field which is returned with each result. This is 
                a computed value representing the relevance of an item relative to the other items in the result set. 
                Multiple factors are combined to boost the most relevant item to the top of the result list.
                """),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ml-auto")
            ),
        ],
        id="modal",
    ),

    html.Div(className='container', children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.FormGroup(
                            [
                                html.H4(dbc.Label("Search GitHub Repositories using Keywords")),
                                dbc.Input(placeholder="Enter keywords...", id='left-input-box', type="text"),
                                dbc.FormText("(format : 'keyword, keyword etc.')"),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Button("Submit", color="primary", className="mr-1", id='left-button')),
                                dbc.Col(dbc.Button("Info", color="secondary", className="mr-1", id='open')),
                            ]
                        ),
                        dcc.Loading(id="loading-icon", children=[
                            html.Div(id='left-output-container', children=[
                                html.Div(id='search_api'),
                                html.Div(id='core_api'),
                                html.Br(),
                                html.Div(id='repos-found'),
                                html.Div(id='datatable')
                            ])
                        ], type="default")
                    ]
                ),
                dbc.Col(
                    [
                        dbc.FormGroup(
                            [
                                html.H4(dbc.Label("Enter GitHub Repository to Extract Data")),
                                dbc.Input(placeholder="Enter repository...", id='right-input-box', type="text"),
                                dbc.FormText("(format : 'owner/name')"),
                            ]
                        ),
                        dbc.Button("Submit", color="primary", className="mr-1", id='right-button'),
                        dcc.Loading(id="loading-icon", children=[
                            html.Div(id='right-output-container', children=[
                                html.Div(id='rate_limit'),
                                html.Br(),
                                html.Div(id='extract_result')
                            ])
                        ], type="default")
                    ]
                ),
            ]
        ),
    ]),
])


""" [Callbacks] """


@app.callback([
    Output('search_api', 'children'),
    Output('core_api', 'children'),
    Output('repos-found', 'children'),
    Output('datatable', 'children')
    ],
    [Input('left-button', 'n_clicks')],
    [State('left-input-box', 'value')])
def update_output(n_clicks, value):
    if n_clicks is None or value is None:
        raise dash.exceptions.PreventUpdate
    else:
        keywords = [keyword.strip() for keyword in value.split(',')]
        query = '+'.join(keywords) + '+in:name+in:readme+in:description'
        result = g.search_repositories(query)
        repos = []
        commits = []

        count = 0
        for repo in result:
            url = repo.clone_url
            url = url.replace('https://github.com/', '')
            url = url.replace('.git', '')
            repos.append(url)

            try:
                commits.append(repo.get_commits().totalCount)
            except GithubException:
                commits.append(0)

            count += 1
            if count == 50:
                break

        data = {'Owner/Name': repos, 'Commits': commits}
        df = pd.DataFrame(data=data)

        try:
            totalCount = result.totalCount
        except GithubException:
            totalCount = 0

        rate_limit = g.get_rate_limit()
        rate = rate_limit.search
        ratec = rate_limit.core

        if totalCount > 50:
            found = f'Found {totalCount} repo(s) - Displaying Top 50'
        else:
            found = f'Found {totalCount} repo(s)'

        return f'You have {rate.remaining}/{rate.limit} Search API calls remaining. Reset time: {rate.reset}', \
               f'You have {ratec.remaining}/{ratec.limit} Core API calls remaining. Reset time: {ratec.reset}', \
               found, \
               dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)


# @app.callback([
#     Output('rate_limit', 'children'),
#     Output('extract_result', 'children')
#     ],
#     [Input('right-button', 'n_clicks')],
#     [State('right-input-box', 'value')])
# def update_output(n_clicks, value):
#     if n_clicks is None or value is None:
#         raise dash.exceptions.PreventUpdate
#     else:
#         rl, result = extract_data(value)
#         return rl, result


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output('task-id', 'children'),
    [Input('right-button', 'n_clicks')],
    [State('task-id', 'children'), State('right-input-box', 'value')])
def start_task_callback(n_clicks, task_id, value):
    """This callback is triggered by  clicking the submit button click event.  If the button was
    really pressed (as opposed to being self-triggered when the app is launch) it checks if the
    user input is valid then puts the query on the Celery queue.  Finally it returns the celery
    task ID to the invisible div called 'task-id'.
    """
    if n_clicks is None or value is None:
        return 'none'
    else:
        task = query.apply_async([value])
        return str(task.id)


@app.callback(
    Output('task-interval', 'interval'),
    [Input('task-id', 'children'), Input('task-status', 'children')])
def toggle_interval_speed(task_id, task_status):
    """This callback is triggered by changes in task-id and task-status divs.  It switches the
    page refresh interval to fast (1 sec) if a task is running, or slow (24 hours) if a task is
    pending or complete."""
    if task_id == 'none':
        return 24 * 60 * 60 * 1000
    if task_id != 'none' and (task_status in ['SUCCESS', 'FAILURE']):
        return 24 * 60 * 60 * 1000
    else:
        return 1000


# @app.callback(
#     Output('spinner', 'style'),
#     [Input('task-interval', 'n_intervals'), Input('task-status', 'children')])
# def show_hide_spinner(n_intervals, task_status):
#     if task_status == 'PROGRESS':
#         return None
#     else:
#         return {'display': 'none'}


@app.callback(
    Output('task-status', 'children'),
    [Input('task-interval', 'n_intervals'), Input('task-id', 'children')])
def update_task_status(n_intervals, task_id):
    """This callback is triggered by the Interval clock and task-id .  It checks the task
    status in Celery and returns the status to an invisible div"""
    return str(AsyncResult(task_id).state)


@app.callback([
            Output('rate_limit', 'children'),
            Output('extract_result', 'children')
            ],
              [Input('task-status', 'children')],
              [State('task-id', 'children')])
def get_results(task_status, task_id):
    """This callback is triggered by task-status.  It checks the task status, and if the status
    is 'SUCCESS' it retrieves results, defines the results form and returns it, otherwise it
    returns [] so that nothing is displayed"""
    if task_status == 'SUCCESS':
        # Fetch results from Celery and forget the task
        result = AsyncResult(task_id).result  # fetch results
        forget = AsyncResult(task_id).forget()  # delete from Celery
        return result[0], result[1]


""" [functions] """


# def get_extensions(languages):
#     extensions = []
#     for x in languages:
#         if x == 'Python':
#             extensions.append('.py')
#         elif x == 'Java':
#             extensions.append('.java')
#         elif x == 'JavaScript':
#             extensions.append('.js')
#         elif x == 'C':
#             extensions.append('.c')
#             extensions.append('.h')
#         elif x == 'C++':
#             extensions.append('.cpp')
#             extensions.append('.h')
#         elif x == 'C#':
#             extensions.append('.cs')
#         elif x == 'Ruby':
#             extensions.append('.rb')
#         elif x == 'Swift':
#             extensions.append('.swift')
#         elif x == 'HTML':
#             extensions.append('.html')
#         elif x == 'CSS':
#             extensions.append('.css')
#         elif x == 'PHP':
#             extensions.append('.php')
#         elif x == 'Shell':
#             extensions.append('.sh')
#         elif x == 'Go':
#             extensions.append('.go')
#         elif x == 'TypeScript':
#             extensions.append('.ts')
#         elif x == 'Objective-C':
#             extensions.append('.h')
#             extensions.append('.m')
#         elif x == 'Kotlin':
#             extensions.append('.kt')
#         elif x == 'R':
#             extensions.append('.r')
#         elif x == 'Scala':
#             extensions.append('.scala')
#         elif x == 'Rust':
#             extensions.append('.rs')
#         elif x == 'Lua':
#             extensions.append('.lua')
#         elif x == 'Matlab':
#             extensions.append('.mat')
#
#     return extensions
#
#
# def extract_data(value):
#     if os.path.exists('./data/data.h5'):
#         reposdf = pd.read_hdf('./data/data.h5', 'repos')
#         repositories = reposdf['Name'].tolist()
#     else:
#         repositories = []
#
#     try:
#         repo = g.get_repo(value)
#         languages = repo.get_languages()
#         lang_exts = get_extensions(languages)
#         value = value.replace("/", "_")
#         value = value.replace("-", "_")
#         dates = []
#         filenames = []
#         totals = []
#         adds = []
#         dels = []
#
#         commits = repo.get_commits()
#         for commit in commits:
#             date = commit.commit.author.date.date()
#             date = date.replace(day=1)
#
#             files = commit.files
#
#             for file in files:
#                 fname = file.filename
#                 if fname.endswith(tuple(lang_exts)):
#                     dates.append(date)
#                     filenames.append(fname)
#                     totals.append(file.changes)
#                     adds.append(file.additions)
#                     dels.append(file.deletions)
#
#         data = {'Date': dates, 'Filename': filenames, 'Total': totals, 'Additions': adds, 'Deletions': dels}
#         df = pd.DataFrame(data=data)
#
#         df.to_hdf('./data/data.h5', key=value)
#
#         if value not in repositories:
#             repositories.append(value)
#
#         datar = {'Name': repositories}
#         dfr = pd.DataFrame(data=datar)
#
#         dfr.to_hdf('./data/data.h5', key='repos')
#
#         rate_limit = g.get_rate_limit()
#         rate = rate_limit.core
#
#         return f'You have {rate.remaining}/{rate.limit} API calls remaining. Reset time: {rate.reset}', \
#                'Completed: Visit Visualizer to Examine Data.'
#
#     except GithubException as e:
#         return f'Status: {e.status} - Data: {e.data}', "Error: Invalid Input Details"
