import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app


""" [Layout] """


layout = html.Div(className="body", children=[
    dbc.Nav(
        [
            html.H5('ChangeVisualizer', className='header'),
            dbc.NavItem(dbc.NavLink('Home', active=True, href='/')),
            dbc.NavItem(dbc.NavLink('Extractor', href='/extractor')),
            dbc.NavItem(dbc.NavLink('Visualizer', href='/visualizer')),
        ],
        pills=True,
        style={
            'background-color': '#333',
            'margin-bottom': '20px',
            'padding': '10px'
        }
    ),

    html.Div(className="content", children=[
        html.Div(className='about', children=[
            html.H1('Visualizing Change Data from GitHub Repositories'),
            html.Div([
                html.P('''
                    Many successful software projects endure continuing change as they adapt to new requirements or 
                    fix bugs in the system. It is useful for software developers to be aware of the parts of the system 
                    that are most change prone. This can help with cost and resource estimations and with guiding code 
                    refactoring. 
                    There are numerous existing tools which focus on the visualisation of software change. However, 
                    these tools do not provide views to explore how the location of these changes, fluctuates over 
                    time. The aim of this project is to address this gap in software change visualisation by mining 
                    change data from GitHub and creating graphics to display the data.
                    The application is split into two major parts, the Extractor and the Visualizer which will be 
                    discussed further below. Each of these are held on their own separate page which can be accessed 
                    using the navigation bar above.
                '''),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H3('Extractor'),
                    html.Div([
                        '''
                            The Extractor page is split into two sides. On the left, you will find a search feature which returns
                            the names and commit count of repositories which hold the keywords submitted. The 
                            application will search for these keywords in the name, description and README file of all public 
                            GitHub repositories. Results are sorted by best match, as indicated by a score field which is 
                            returned with each result. If there is a large quantity of results, the first fifty best matches will be displayed.
                            On the right side, a unique owner/name repository identification string can be entered and the 
                            application will mine and store the relevant change data which can then be visualized on the 
                            Visualizer page.
                        '''
                    ]),
                ]),
                dbc.Col([
                    html.H3('Visualizer'),
                    html.Div([
                        html.P('''
                            The Visualizer provides interactive visualizations for the user to explore the data held for
                            different repositories. You can decide which repository to explore and whether to do so on 
                            file or folder level. Once selected a table holding a count for folders, files and LOC 
                            changes for the repo will be displayed along with a figure for a proposed Pareto Principle 
                            hypothesis. There are also multiple interactive graphs for exploring the location of change 
                            over time.
                        '''),
                    ]),
                ])
            ])
        ])
    ]),
])

