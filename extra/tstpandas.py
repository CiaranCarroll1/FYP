import pandas as pd

df = pd.read_csv("./gothinkster_realworld.csv")
df['Date'] = pd.to_datetime(df['Date'])
df.index = df['Date']
df.resample('M').sum()

df.head()


dcc.Graph(
        id='linechart',
        figure={
            'data': [
                {
                    'x': dates,
                    'y': values,
                    'type': 'line',
                    'name': 'Total'
                },
                {
                    'x': dates,
                    'y': adds,
                    'type': 'line',
                    'name': 'Additions'
                },
                {
                    'x': dates,
                    'y': dels,
                    'type': 'line',
                    'name': 'Deletions'
                },
            ],
            'layout': {
                'title': 'Change over time',
                'clickmode': 'event+select'
            }
        }
    ),