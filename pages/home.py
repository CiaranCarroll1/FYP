import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app


""" [Layout] """


layout = html.Div(className="body", children=[
    dbc.Nav(
        [
            html.H5('ChangeVisualizer', className='header'),
            dbc.NavItem(dbc.NavLink('Home', active=True, href='/home')),
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
            html.H1('Visualizing Change Data in GitHub Repositories'),
            html.Div([
                html.P('''
                    Many successful software projects endure continuing change as they adapt to new requirements or 
                    fix bugs in the system. It is useful for software developers to be aware of the parts of the system 
                    that are most change prone. This can help with cost and resource estimations and with guiding code 
                    refactoring. 
                '''),
                html.P('''
                    There are numerous existing tools which focus on the visualisation of software change. However, 
                    these tools do not provide views to explore how the location of these changes, fluctuates over 
                    time. The aim of this project is to address this gap in software change visualisation by mining 
                    change data from version control systems (VCS) and creating graphics to display the data.
                '''),
            ])
        ])
    ]),
])

