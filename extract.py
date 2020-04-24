import os
from github import Github, GithubException
import pandas as pd

ACCESS_TOKEN = '821f643807b3d0078f309d35531c7e59d577aa43'
g = Github(ACCESS_TOKEN)


def extract(value):
    if os.path.exists('/data/data.h5'):
        reposdf = pd.read_hdf('/data/data.h5', 'repos')
        repositories = reposdf['Name'].tolist()
    else:
        repositories = []

    try:
        repo = g.get_repo(value)
        languages = repo.get_languages()
        lang_exts = get_extensions(languages)
        value = value.replace("/", "_")
        value = value.replace("-", "_")
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
                fname = file.filename
                if fname.endswith(tuple(lang_exts)):
                    dates.append(date)
                    filenames.append(fname)
                    totals.append(file.changes)
                    adds.append(file.additions)
                    dels.append(file.deletions)

        data = {'Date': dates, 'Filename': filenames, 'Total': totals, 'Additions': adds, 'Deletions': dels}
        df = pd.DataFrame(data=data)

        df.to_hdf('/data/data.h5', key=value)

        if value not in repositories:
            repositories.append(value)

        datar = {'Name': repositories}
        dfr = pd.DataFrame(data=datar)

        dfr.to_hdf('/data/data.h5', key='repos')

        rate_limit = g.get_rate_limit()
        rate = rate_limit.core

        return f'You have {rate.remaining}/{rate.limit} API calls remaining. Reset time: {rate.reset}', \
               'Completed: Visit Visualizer to Examine Data.'

    except GithubException as e:
        return f'Status: {e.status} - Data: {e.data}', "Error: Invalid Input Details"


def get_extensions(languages):
    extensions = []
    for x in languages:
        if x == 'Python':
            extensions.append('.py')
        elif x == 'Java':
            extensions.append('.java')
        elif x == 'JavaScript':
            extensions.append('.js')
        elif x == 'C':
            extensions.append('.c')
            extensions.append('.h')
        elif x == 'C++':
            extensions.append('.cpp')
            extensions.append('.h')
        elif x == 'C#':
            extensions.append('.cs')
        elif x == 'Ruby':
            extensions.append('.rb')
        elif x == 'Swift':
            extensions.append('.swift')
        elif x == 'HTML':
            extensions.append('.html')
        elif x == 'CSS':
            extensions.append('.css')
        elif x == 'PHP':
            extensions.append('.php')
        elif x == 'Shell':
            extensions.append('.sh')
        elif x == 'Go':
            extensions.append('.go')
        elif x == 'TypeScript':
            extensions.append('.ts')
        elif x == 'Objective-C':
            extensions.append('.h')
            extensions.append('.m')
        elif x == 'Kotlin':
            extensions.append('.kt')
        elif x == 'R':
            extensions.append('.r')
        elif x == 'Scala':
            extensions.append('.scala')
        elif x == 'Rust':
            extensions.append('.rs')
        elif x == 'Lua':
            extensions.append('.lua')
        elif x == 'Matlab':
            extensions.append('.mat')

    return extensions