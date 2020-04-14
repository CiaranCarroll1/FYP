# Dropdown rows
# dbc.Row(
#         [
#             dbc.Col(dcc.Dropdown(id='month1', placeholder='Select Month to Compare')),
#             dbc.Col(dcc.Dropdown(id='month2', placeholder='Select Month to Compare')),
#             dbc.Col(dcc.Dropdown(id='month3', placeholder='Select Month to Compare')),
#         ]
#     ),


# Dropdown callbacks
# @app.callback([
#     Output('month1', 'options'),
#     Output('month2', 'options'),
#     Output('month3', 'options'),
# ],
#     [Input('repository_title', 'value')])
# def update_month_dropdowns(repotitle):
#     df = pd.read_csv("./repositories/" + repotitle + ".csv")
#     months = df['Date'].unique()
#     new_months = [x[:-3] for x in months]
#     return [{'label': i, 'value': i} for i in new_months], \
#            [{'label': i, 'value': i} for i in new_months], \
#            [{'label': i, 'value': i} for i in new_months]
#

# @app.callback(
#     Output('filechartmonth1', 'figure'),
#     [Input('repositorytitle', 'value'),
#      Input('month1', 'value')])
# def update_filechart_1(repotitle, month):
#     if month is None:
#         return {'data': []}
#     else:
#         df = pd.read_csv("./repositories/" + repotitle + ".csv")
#         month = month + "-01"
#         df = df.loc[df['Date'] == month]
#         month = month[:-3]
#         df = df.groupby("Filename").sum()
#         df = df.sort_values(by=['Total'], ascending=False)
#         filenames = df.index.tolist()
#         filetotals = df['Total'].tolist()
#         del filenames[10:]
#         del filetotals[10:]
#         return createfilechart(filenames, filetotals, month)
#
# @app.callback(
#     Output('filechartmonth2', 'figure'),
#     [Input('repositorytitle', 'value'),
#      Input('month2', 'value')])
# def update_filechart_1(repotitle, month):
#     if month is None:
#         return {'data': []}
#     else:
#         df = pd.read_csv("./repositories/" + repotitle + ".csv")
#         month = month + "-01"
#         df = df.loc[df['Date'] == month]
#         month = month[:-3]
#         df = df.groupby("Filename").sum()
#         df = df.sort_values(by=['Total'], ascending=False)
#         filenames = df.index.tolist()
#         filetotals = df['Total'].tolist()
#         del filenames[10:]
#         del filetotals[10:]
#         return createfilechart(filenames, filetotals, month)
#
# @app.callback(
#     Output('filechartmonth3', 'figure'),
#     [Input('repositorytitle', 'value'),
#      Input('month3', 'value')])
# def update_filechart_1(repotitle, month):
#     if month is None:
#         return {'data': []}
#     else:
#         df = pd.read_csv("./repositories/" + repotitle + ".csv")
#         month = month + "-01"
#         df = df.loc[df['Date'] == month]
#         month = month[:-3]
#         df = df.groupby("Filename").sum()
#         df = df.sort_values(by=['Total'], ascending=False)
#         filenames = df.index.tolist()
#         filetotals = df['Total'].tolist()
#         del filenames[10:]
#         del filetotals[10:]
#         return createfilechart(filenames, filetotals, month)

# Footer
# html.Div(className='footer', children=[html.A('GitHub', href='https://github.com/CiaranCarroll1/FYP')]),


# @app.callback(
#     Output('left-output-container', 'children'),
#     [Input('left-button', 'n_clicks')],
#     [State('left-input-box', 'value')])
# def update_output(n_clicks, value):
#     if n_clicks is None or value is None:
#         raise dash.exceptions.PreventUpdate
#     else:
#         count = 0
#         keywords = [keyword.strip() for keyword in value.split(',')]
#         query = '+'.join(keywords) + '+in:readme+in:description'
#         result = g.search_repositories(query, 'stars', 'desc')
#         urls = []
#         for repo in result:
#             count = count + 1
#             url = repo.clone_url
#             url = url.replace('https://github.com/', '')
#             url = url.replace('.git', '')
#             urls.append(html.P(url + " - Commits: " + str(repo.get_commits().totalCount)))
#             if count == 20:
#                 break
#         return urls