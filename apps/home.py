import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app

layout = html.Div(className="body", children=[
    html.H1('Visualizing Change Data in GitHub Repositories', className='header'),
    dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink('Home', active=True, href='/apps/home')),
            dbc.NavItem(dbc.NavLink('Extractor', href='/apps/extractor')),
            dbc.NavItem(dbc.NavLink('Visualizer', href='/apps/visualizer')),
        ],
        pills=True,
        style={
            'background-color': '#333',
            'margin-bottom': '20px',
            'padding': '10px'
        }
    ),

    html.Div(className="content", children=[
        html.H2('About'),
        html.Div([
            html.P('''
                Many successful software projects endure continuing change as they adapt to new requirements or fix bugs
                 in the system. It is useful for software developers to be aware of the 
                 parts of the system that are most change prone. This can help with cost 
                 and resource estimations and with guiding code refactoring. 
            '''),
            html.P('''
                Existing tools provide visualisations of the number of changes at specific intervals of time during 
                the project lifecycle and these projects have often quantified change by the number of commits to a 
                repository during this time. These tools do not show how the location of these changes, fluctuates 
                over time.  
            '''),
            html.P('''
                The aim of this project is to address this gap in software change visualisation by mining the data found 
                in a version control system and creating visualisations for the files with the greatest change for the 
                entire project and specified intervals. For this project, change will be defined by the additions, 
                deletions and total change to the files. 
            ''')
        ])
    ]),

    html.Footer(className='footer', children=[html.A('GitHub', href='https://github.com/CiaranCarroll1/FYP')]),
])

